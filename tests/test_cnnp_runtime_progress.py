import unittest
from pathlib import Path
from unittest import mock

from data_processing import cnnp_runtime


class RuntimeProgressTests(unittest.TestCase):
    def test_run_condition_reports_image_progress(self):
        events = []
        progress_state = {"completed": 0, "total": 2}
        context = {
            "np": object(),
            "device_label": "cpu",
            "model_path": Path("model_state.pth"),
        }

        with mock.patch.object(cnnp_runtime, "_build_message", return_value=[1, 0]), mock.patch.object(
            cnnp_runtime, "_run_single_image", return_value=("original", "embedded")
        ), mock.patch.object(cnnp_runtime, "_calculate_psnr", return_value=51.25), mock.patch.object(
            cnnp_runtime, "_calculate_ssim", return_value=0.987654
        ):
            rows, _ = cnnp_runtime._run_condition(
                context,
                Path("datasets") / "standard_test_images",
                ["Barbara.bmp", "Lena.bmp"],
                "histogram_shifting",
                10000,
                20260430,
                (512, 512),
                "2026-04-30 12:00:00",
                progress_callback=events.append,
                progress_state=progress_state,
            )

        self.assertEqual(2, len(rows))
        self.assertEqual(2, progress_state["completed"])
        self.assertEqual("image_start", events[0]["stage"])
        self.assertEqual("Barbara.bmp", events[0]["image"])
        self.assertEqual(0, events[0]["current"])
        self.assertEqual("image_done", events[1]["stage"])
        self.assertEqual(1, events[1]["current"])
        self.assertEqual(51.25, events[1]["psnr"])
        self.assertEqual("image_done", events[-1]["stage"])
        self.assertEqual(2, events[-1]["current"])

    def test_run_condition_checks_pause_before_each_image(self):
        pause_callback = mock.Mock()
        progress_state = {"completed": 0, "total": 2}
        context = {
            "np": object(),
            "device_label": "cpu",
            "model_path": Path("model_state.pth"),
        }

        with mock.patch.object(cnnp_runtime, "_build_message", return_value=[1, 0]), mock.patch.object(
            cnnp_runtime, "_run_single_image", return_value=("original", "embedded")
        ), mock.patch.object(cnnp_runtime, "_calculate_psnr", return_value=51.25), mock.patch.object(
            cnnp_runtime, "_calculate_ssim", return_value=0.987654
        ):
            cnnp_runtime._run_condition(
                context,
                Path("datasets") / "standard_test_images",
                ["Barbara.bmp", "Lena.bmp"],
                "histogram_shifting",
                10000,
                20260430,
                (512, 512),
                "2026-04-30 12:00:00",
                progress_state=progress_state,
                pause_callback=pause_callback,
            )

        self.assertEqual(2, pause_callback.call_count)


if __name__ == "__main__":
    unittest.main()
