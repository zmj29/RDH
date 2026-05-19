import unittest
from pathlib import Path
from unittest.mock import patch

from data_processing.prepare_extended_images import (
    build_output_path,
    get_recommended_image_set,
    list_supported_images,
)


class PrepareExtendedImagesTests(unittest.TestCase):
    def test_get_recommended_image_set_returns_final_eight_names(self):
        self.assertEqual(
            [
                "Barbara",
                "Lena",
                "Peppers",
                "yacht",
                "Baboon",
                "Boat",
                "Goldhill",
                "Airplane",
            ],
            get_recommended_image_set(),
        )

    def test_list_supported_images_filters_and_sorts_files(self):
        root = Path(r"D:\mock_input")
        fake_paths = [
            Path(r"D:\mock_input\notes.txt"),
            Path(r"D:\mock_input\Boat.png"),
            Path(r"D:\mock_input\baboon.JPG"),
            Path(r"D:\mock_input\Airplane.bmp"),
        ]

        with patch("pathlib.Path.iterdir", return_value=fake_paths), patch(
            "pathlib.Path.is_file", return_value=True
        ):
            image_names = [path.name for path in list_supported_images(root)]

        self.assertEqual(
            ["Airplane.bmp", "baboon.JPG", "Boat.png"],
            image_names,
        )

    def test_build_output_path_uses_bmp_suffix(self):
        output_path = build_output_path(Path(r"D:\output"), Path("Boat.png"))
        self.assertEqual(Path(r"D:\output\Boat.bmp"), output_path)


if __name__ == "__main__":
    unittest.main()
