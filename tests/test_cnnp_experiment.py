import unittest

from data_processing.cnnp_experiment import (
    build_chart_rows,
    build_conditions,
    format_environment_lines,
    summarize_results,
)


class ExperimentSummaryTests(unittest.TestCase):
    def test_build_conditions_expands_all_mode_payload_image_pairs(self):
        conditions = build_conditions(
            modes=["histogram_shifting", "expansion_embedding"],
            payloads=[10000, 20000],
            images=["Barbara.bmp", "Lena.bmp"],
        )

        self.assertEqual(8, len(conditions))
        self.assertEqual(
            {
                "mode": "histogram_shifting",
                "payload": 10000,
                "image": "Barbara.bmp",
            },
            conditions[0],
        )
        self.assertEqual(
            {
                "mode": "expansion_embedding",
                "payload": 20000,
                "image": "Lena.bmp",
            },
            conditions[-1],
        )

    def test_summarize_results_groups_by_mode_and_payload(self):
        rows = [
            {
                "mode": "histogram_shifting",
                "payload": 10000,
                "image": "Barbara.bmp",
                "psnr": 50.0,
                "ssim": 0.99,
                "elapsed_seconds": 1.0,
            },
            {
                "mode": "histogram_shifting",
                "payload": 10000,
                "image": "Lena.bmp",
                "psnr": 54.0,
                "ssim": 0.97,
                "elapsed_seconds": 3.0,
            },
        ]

        summary = summarize_results(rows)

        self.assertEqual(1, len(summary))
        self.assertEqual("histogram_shifting", summary[0]["mode"])
        self.assertEqual(10000, summary[0]["payload"])
        self.assertEqual(52.0, summary[0]["average_psnr"])
        self.assertEqual(0.98, summary[0]["average_ssim"])
        self.assertEqual(2.0, summary[0]["average_elapsed_seconds"])

    def test_build_chart_rows_creates_gap_table(self):
        summary_rows = [
            {
                "mode": "histogram_shifting",
                "payload": 10000,
                "average_psnr": 55.0,
                "average_ssim": 0.99,
                "average_elapsed_seconds": 1.2,
            },
            {
                "mode": "expansion_embedding",
                "payload": 10000,
                "average_psnr": 47.0,
                "average_ssim": 0.96,
                "average_elapsed_seconds": 1.4,
            },
        ]

        trend_rows, gap_rows = build_chart_rows(summary_rows)

        self.assertEqual(
            ["payload", "mode", "average_psnr", "average_ssim", "average_elapsed_seconds"],
            list(trend_rows[0].keys()),
        )
        self.assertEqual(1, len(gap_rows))
        self.assertEqual(10000, gap_rows[0]["payload"])
        self.assertEqual(8.0, gap_rows[0]["psnr_gap"])

    def test_format_environment_lines_contains_required_fields(self):
        lines = format_environment_lines(
            {
                "run_datetime": "2026-04-06 10:00:00",
                "device": "cpu",
                "python_version": "3.7.9",
                "torch_version": "1.6.0",
                "matlab_version": "9.6",
                "model_file": "model_state.pth",
                "image_names": ["Barbara.bmp", "Lena.bmp"],
                "payloads": [10000, 20000],
                "modes": ["histogram_shifting", "expansion_embedding"],
                "seed": 20260406,
            }
        )

        joined = "\n".join(lines)

        self.assertIn("run_datetime: 2026-04-06 10:00:00", joined)
        self.assertIn("python_version: 3.7.9", joined)
        self.assertIn("seed: 20260406", joined)


if __name__ == "__main__":
    unittest.main()
