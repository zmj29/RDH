import unittest

from gui.labels import COLUMN_LABELS, TEXT, format_mode_label, format_progress_message


class GuiLabelsTests(unittest.TestCase):
    def test_ui_text_is_chinese(self):
        self.assertEqual("CNNP 可逆数据隐藏实验控制台", TEXT["app_title"])
        self.assertEqual("开始评估", TEXT["run_button"])
        self.assertEqual("批量性能评估", TEXT["experiment_tab"])
        self.assertEqual("扩展嵌入闭环", TEXT["closed_loop_tab"])
        self.assertEqual("暂停", TEXT["pause_button"])
        self.assertEqual("继续", TEXT["resume_button"])
        self.assertEqual("运行闭环", TEXT["closed_loop_run_button"])
        self.assertEqual("闭环结果", TEXT["closed_loop_result_panel"])
        self.assertEqual("运行日志", TEXT["log_panel"])
        self.assertEqual("嵌入方式", COLUMN_LABELS["mode"])

    def test_format_mode_label_translates_known_modes(self):
        self.assertEqual("直方图平移", format_mode_label("histogram_shifting"))
        self.assertEqual("扩展嵌入", format_mode_label("expansion_embedding"))
        self.assertEqual("unknown", format_mode_label("unknown"))

    def test_format_progress_message_describes_completed_image(self):
        message = format_progress_message(
            {
                "stage": "image_done",
                "mode": "histogram_shifting",
                "payload": 10000,
                "image": "Lena.bmp",
                "current": 2,
                "total": 4,
                "psnr": 52.3,
                "ssim": 0.987,
                "elapsed_seconds": 1.25,
            }
        )

        self.assertIn("[2/4]", message)
        self.assertIn("直方图平移", message)
        self.assertIn("Lena.bmp", message)
        self.assertIn("PSNR=52.3", message)

    def test_format_progress_message_describes_seed_progress(self):
        message = format_progress_message(
            {
                "stage": "seed_start",
                "current": 64,
                "total": 192,
                "seed": 20260407,
                "seed_index": 2,
                "seed_count": 3,
            }
        )

        self.assertIn("[64/192]", message)
        self.assertIn("种子 20260407(2/3)", message)

    def test_format_progress_message_describes_closed_loop_stages(self):
        message = format_progress_message({"stage": "closed_loop_extract_done", "current": 2, "total": 4})

        self.assertIn("[2/4]", message)
        self.assertIn("提取完成", message)


if __name__ == "__main__":
    unittest.main()
