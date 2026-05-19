import unittest

from data_processing.aggregate_multi_seed_results import (
    aggregate_by_image,
    aggregate_by_mode_payload,
    build_seed_summary,
)


class AggregateMultiSeedResultsTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {
                "mode": "histogram_shifting",
                "payload": "10000",
                "image": "Barbara.bmp",
                "psnr": "55.0",
                "ssim": "0.9999",
                "elapsed_seconds": "7.0",
                "seed": "20260406",
            },
            {
                "mode": "histogram_shifting",
                "payload": "10000",
                "image": "Barbara.bmp",
                "psnr": "54.0",
                "ssim": "0.9997",
                "elapsed_seconds": "6.0",
                "seed": "20260407",
            },
            {
                "mode": "histogram_shifting",
                "payload": "10000",
                "image": "Lena.bmp",
                "psnr": "52.0",
                "ssim": "0.9995",
                "elapsed_seconds": "5.0",
                "seed": "20260406",
            },
            {
                "mode": "histogram_shifting",
                "payload": "10000",
                "image": "Lena.bmp",
                "psnr": "50.0",
                "ssim": "0.9991",
                "elapsed_seconds": "4.0",
                "seed": "20260407",
            },
        ]

    def test_aggregate_by_mode_payload_builds_mean_and_std(self):
        summary_rows = aggregate_by_mode_payload(self.rows)

        self.assertEqual(1, len(summary_rows))
        row = summary_rows[0]
        self.assertEqual("histogram_shifting", row["mode"])
        self.assertEqual(10000, row["payload"])
        self.assertEqual(52.75, row["mean_psnr"])
        self.assertEqual(2.22, row["std_psnr"])
        self.assertEqual(2, row["seed_count"])
        self.assertEqual(2, row["image_count"])
        self.assertEqual(4, row["sample_count"])
        self.assertEqual("52.75 ± 2.22", row["psnr_mean_std"])

    def test_aggregate_by_image_groups_each_image_across_seeds(self):
        image_rows = aggregate_by_image(self.rows)

        self.assertEqual(2, len(image_rows))
        self.assertEqual("Barbara.bmp", image_rows[0]["image"])
        self.assertEqual(54.5, image_rows[0]["mean_psnr"])
        self.assertEqual(0.71, image_rows[0]["std_psnr"])
        self.assertEqual(2, image_rows[0]["seed_count"])

    def test_build_seed_summary_lists_each_seed_file(self):
        seed_summary = build_seed_summary(
            [
                r"results\multi_seed_8img\seed_20260406\per_image_results.csv",
                r"results\multi_seed_8img\seed_20260407\per_image_results.csv",
            ]
        )

        self.assertEqual(2, len(seed_summary))
        self.assertEqual("20260406", seed_summary[0]["seed"])
        self.assertEqual(
            r"results\multi_seed_8img\seed_20260406\per_image_results.csv",
            seed_summary[0]["source_csv"],
        )


if __name__ == "__main__":
    unittest.main()
