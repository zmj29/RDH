import unittest
from pathlib import Path

from gui.config import (
    DEFAULT_CLOSED_LOOP_CARRIER,
    DEFAULT_IMAGE_DIR,
    DEFAULT_PAYLOADS_TEXT,
    DEFAULT_SEEDS_TEXT,
    GuiClosedLoopConfig,
    GuiExperimentConfig,
    build_closed_loop_output_paths,
    build_run_output_paths,
    parse_payloads,
    parse_seeds,
    to_closed_loop_kwargs,
    to_runtime_kwargs,
)


class GuiConfigTests(unittest.TestCase):
    def test_default_batch_settings_match_eight_image_experiment(self):
        self.assertEqual(
            Path("datasets") / "extended_test_images_8",
            DEFAULT_IMAGE_DIR.relative_to(DEFAULT_IMAGE_DIR.parents[1]),
        )
        self.assertEqual(
            Path("datasets") / "standard_test_images" / "Lena.bmp",
            DEFAULT_CLOSED_LOOP_CARRIER.relative_to(DEFAULT_CLOSED_LOOP_CARRIER.parents[2]),
        )
        self.assertEqual("10000,20000,50000,100000", DEFAULT_PAYLOADS_TEXT)
        self.assertEqual("20260406,20260407,20260408", DEFAULT_SEEDS_TEXT)

    def test_parse_payloads_accepts_commas_spaces_and_semicolons(self):
        self.assertEqual((10000, 20000, 50000), parse_payloads("10000, 20000;50000"))

    def test_parse_payloads_rejects_empty_input(self):
        with self.assertRaisesRegex(ValueError, "至少输入一个载荷长度"):
            parse_payloads(" , ; ")

    def test_parse_payloads_rejects_non_positive_values(self):
        with self.assertRaisesRegex(ValueError, "载荷长度必须大于或等于 1"):
            parse_payloads("10000, 0")

    def test_parse_seeds_accepts_multiple_seed_values(self):
        self.assertEqual((20260406, 20260407, 20260408), parse_seeds("20260406, 20260407;20260408"))

    def test_parse_seeds_rejects_empty_input(self):
        with self.assertRaisesRegex(ValueError, "至少输入一个随机种子"):
            parse_seeds(" , ; ")

    def test_build_run_output_paths_uses_expected_filenames(self):
        output_dir = Path("results") / "gui_runs" / "run_20260430_120000"

        paths = build_run_output_paths(output_dir)

        self.assertEqual(output_dir / "cnnp_psnr_results.csv", paths["results_csv_path"])
        self.assertEqual(output_dir / "per_image_results.csv", paths["per_image_csv_path"])
        self.assertEqual(output_dir / "average_results.csv", paths["average_csv_path"])
        self.assertEqual(output_dir / "payload_psnr_trend.csv", paths["trend_csv_path"])
        self.assertEqual(output_dir / "mode_gap_comparison.csv", paths["gap_csv_path"])
        self.assertEqual(output_dir / "environment_info.txt", paths["environment_info_path"])
        self.assertEqual(output_dir / "logs", paths["logs_dir"])

    def test_to_runtime_kwargs_maps_gui_config_to_batch_runner_arguments(self):
        config = GuiExperimentConfig(
            image_dir=Path("datasets") / "extended_test_images_8",
            model_path=Path("model_parameter") / "model_state.pth",
            modes=("histogram_shifting",),
            payloads=(10000,),
            seeds=(20260430,),
            output_dir=Path("results") / "gui_runs" / "run_20260430_120000",
        )

        kwargs = to_runtime_kwargs(config)

        self.assertEqual(Path("datasets") / "extended_test_images_8", kwargs["image_dir"])
        self.assertEqual(Path("model_parameter") / "model_state.pth", kwargs["model_path"])
        self.assertEqual(["histogram_shifting"], kwargs["modes"])
        self.assertEqual([10000], kwargs["payloads"])
        self.assertEqual(20260430, kwargs["seed"])
        self.assertEqual((512, 512), kwargs["image_size"])
        self.assertEqual(config.output_dir / "average_results.csv", kwargs["average_csv_path"])

    def test_to_runtime_kwargs_can_target_a_seed_output_dir(self):
        config = GuiExperimentConfig(
            image_dir=Path("datasets") / "extended_test_images_8",
            model_path=Path("model_parameter") / "model_state.pth",
            modes=("histogram_shifting",),
            payloads=(10000,),
            seeds=(20260406, 20260407),
            output_dir=Path("results") / "gui_runs" / "run_20260430_120000",
        )

        kwargs = to_runtime_kwargs(config, seed=20260407, output_dir=config.output_dir / "seed_20260407")

        self.assertEqual(20260407, kwargs["seed"])
        self.assertEqual(config.output_dir / "seed_20260407" / "per_image_results.csv", kwargs["per_image_csv_path"])

    def test_build_closed_loop_output_paths_uses_expected_filenames(self):
        output_dir = Path("results") / "gui_closed_loop" / "run_20260504_120000"

        paths = build_closed_loop_output_paths(output_dir)

        self.assertEqual(output_dir / "watermarked.png", paths["watermarked_path"])
        self.assertEqual(output_dir / "carrier.png", paths["carrier_output_path"])
        self.assertEqual(output_dir / "recovered.png", paths["recovered_path"])
        self.assertEqual(output_dir / "extracted.txt", paths["text_output_path"])
        self.assertEqual(output_dir / "extracted_bits.txt", paths["bits_output_path"])
        self.assertEqual(output_dir / "verification_summary.json", paths["summary_path"])
        self.assertEqual(output_dir / "closed_loop_report.txt", paths["report_path"])

    def test_to_closed_loop_kwargs_maps_gui_config_to_closed_loop_runner(self):
        config = GuiClosedLoopConfig(
            carrier_path=Path("datasets") / "standard_test_images" / "Lena.bmp",
            model_path=Path("model_parameter") / "model_state.pth",
            secret_text="测试",
            output_dir=Path("results") / "gui_closed_loop" / "run_20260504_120000",
        )

        kwargs = to_closed_loop_kwargs(config)

        self.assertEqual(config.carrier_path, kwargs["carrier_path"])
        self.assertEqual(config.model_path, kwargs["model_path"])
        self.assertEqual("测试", kwargs["secret_text"])
        self.assertEqual(config.output_dir / "watermarked.png", kwargs["watermarked_path"])
        self.assertEqual(config.output_dir / "carrier.png", kwargs["carrier_output_path"])
        self.assertEqual(config.output_dir / "recovered.png", kwargs["recovered_path"])
        self.assertEqual(config.output_dir / "extracted.txt", kwargs["text_output_path"])
        self.assertEqual(config.output_dir / "verification_summary.json", kwargs["summary_path"])
        self.assertEqual(config.output_dir / "closed_loop_report.txt", kwargs["report_path"])


if __name__ == "__main__":
    unittest.main()
