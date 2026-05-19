import unittest
from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep
from unittest import mock

from gui.config import GuiClosedLoopConfig, GuiExperimentConfig
from gui.workers import PauseController, _run_closed_loop, _run_configured_experiment


class PauseControllerTests(unittest.TestCase):
    def test_wait_if_paused_blocks_until_resume(self):
        pause = PauseController()
        pause.pause()
        calls = []
        thread = Thread(target=lambda: (pause.wait_if_paused(), calls.append("resumed")))

        thread.start()
        sleep(0.02)
        self.assertEqual([], calls)
        pause.resume()
        thread.join(timeout=1)

        self.assertEqual(["resumed"], calls)


class GuiClosedLoopWorkerTests(unittest.TestCase):
    def test_run_closed_loop_embeds_extracts_and_verifies(self):
        events = Queue()
        config = GuiClosedLoopConfig(
            carrier_path=Path("datasets") / "standard_test_images" / "Lena.bmp",
            model_path=Path("model_parameter") / "model_state.pth",
            secret_text="测试",
            output_dir=Path("results") / "gui_closed_loop" / "run_20260504_120000",
        )

        with mock.patch("gui.workers.embed_secret_text", return_value={"secret_bit_count": 48}) as embed, mock.patch(
            "gui.workers.extract_secret_text",
            return_value={"secret_text": "测试", "secret_bit_count": 48},
        ) as extract, mock.patch(
            "gui.workers.verify_closed_loop",
            return_value={"message_match": True, "image_match": True, "bit_error_count": 0, "pixel_error_count": 0},
        ) as verify, mock.patch("gui.workers.write_roundtrip_report") as write_report:
            _run_closed_loop(config, events)

        kinds = []
        stages = []
        done_payload = {}
        while not events.empty():
            event = events.get()
            kinds.append(event.kind)
            if event.kind == "progress":
                stages.append(event.payload["stage"])
            if event.kind == "done":
                done_payload = event.payload

        self.assertIn("done", kinds)
        self.assertEqual(
            [
                "closed_loop_start",
                "closed_loop_embed_done",
                "closed_loop_extract_done",
                "closed_loop_verify_done",
            ],
            stages,
        )
        embed.assert_called_once()
        extract.assert_called_once()
        verify.assert_called_once()
        write_report.assert_called_once()
        self.assertIn("summary_path", done_payload["paths"])
        self.assertIn("report_path", done_payload["paths"])

    def test_run_closed_loop_checks_pause_between_stages(self):
        events = Queue()
        pause = mock.Mock()
        config = GuiClosedLoopConfig(
            carrier_path=Path("datasets") / "standard_test_images" / "Lena.bmp",
            model_path=Path("model_parameter") / "model_state.pth",
            secret_text="测试",
            output_dir=Path("results") / "gui_closed_loop" / "run_20260504_120000",
        )

        with mock.patch("gui.workers.embed_secret_text", return_value={"secret_bit_count": 48}), mock.patch(
            "gui.workers.extract_secret_text",
            return_value={"secret_text": "测试", "secret_bit_count": 48},
        ), mock.patch(
            "gui.workers.verify_closed_loop",
            return_value={"message_match": True, "image_match": True, "bit_error_count": 0, "pixel_error_count": 0},
        ), mock.patch("gui.workers.write_roundtrip_report"):
            _run_closed_loop(config, events, pause)

        self.assertGreaterEqual(pause.wait_if_paused.call_count, 3)


class GuiExperimentWorkerTests(unittest.TestCase):
    def test_run_configured_experiment_runs_each_seed_and_writes_aggregate_outputs(self):
        output_dir = Path("results") / "gui_worker_test" / "run_20260505_120000"
        config = GuiExperimentConfig(
            image_dir=Path("datasets") / "extended_test_images_8",
            model_path=Path("model_parameter") / "model_state.pth",
            modes=("histogram_shifting",),
            payloads=(10000,),
            seeds=(20260406, 20260407),
            output_dir=output_dir,
        )
        calls = []
        progress_events = []

        def runner(**kwargs):
            seed = kwargs["seed"]
            calls.append(seed)
            kwargs["progress_callback"]({"stage": "start", "current": 0, "total": 1})
            kwargs["progress_callback"]({"stage": "complete", "current": 1, "total": 1, "output_dir": str(output_dir)})
            return {
                "per_image_rows": [
                    {
                        "mode": "histogram_shifting",
                        "payload": 10000,
                        "image": "Lena.bmp",
                        "psnr": 50.0 + len(calls),
                        "ssim": 0.99,
                        "elapsed_seconds": 1.0,
                        "seed": seed,
                    }
                ]
            }

        with mock.patch("data_processing.cnnp_experiment.write_csv_rows") as write_csv_rows:
            result = _run_configured_experiment(config, runner, progress_events.append, None)

        written_paths = [call.args[0] for call in write_csv_rows.call_args_list]
        self.assertEqual([20260406, 20260407], calls)
        self.assertEqual(2, result["summary_rows"][0]["seed_count"])
        self.assertEqual(2, result["summary_rows"][0]["sample_count"])
        self.assertIn(output_dir / "per_image_results.csv", written_paths)
        self.assertIn(output_dir / "aggregated" / "mode_payload_summary.csv", written_paths)
        self.assertEqual(
            ["seed_start", "seed_complete", "seed_start", "seed_complete", "complete"],
            [event["stage"] for event in progress_events],
        )


if __name__ == "__main__":
    unittest.main()
