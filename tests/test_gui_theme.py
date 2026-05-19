import unittest

from gui.theme import PALETTE, get_window_geometry


class GuiThemeTests(unittest.TestCase):
    def test_palette_contains_core_surface_and_action_colors(self):
        self.assertEqual("#f6f8fb", PALETTE["app_bg"])
        self.assertEqual("#ffffff", PALETTE["surface"])
        self.assertEqual("#2563eb", PALETTE["primary"])
        self.assertEqual("#0f766e", PALETTE["closed_loop"])

    def test_window_geometry_fits_switchable_console(self):
        self.assertEqual("1240x860", get_window_geometry())


if __name__ == "__main__":
    unittest.main()
