from __future__ import annotations

import queue
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from gui.config import (
    DEFAULT_CLOSED_LOOP_OUTPUT_BASE,
    DEFAULT_CLOSED_LOOP_CARRIER,
    DEFAULT_IMAGE_DIR,
    DEFAULT_OUTPUT_BASE,
    DEFAULT_PAYLOADS_TEXT,
    DEFAULT_SEEDS_TEXT,
    PROJECT_ROOT,
    VALID_MODES,
    GuiClosedLoopConfig,
    GuiExperimentConfig,
    build_timestamped_output_dir,
    parse_payloads,
    parse_seeds,
)
from gui.labels import COLUMN_LABELS, TEXT, format_mode_label, format_progress_message
from gui.theme import PALETTE, apply_theme, get_window_geometry
from gui.workers import PauseController, WorkerEvent, start_closed_loop_worker, start_experiment_worker


LOG_WINDOW_SIZE = "900x520"
RESULTS_VISIBLE_ROWS = 8


class CnnpGuiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.events: queue.Queue[WorkerEvent] = queue.Queue()
        self.worker = None
        self.pause_controller: PauseController | None = None
        self.current_worker_kind = ""
        self.active_view = ""
        self.active_page: ttk.Frame | None = None
        self.log_messages: list[str] = []
        self.log_window: tk.Toplevel | None = None
        self.log_window_text: tk.Text | None = None
        self.root.title(TEXT["app_title"])
        apply_theme(self.root)
        self.root.geometry(get_window_geometry())
        self._init_vars()
        self._build_layout()

    def _init_vars(self) -> None:
        self.image_dir_var = tk.StringVar(value=str(DEFAULT_IMAGE_DIR))
        self.model_path_var = tk.StringVar(value=str(PROJECT_ROOT / "model_parameter" / "model_state.pth"))
        self.output_base_var = tk.StringVar(value=str(DEFAULT_OUTPUT_BASE))
        self.closed_loop_carrier_var = tk.StringVar(value=str(DEFAULT_CLOSED_LOOP_CARRIER))
        self.closed_loop_output_base_var = tk.StringVar(value=str(DEFAULT_CLOSED_LOOP_OUTPUT_BASE))
        self.secret_text_var = tk.StringVar(value="测试")
        self.payloads_var = tk.StringVar(value=DEFAULT_PAYLOADS_TEXT)
        self.seed_var = tk.StringVar(value=DEFAULT_SEEDS_TEXT)
        self.mode_vars = {mode: tk.BooleanVar(value=True) for mode in VALID_MODES}
        self.experiment_progress_value_var = tk.DoubleVar(value=0.0)
        self.experiment_progress_text_var = tk.StringVar(value=TEXT["progress_idle"])
        self.closed_loop_progress_value_var = tk.DoubleVar(value=0.0)
        self.closed_loop_progress_text_var = tk.StringVar(value=TEXT["progress_idle"])
        self.closed_loop_result_var = tk.StringVar(value=TEXT["closed_loop_ready"])
        self.closed_loop_verify_var = tk.StringVar(value="-")
        self.closed_loop_output_var = tk.StringVar(value="-")

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=(18, 16), style="App.TFrame")
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        header = ttk.Frame(main, style="App.TFrame")
        header.grid(row=0, column=0, sticky=tk.EW)
        self._build_header(header)
        self.workspace = ttk.Frame(main, padding=12, style="Surface.TFrame")
        self.workspace.grid(row=1, column=0, sticky=tk.NSEW, pady=(12, 0))

        self._build_view_switcher(self.workspace)
        self._build_fixed_experiment_actions(self.workspace)
        self._build_fixed_closed_loop_actions(self.workspace)
        self.page_container = ttk.Frame(self.workspace, style="Surface.TFrame")
        self.page_container.pack(fill=tk.BOTH, expand=True)
        self.experiment_page = ttk.Frame(self.page_container, style="Surface.TFrame")
        self.closed_loop_page = ttk.Frame(self.page_container, style="Surface.TFrame")

        self._build_experiment_area(self.experiment_page)
        self._build_closed_loop_area(self.closed_loop_page)
        self._show_view("experiment")
        self._build_log_footer(main, row=2)

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="Header.TFrame")
        header.pack(fill=tk.X)
        ttk.Label(header, text=TEXT["app_title"], style="HeaderTitle.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="CNN 预测驱动的可逆数据隐藏实验、嵌入闭环验证与结果导出",
            style="HeaderSub.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

    def _build_view_switcher(self, parent: ttk.Frame) -> None:
        switcher = ttk.Frame(parent, style="Surface.TFrame")
        switcher.pack(fill=tk.X, pady=(0, 12))
        self.experiment_switch = ttk.Button(
            switcher,
            text=TEXT["experiment_tab"],
            command=lambda: self._show_view("experiment"),
            style="ExperimentSwitchActive.TButton",
        )
        self.closed_loop_switch = ttk.Button(
            switcher,
            text=TEXT["closed_loop_tab"],
            command=lambda: self._show_view("closed_loop"),
            style="ClosedLoopSwitch.TButton",
        )
        self.experiment_switch.grid(row=0, column=0, sticky=tk.EW, padx=(0, 6))
        self.closed_loop_switch.grid(row=0, column=1, sticky=tk.EW, padx=(6, 0))
        switcher.columnconfigure(0, weight=1, uniform="view_switch")
        switcher.columnconfigure(1, weight=1, uniform="view_switch")

    def _show_view(self, view_name: str) -> None:
        pages = {
            "experiment": self.experiment_page,
            "closed_loop": self.closed_loop_page,
        }
        page = pages[view_name]
        for candidate in pages.values():
            candidate.pack_forget()
        page.pack(fill=tk.BOTH, expand=True)
        self.active_view = view_name
        self.active_page = page
        self.experiment_switch.configure(
            style="ExperimentSwitchActive.TButton" if view_name == "experiment" else "ExperimentSwitch.TButton"
        )
        self.closed_loop_switch.configure(
            style="ClosedLoopSwitchActive.TButton" if view_name == "closed_loop" else "ClosedLoopSwitch.TButton"
        )
        if view_name == "experiment":
            if not self.experiment_action_bar.winfo_manager():
                self.experiment_action_bar.pack(fill=tk.X, pady=(0, 10), before=self.page_container)
            self.closed_loop_action_bar.pack_forget()
        else:
            self.experiment_action_bar.pack_forget()
            if not self.closed_loop_action_bar.winfo_manager():
                self.closed_loop_action_bar.pack(fill=tk.X, pady=(0, 10), before=self.page_container)

    def _build_experiment_area(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        ttk.Label(parent, text=TEXT["experiment_tab"], style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )
        self._build_progress(parent, "experiment", layout="grid", row=1)
        self._build_inputs(parent, layout="grid", row=2)
        self._build_results(parent, layout="grid", row=3)

    def _build_closed_loop_area(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        ttk.Label(parent, text=TEXT["closed_loop_tab"], style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )
        self._build_progress(parent, "closed_loop", layout="grid", row=1)
        panel = ttk.LabelFrame(parent, text=TEXT["closed_loop_panel"], padding=12, style="Card.TLabelframe")
        panel.grid(row=2, column=0, sticky=tk.EW)
        self._path_row(panel, 0, TEXT["carrier_image"], self.closed_loop_carrier_var, self._choose_closed_loop_carrier)
        self._path_row(panel, 1, TEXT["model_file"], self.model_path_var, self._choose_model_file)
        self._path_row(panel, 2, TEXT["output_folder"], self.closed_loop_output_base_var, self._choose_closed_loop_output_base)
        ttk.Label(panel, text=TEXT["secret_text"]).grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(panel, textvariable=self.secret_text_var).grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=6)
        panel.columnconfigure(1, weight=1)
        panel.columnconfigure(3, weight=1)
        self._build_closed_loop_result(parent)

    def _build_closed_loop_result(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(parent, text=TEXT["closed_loop_result_panel"], padding=12, style="Card.TLabelframe")
        panel.grid(row=3, column=0, sticky=tk.NSEW, pady=(8, 0))
        content = ttk.Frame(panel, style="Surface.TFrame")
        content.pack(fill=tk.BOTH, expand=True)
        ttk.Label(content, textvariable=self.closed_loop_result_var, style="Status.TLabel").pack(fill=tk.X)
        grid = ttk.Frame(content, style="Surface.TFrame")
        grid.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(grid, text="验证", style="Muted.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(grid, textvariable=self.closed_loop_verify_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(grid, text=TEXT["output_files"], style="Muted.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(6, 0))
        ttk.Label(grid, textvariable=self.closed_loop_output_var, wraplength=900).grid(row=1, column=1, sticky=tk.W, pady=(6, 0))
        grid.columnconfigure(1, weight=1)

    def _build_inputs(self, parent: ttk.Frame, layout: str = "pack", row: int | None = None) -> None:
        panel = ttk.LabelFrame(parent, text=TEXT["settings_panel"], padding=12, style="Card.TLabelframe")
        if layout == "grid":
            panel.grid(row=row, column=0, sticky=tk.EW)
        else:
            panel.pack(fill=tk.X)
        self._path_row(panel, 0, TEXT["image_folder"], self.image_dir_var, self._choose_image_dir)
        self._path_row(panel, 1, TEXT["model_file"], self.model_path_var, self._choose_model_file)
        self._path_row(panel, 2, TEXT["output_folder"], self.output_base_var, self._choose_output_base)
        ttk.Label(panel, text=TEXT["payloads"]).grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(panel, textvariable=self.payloads_var).grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=6)
        ttk.Label(panel, text=TEXT["seed"]).grid(row=4, column=0, sticky=tk.W, pady=4)
        ttk.Entry(panel, textvariable=self.seed_var).grid(row=4, column=1, columnspan=3, sticky=tk.EW, padx=6)
        mode_frame = ttk.Frame(panel)
        mode_frame.grid(row=5, column=1, columnspan=3, sticky=tk.W, pady=4)
        ttk.Label(panel, text=TEXT["modes"]).grid(row=5, column=0, sticky=tk.W, pady=4)
        for mode in VALID_MODES:
            ttk.Checkbutton(mode_frame, text=format_mode_label(mode), variable=self.mode_vars[mode]).pack(side=tk.LEFT, padx=(0, 12))
        panel.columnconfigure(1, weight=1)

    def _path_row(self, parent, row, label, variable, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, columnspan=2, sticky=tk.EW, padx=6)
        ttk.Button(parent, text=TEXT["browse"], command=command, style="Browse.TButton").grid(row=row, column=3, sticky=tk.EW)

    def _build_fixed_experiment_actions(self, parent: ttk.Frame) -> None:
        self.experiment_action_bar = ttk.Frame(parent, style="Surface.TFrame")
        self.experiment_action_bar.pack(fill=tk.X, pady=(0, 10))
        self.run_button = ttk.Button(
            self.experiment_action_bar,
            text=TEXT["run_button"],
            command=self._start_experiment,
            style="Primary.TButton",
        )
        self.run_button.pack(side=tk.LEFT)
        self.clear_log_button = ttk.Button(
            self.experiment_action_bar,
            text=TEXT["clear_log"],
            command=self._clear_log,
            style="Secondary.TButton",
        )
        self.clear_log_button.pack(side=tk.LEFT, padx=8)

    def _build_fixed_closed_loop_actions(self, parent: ttk.Frame) -> None:
        self.closed_loop_action_bar = ttk.Frame(parent, style="Surface.TFrame")
        self.closed_loop_button = ttk.Button(
            self.closed_loop_action_bar,
            text=TEXT["closed_loop_run_button"],
            command=self._start_closed_loop,
            style="Primary.TButton",
        )
        self.closed_loop_button.pack(side=tk.LEFT)
        self.closed_loop_action_bar.pack_forget()

    def _build_actions(self, parent: ttk.Frame, layout: str = "pack", row: int | None = None) -> None:
        bar = ttk.Frame(parent)
        if layout == "grid":
            bar.grid(row=row, column=0, sticky=tk.EW, pady=(8, 8))
        else:
            bar.pack(fill=tk.X, pady=(10, 8))
        self.run_button = ttk.Button(bar, text=TEXT["run_button"], command=self._start_experiment, style="Primary.TButton")
        self.run_button.pack(side=tk.LEFT)
        ttk.Button(bar, text=TEXT["clear_log"], command=self._clear_log, style="Secondary.TButton").pack(side=tk.LEFT, padx=8)

    def _build_progress(self, parent: ttk.Frame, kind: str, layout: str = "pack", row: int | None = None) -> None:
        panel = ttk.LabelFrame(parent, text=TEXT["progress_panel"], padding=10, style="Card.TLabelframe")
        if layout == "grid":
            panel.grid(row=row, column=0, sticky=tk.EW, pady=(0, 12))
        else:
            panel.pack(fill=tk.X, pady=(0, 12))
        value_var, text_var = self._progress_vars(kind)
        bar = ttk.Frame(panel, style="Surface.TFrame")
        bar.pack(fill=tk.X)
        ttk.Progressbar(bar, maximum=100, variable=value_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        pause_button = ttk.Button(
            bar,
            text=TEXT["pause_button"],
            command=self._toggle_pause,
            style="Secondary.TButton",
        )
        pause_button.pack(side=tk.LEFT, padx=(8, 0))
        pause_button.configure(state=tk.DISABLED)
        ttk.Label(panel, textvariable=text_var).pack(anchor=tk.W, pady=(4, 0))
        if kind == "experiment":
            self.experiment_progress_panel = panel
            self.experiment_pause_button = pause_button
        else:
            self.closed_loop_progress_panel = panel
            self.closed_loop_pause_button = pause_button

    def _build_results(self, parent: ttk.Frame, layout: str = "pack", row: int | None = None) -> None:
        panel = ttk.LabelFrame(parent, text=TEXT["results_panel"], padding=10, style="Card.TLabelframe")
        if layout == "grid":
            panel.grid(row=row, column=0, sticky=tk.NSEW)
        else:
            panel.pack(fill=tk.BOTH, expand=True)
        columns = ("mode", "payload", "average_psnr", "average_ssim", "average_elapsed_seconds", "image_count")
        table = ttk.Frame(panel, style="Surface.TFrame")
        table.pack(fill=tk.BOTH, expand=True)
        self.results_tree = ttk.Treeview(table, columns=columns, show="headings", height=RESULTS_VISIBLE_ROWS)
        for column in columns:
            self.results_tree.heading(column, text=COLUMN_LABELS[column])
            self.results_tree.column(column, width=145, anchor=tk.CENTER)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_scrollbar = ttk.Scrollbar(table, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=self.results_scrollbar.set)

    def _build_log_footer(self, parent: ttk.Frame, row: int) -> None:
        self.log_footer = ttk.Frame(parent, style="App.TFrame")
        self.log_footer.grid(row=row, column=0, sticky=tk.EW, pady=(10, 0))
        self.view_log_button = ttk.Button(
            self.log_footer,
            text=TEXT.get("view_log", "查看运行日志"),
            command=self._show_log_window,
            style="Secondary.TButton",
        )
        self.view_log_button.pack(side=tk.RIGHT)

    def _choose_image_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.image_dir_var.get())
        if path:
            self.image_dir_var.set(path)

    def _choose_model_file(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=str(PROJECT_ROOT),
            filetypes=(("PyTorch 模型", "*.pth"), ("所有文件", "*.*")),
        )
        if path:
            self.model_path_var.set(path)

    def _choose_output_base(self) -> None:
        path = filedialog.askdirectory(initialdir=self.output_base_var.get())
        if path:
            self.output_base_var.set(path)

    def _choose_closed_loop_carrier(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=str(DEFAULT_IMAGE_DIR),
            filetypes=(("图像文件", "*.bmp *.png *.jpg *.jpeg *.tif *.tiff"), ("所有文件", "*.*")),
        )
        if path:
            self.closed_loop_carrier_var.set(path)

    def _choose_closed_loop_output_base(self) -> None:
        path = filedialog.askdirectory(initialdir=self.closed_loop_output_base_var.get())
        if path:
            self.closed_loop_output_base_var.set(path)

    def _start_experiment(self) -> None:
        try:
            config = self._collect_config()
        except ValueError as exc:
            messagebox.showerror(TEXT["invalid_settings_title"], str(exc))
            return
        self.pause_controller = PauseController()
        self.current_worker_kind = "experiment"
        self._set_running(True)
        self._clear_results()
        self._set_progress("experiment", 0, TEXT["progress_queued"])
        self._append_log(TEXT["progress_queued"])
        self.worker = start_experiment_worker(config, self.events, self.pause_controller)
        self.root.after(200, self._poll_events)

    def _start_closed_loop(self) -> None:
        try:
            config = self._collect_closed_loop_config()
        except ValueError as exc:
            messagebox.showerror(TEXT["invalid_settings_title"], str(exc))
            return
        self.pause_controller = PauseController()
        self.current_worker_kind = "closed_loop"
        self._set_running(True)
        self._set_progress("closed_loop", 0, TEXT["closed_loop_queued"])
        self._reset_closed_loop_result()
        self._append_log(TEXT["closed_loop_queued"])
        self.worker = start_closed_loop_worker(config, self.events, self.pause_controller)
        self.root.after(200, self._poll_events)

    def _collect_config(self) -> GuiExperimentConfig:
        modes = tuple(mode for mode in VALID_MODES if self.mode_vars[mode].get())
        if not modes:
            raise ValueError("请至少选择一种嵌入方式")
        output_dir = build_timestamped_output_dir(Path(self.output_base_var.get()))
        return GuiExperimentConfig(
            image_dir=Path(self.image_dir_var.get()),
            model_path=Path(self.model_path_var.get()),
            modes=modes,
            payloads=parse_payloads(self.payloads_var.get()),
            seeds=parse_seeds(self.seed_var.get()),
            output_dir=output_dir,
        )

    def _collect_closed_loop_config(self) -> GuiClosedLoopConfig:
        secret_text = self.secret_text_var.get()
        if not secret_text:
            raise ValueError("请输入秘密信息")
        output_dir = build_timestamped_output_dir(Path(self.closed_loop_output_base_var.get()))
        return GuiClosedLoopConfig(
            carrier_path=Path(self.closed_loop_carrier_var.get()),
            model_path=Path(self.model_path_var.get()),
            secret_text=secret_text,
            output_dir=output_dir,
        )

    def _parse_seed(self) -> int:
        try:
            seed = int(self.seed_var.get())
        except ValueError as exc:
            raise ValueError("随机种子必须是整数") from exc
        if seed < 0:
            raise ValueError("随机种子必须大于或等于 0")
        return seed

    def _poll_events(self) -> None:
        while not self.events.empty():
            event = self.events.get()
            if event.kind == "log":
                self._append_log(event.message)
            elif event.kind == "progress":
                self._handle_progress(event)
            elif event.kind == "done":
                self._handle_done(event)
            elif event.kind == "error":
                self._handle_error(event)
        if self.worker is not None:
            self.root.after(200, self._poll_events)

    def _handle_done(self, event: WorkerEvent) -> None:
        self._append_log(event.message)
        payload = event.payload or {}
        if "verify_result" in payload:
            self._handle_closed_loop_done(payload)
            return
        for row in payload.get("summary_rows", []):
            values = [self._format_result_value(column, row) for column in self.results_tree["columns"]]
            self.results_tree.insert("", tk.END, values=values)
        self._set_progress("experiment", 100, "性能评估完成")
        self._append_log("CSV 文件和日志已写入输出目录。")
        self._set_running(False)
        self.worker = None
        self.current_worker_kind = ""

    def _handle_closed_loop_done(self, payload: dict[str, object]) -> None:
        verify_result = payload.get("verify_result", {})
        extract_result = payload.get("extract_result", {})
        paths = payload.get("paths", {})
        self._set_progress("closed_loop", 100, TEXT["closed_loop_done_title"])
        self.closed_loop_result_var.set(f"提取文本：{extract_result.get('secret_text', '')}")
        self.closed_loop_verify_var.set(
            f"{TEXT['message_match']}={verify_result.get('message_match')}，"
            f"{TEXT['image_match']}={verify_result.get('image_match')}，"
            f"bit错误={verify_result.get('bit_error_count')}，"
            f"像素错误={verify_result.get('pixel_error_count')}"
        )
        self._append_log(f"提取文本：{extract_result.get('secret_text', '')}")
        self._append_log(
            "验证结果："
            f"消息一致={verify_result.get('message_match')}，"
            f"图像一致={verify_result.get('image_match')}，"
            f"bit错误={verify_result.get('bit_error_count')}，"
            f"像素错误={verify_result.get('pixel_error_count')}"
        )
        if paths:
            output_items = [
                f"含密图：{paths.get('watermarked_path')}",
                f"恢复图：{paths.get('recovered_path')}",
                f"提取文本：{paths.get('text_output_path')}",
                f"验证摘要：{paths.get('summary_path')}",
                f"闭环报告：{paths.get('report_path')}",
            ]
            self.closed_loop_output_var.set("；".join(item for item in output_items if not item.endswith("None")))
            self._append_log(f"含密图：{paths.get('watermarked_path')}")
            self._append_log(f"恢复图：{paths.get('recovered_path')}")
            self._append_log(f"提取文本文件：{paths.get('text_output_path')}")
            self._append_log(f"验证摘要：{paths.get('summary_path')}")
            self._append_log(f"闭环报告：{paths.get('report_path')}")
        self._set_running(False)
        self.worker = None
        self.current_worker_kind = ""

    def _reset_closed_loop_result(self) -> None:
        self.closed_loop_result_var.set("正在运行闭环，请等待 MATLAB 引擎和模型处理完成")
        self.closed_loop_verify_var.set("-")
        self.closed_loop_output_var.set("-")

    def _handle_error(self, event: WorkerEvent) -> None:
        progress_kind = self._current_progress_kind()
        self._set_progress(progress_kind, self._get_progress_value(progress_kind), TEXT["progress_failed"])
        self._append_log("错误：" + event.message)
        if event.payload:
            self._append_log(event.payload)
        self._set_running(False)
        self.worker = None
        title_key = "closed_loop_failed_title" if self.current_worker_kind == "closed_loop" else "experiment_failed_title"
        self.current_worker_kind = ""
        messagebox.showerror(TEXT[title_key], event.message)

    def _handle_progress(self, event: WorkerEvent) -> None:
        payload = event.payload or {}
        current = int(payload.get("current", 0) or 0)
        total = int(payload.get("total", 0) or 0)
        percent = 0 if total == 0 else current * 100 / total
        if payload.get("stage") == "complete":
            percent = 100
        message = format_progress_message(payload)
        if message:
            self._append_log(message)
            self._set_progress(self._current_progress_kind(), percent, message)

    def _format_result_value(self, column: str, row: dict[str, object]) -> object:
        value = row.get(column, "")
        if column == "mode":
            return format_mode_label(str(value))
        return value

    def _current_progress_kind(self) -> str:
        if self.current_worker_kind in {"experiment", "closed_loop"}:
            return self.current_worker_kind
        return "closed_loop" if self.active_view == "closed_loop" else "experiment"

    def _progress_vars(self, kind: str) -> tuple[tk.DoubleVar, tk.StringVar]:
        if kind == "closed_loop":
            return self.closed_loop_progress_value_var, self.closed_loop_progress_text_var
        return self.experiment_progress_value_var, self.experiment_progress_text_var

    def _get_progress_value(self, kind: str) -> float:
        value_var, _ = self._progress_vars(kind)
        return float(value_var.get())

    def _set_progress(self, kind: str, value: float, text: str) -> None:
        value_var, text_var = self._progress_vars(kind)
        value_var.set(value)
        text_var.set(text)

    def _show_log_window(self) -> None:
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_window.lift()
            self.log_window.focus_force()
            return
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title(TEXT["log_panel"])
        self.log_window.geometry(LOG_WINDOW_SIZE)
        self.log_window.configure(bg=PALETTE["app_bg"])
        self.log_window.protocol("WM_DELETE_WINDOW", self._close_log_window)
        frame = ttk.Frame(self.log_window, padding=12, style="App.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)
        self.log_window_text = tk.Text(frame, wrap=tk.WORD)
        self.log_window_text.pack(fill=tk.BOTH, expand=True)
        self.log_window_text.configure(
            bg=PALETTE["log_bg"],
            fg=PALETTE["log_text"],
            insertbackground=PALETTE["log_text"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=8,
        )
        if self.log_messages:
            self.log_window_text.insert(tk.END, "\n".join(self.log_messages) + "\n")
            self.log_window_text.see(tk.END)

    def _close_log_window(self) -> None:
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_window.destroy()
        self.log_window = None
        self.log_window_text = None

    def _append_log(self, message: str) -> None:
        self.log_messages.append(message)
        if self.log_window_text is not None and self.log_window_text.winfo_exists():
            self.log_window_text.insert(tk.END, message + "\n")
            self.log_window_text.see(tk.END)

    def _clear_log(self) -> None:
        self.log_messages.clear()
        if self.log_window_text is not None and self.log_window_text.winfo_exists():
            self.log_window_text.delete("1.0", tk.END)

    def _clear_results(self) -> None:
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

    def _toggle_pause(self) -> None:
        if self.pause_controller is None:
            return
        progress_kind = self._current_progress_kind()
        pause_button = self._pause_button(progress_kind)
        if self.pause_controller.is_paused:
            self.pause_controller.resume()
            pause_button.configure(text=TEXT["pause_button"])
            self._set_progress(progress_kind, self._get_progress_value(progress_kind), TEXT["progress_resumed"])
            self._append_log(TEXT["progress_resumed"])
        else:
            self.pause_controller.pause()
            pause_button.configure(text=TEXT["resume_button"])
            self._set_progress(progress_kind, self._get_progress_value(progress_kind), TEXT["progress_paused"])
            self._append_log(TEXT["progress_paused"])

    def _pause_button(self, kind: str) -> ttk.Button:
        return self.closed_loop_pause_button if kind == "closed_loop" else self.experiment_pause_button

    def _set_running(self, is_running: bool) -> None:
        self.run_button.configure(state=tk.DISABLED if is_running else tk.NORMAL)
        self.closed_loop_button.configure(state=tk.DISABLED if is_running else tk.NORMAL)
        for kind in ("experiment", "closed_loop"):
            button = self._pause_button(kind)
            state = tk.NORMAL if is_running and self.current_worker_kind == kind else tk.DISABLED
            button.configure(state=state, text=TEXT["pause_button"])
        if not is_running:
            if self.pause_controller is not None:
                self.pause_controller.resume()
            self.pause_controller = None


def main() -> None:
    root = tk.Tk()
    CnnpGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
