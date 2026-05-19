from __future__ import annotations

from tkinter import font, ttk


PALETTE = {
    "app_bg": "#f6f8fb",
    "surface": "#ffffff",
    "surface_alt": "#eef2f7",
    "border": "#d8e0ea",
    "text": "#172033",
    "muted": "#64748b",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "success": "#0f766e",
    "closed_loop": "#0f766e",
    "closed_loop_hover": "#0b5f58",
    "log_bg": "#0f172a",
    "log_text": "#dbeafe",
}


def get_window_geometry() -> str:
    return "1240x860"


def apply_theme(root) -> None:
    root.configure(bg=PALETTE["app_bg"])
    root.minsize(1120, 820)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Microsoft YaHei UI", size=10)
    text_font = font.nametofont("TkTextFont")
    text_font.configure(family="Microsoft YaHei UI", size=10)

    style.configure(".", font=default_font)
    style.configure("TFrame", background=PALETTE["surface"])
    style.configure("App.TFrame", background=PALETTE["app_bg"])
    style.configure("Surface.TFrame", background=PALETTE["surface"])
    style.configure("Header.TFrame", background=PALETTE["app_bg"])
    style.configure("TLabel", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("TCheckbutton", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("TLabelframe", background=PALETTE["surface"], bordercolor=PALETTE["border"])
    style.configure("TLabelframe.Label", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("HeaderTitle.TLabel", background=PALETTE["app_bg"], foreground=PALETTE["text"], font=("Microsoft YaHei UI", 17, "bold"))
    style.configure("HeaderSub.TLabel", background=PALETTE["app_bg"], foreground=PALETTE["muted"], font=("Microsoft YaHei UI", 10))
    style.configure("SectionTitle.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"], font=("Microsoft YaHei UI", 12, "bold"))
    style.configure("Muted.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"])
    style.configure("Status.TLabel", background=PALETTE["surface_alt"], foreground=PALETTE["text"], padding=(10, 6))

    style.configure("Card.TLabelframe", background=PALETTE["surface"], bordercolor=PALETTE["border"], relief="solid")
    style.configure("Card.TLabelframe.Label", background=PALETTE["surface"], foreground=PALETTE["text"], font=("Microsoft YaHei UI", 10, "bold"))

    style.configure("Primary.TButton", padding=(18, 8), foreground="#ffffff", background=PALETTE["primary"])
    style.map("Primary.TButton", background=[("active", PALETTE["primary_hover"]), ("disabled", PALETTE["border"])])
    style.configure("Secondary.TButton", padding=(14, 7), foreground=PALETTE["text"], background=PALETTE["surface_alt"])
    style.configure("Browse.TButton", padding=(12, 5), foreground=PALETTE["text"], background=PALETTE["surface_alt"])
    style.configure("ExperimentSwitch.TButton", padding=(16, 10), foreground=PALETTE["primary"], background=PALETTE["surface_alt"])
    style.configure("ExperimentSwitchActive.TButton", padding=(16, 10), foreground="#ffffff", background=PALETTE["primary"])
    style.map("ExperimentSwitchActive.TButton", background=[("active", PALETTE["primary_hover"])])
    style.configure("ClosedLoopSwitch.TButton", padding=(16, 10), foreground=PALETTE["closed_loop"], background=PALETTE["surface_alt"])
    style.configure("ClosedLoopSwitchActive.TButton", padding=(16, 10), foreground="#ffffff", background=PALETTE["closed_loop"])
    style.map("ClosedLoopSwitchActive.TButton", background=[("active", PALETTE["closed_loop_hover"])])

    style.configure("TEntry", padding=(6, 5), fieldbackground="#ffffff", bordercolor=PALETTE["border"])
    style.configure("Horizontal.TProgressbar", troughcolor=PALETTE["surface_alt"], background=PALETTE["primary"], bordercolor=PALETTE["border"])
    style.configure("Treeview", rowheight=28, background="#ffffff", fieldbackground="#ffffff", foreground=PALETTE["text"])
    style.configure("Treeview.Heading", background=PALETTE["surface_alt"], foreground=PALETTE["text"], font=("Microsoft YaHei UI", 10, "bold"))
