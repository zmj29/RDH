import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


class BitHelperTests(unittest.TestCase):
    def test_text_bits_round_trip_utf8(self):
        from rdh_bits import bits_to_text, text_to_bits

        bits = text_to_bits("秘密A")

        self.assertEqual("秘密A", bits_to_text(bits))
        self.assertEqual(0, len(bits) % 8)

    def test_even_bit_count_rejects_odd_length(self):
        from rdh_bits import ensure_even_bit_count

        with self.assertRaises(ValueError):
            ensure_even_bit_count([1, 0, 1])


class ExpansionClosedLoopTests(unittest.TestCase):
    def test_reverse_two_stage_extracts_stage_one_before_stage_zero(self):
        from expansion_closed_loop import reverse_two_stage

        calls = []

        def fake_reverse_stage(image, parity):
            calls.append((image, parity))
            if parity == 1:
                return "after-stage-0", [1, 1]
            if parity == 0:
                return "carrier", [0, 0]
            raise AssertionError(f"unexpected parity: {parity}")

        carrier, payload_bits = reverse_two_stage("watermarked", fake_reverse_stage)

        self.assertEqual("carrier", carrier)
        self.assertEqual([0, 0, 1, 1], payload_bits)
        self.assertEqual([("watermarked", 1), ("after-stage-0", 0)], calls)

    def test_build_verification_result_counts_message_and_pixel_errors(self):
        from expansion_closed_loop import build_verification_result

        result = build_verification_result(
            original_bits=[1, 0, 1, 1],
            extracted_bits=[1, 1, 1, 0],
            original_image=[[1, 2], [3, 4]],
            recovered_image=[[1, 9], [3, 8]],
        )

        self.assertFalse(result["message_match"])
        self.assertFalse(result["image_match"])
        self.assertEqual(2, result["bit_error_count"])
        self.assertEqual(2, result["pixel_error_count"])

    def test_roundtrip_writes_standard_report_files(self):
        from expansion_closed_loop import run_expansion_roundtrip

        with TemporaryDirectory() as tmp_dir, mock.patch(
            "expansion_closed_loop.embed_secret_text", return_value={"secret_bit_count": 48}
        ) as embed, mock.patch(
            "expansion_closed_loop.extract_secret_text",
            return_value={"secret_text": "测试", "secret_bit_count": 48},
        ) as extract, mock.patch(
            "expansion_closed_loop.verify_closed_loop",
            return_value={"message_match": True, "image_match": True, "bit_error_count": 0, "pixel_error_count": 0},
        ) as verify:
            result = run_expansion_roundtrip(
                carrier_path=Path("carrier.bmp"),
                secret_text="测试",
                output_dir=Path(tmp_dir),
                model_path=Path("model.pth"),
            )

            self.assertEqual("success", result["status"])
            self.assertEqual(str(Path(tmp_dir) / "verification_summary.json"), result["paths"]["summary_path"])
            self.assertEqual(str(Path(tmp_dir) / "closed_loop_report.txt"), result["paths"]["report_path"])
            self.assertTrue((Path(tmp_dir) / "verification_summary.json").exists())
            self.assertTrue((Path(tmp_dir) / "closed_loop_report.txt").exists())
        embed.assert_called_once()
        extract.assert_called_once()
        verify.assert_called_once()


class RdhCliTests(unittest.TestCase):
    def test_embed_command_passes_secret_text_and_paths(self):
        from rdh_cli import main

        with mock.patch("rdh_cli.embed_secret_text", return_value={"ok": True}) as embed, mock.patch(
            "sys.stdout", new_callable=StringIO
        ):
            exit_code = main(
                [
                    "embed",
                    "--carrier",
                    "carrier.bmp",
                    "--secret-text",
                    "hello",
                    "--watermarked",
                    "watermarked.png",
                    "--model",
                    "model.pth",
                ]
            )

        self.assertEqual(0, exit_code)
        embed.assert_called_once()
        _, kwargs = embed.call_args
        self.assertEqual("hello", kwargs["secret_text"])
        self.assertEqual("carrier.bmp", str(kwargs["carrier_path"]))
        self.assertEqual("watermarked.png", str(kwargs["watermarked_path"]))

    def test_roundtrip_command_runs_expansion_roundtrip(self):
        from rdh_cli import main

        with mock.patch("rdh_cli.run_expansion_roundtrip", return_value={"ok": True}) as roundtrip, mock.patch(
            "sys.stdout", new_callable=StringIO
        ):
            exit_code = main(
                [
                    "roundtrip",
                    "--carrier",
                    "carrier.bmp",
                    "--secret-text",
                    "hello",
                    "--output-dir",
                    "out",
                    "--model",
                    "model.pth",
                ]
            )

        self.assertEqual(0, exit_code)
        roundtrip.assert_called_once()
        _, kwargs = roundtrip.call_args
        self.assertEqual("hello", kwargs["secret_text"])
        self.assertEqual("carrier.bmp", str(kwargs["carrier_path"]))
        self.assertEqual("out", str(kwargs["output_dir"]))


if __name__ == "__main__":
    unittest.main()
