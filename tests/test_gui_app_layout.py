import tkinter as tk
import unittest

from gui.app import RESULTS_VISIBLE_ROWS, CnnpGuiApp
from gui.config import DEFAULT_IMAGE_DIR, DEFAULT_PAYLOADS_TEXT, DEFAULT_SEEDS_TEXT
from gui.labels import TEXT


class GuiAppLayoutTests(unittest.TestCase):
    def test_main_views_are_split_and_switchable(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            self.assertEqual("experiment", app.active_view)
            self.assertEqual(TEXT["experiment_tab"], app.experiment_switch["text"])
            self.assertEqual(TEXT["closed_loop_tab"], app.closed_loop_switch["text"])

            app._show_view("closed_loop")

            self.assertEqual("closed_loop", app.active_view)
            self.assertIs(app.closed_loop_page, app.active_page)
        finally:
            root.destroy()

    def test_progress_panels_belong_to_their_own_pages(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            self.assertIs(app.experiment_page, app.experiment_progress_panel.master)
            self.assertIs(app.closed_loop_page, app.closed_loop_progress_panel.master)
            self.assertEqual("pack", app.experiment_page.winfo_manager())
            self.assertEqual("", app.closed_loop_page.winfo_manager())

            app._show_view("closed_loop")

            self.assertEqual("", app.experiment_page.winfo_manager())
            self.assertEqual("pack", app.closed_loop_page.winfo_manager())
        finally:
            root.destroy()

    def test_main_view_uses_clean_result_and_log_button_layout(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            self.assertEqual("pack", app.page_container.winfo_manager())
            self.assertEqual("grid", app.results_tree.master.master.winfo_manager())
            self.assertEqual(RESULTS_VISIBLE_ROWS, int(app.results_tree.cget("height")))
            self.assertEqual("pack", app.results_scrollbar.winfo_manager())
            self.assertEqual("grid", app.log_footer.winfo_manager())
            self.assertIs(app.log_footer, app.view_log_button.master)
        finally:
            root.destroy()

    def test_experiment_actions_stay_outside_scrollable_page(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            self.assertEqual("pack", app.experiment_action_bar.winfo_manager())
            self.assertIs(app.workspace, app.experiment_action_bar.master)
            self.assertIs(app.experiment_action_bar, app.run_button.master)
            self.assertIs(app.experiment_action_bar, app.clear_log_button.master)

            app._show_view("closed_loop")

            self.assertEqual("", app.experiment_action_bar.winfo_manager())
        finally:
            root.destroy()

    def test_closed_loop_action_stays_outside_scrollable_page(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            self.assertEqual("", app.closed_loop_action_bar.winfo_manager())

            app._show_view("closed_loop")

            self.assertEqual("pack", app.closed_loop_action_bar.winfo_manager())
            self.assertIs(app.workspace, app.closed_loop_action_bar.master)
            self.assertIs(app.closed_loop_action_bar, app.closed_loop_button.master)
            self.assertEqual("", app.experiment_action_bar.winfo_manager())
        finally:
            root.destroy()

    def test_log_button_opens_log_window(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            app._append_log("hello")
            app._show_log_window()

            self.assertIsNotNone(app.log_window)
            self.assertIsNotNone(app.log_window_text)
            self.assertIn("hello", app.log_window_text.get("1.0", tk.END))
        finally:
            root.destroy()

    def test_experiment_defaults_use_eight_image_batch_settings(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            self.assertEqual(str(DEFAULT_IMAGE_DIR), app.image_dir_var.get())
            self.assertEqual(DEFAULT_PAYLOADS_TEXT, app.payloads_var.get())
            self.assertEqual(DEFAULT_SEEDS_TEXT, app.seed_var.get())
        finally:
            root.destroy()

    def test_progress_state_is_separate_per_view(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            app._set_progress("experiment", 25, "批量进度")

            self.assertEqual(25, app.experiment_progress_value_var.get())
            self.assertEqual("批量进度", app.experiment_progress_text_var.get())
            self.assertEqual(0, app.closed_loop_progress_value_var.get())
            self.assertEqual(TEXT["progress_idle"], app.closed_loop_progress_text_var.get())

            app._set_progress("closed_loop", 50, "闭环进度")

            self.assertEqual(25, app.experiment_progress_value_var.get())
            self.assertEqual("批量进度", app.experiment_progress_text_var.get())
            self.assertEqual(50, app.closed_loop_progress_value_var.get())
            self.assertEqual("闭环进度", app.closed_loop_progress_text_var.get())
        finally:
            root.destroy()

    def test_only_running_view_pause_button_is_enabled(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)
            app.current_worker_kind = "experiment"

            app._set_running(True)

            self.assertEqual("normal", str(app.experiment_pause_button["state"]))
            self.assertEqual("disabled", str(app.closed_loop_pause_button["state"]))
        finally:
            root.destroy()

    def test_closed_loop_done_shows_report_outputs(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = CnnpGuiApp(root)

            app._handle_closed_loop_done(
                {
                    "extract_result": {"secret_text": "测试"},
                    "verify_result": {
                        "message_match": True,
                        "image_match": True,
                        "bit_error_count": 0,
                        "pixel_error_count": 0,
                    },
                    "paths": {
                        "watermarked_path": "out/watermarked.png",
                        "recovered_path": "out/recovered.png",
                        "text_output_path": "out/extracted.txt",
                        "summary_path": "out/verification_summary.json",
                        "report_path": "out/closed_loop_report.txt",
                    },
                }
            )

            output_text = app.closed_loop_output_var.get()
            self.assertIn("out/closed_loop_report.txt", output_text)
            self.assertIn("out/verification_summary.json", output_text)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
