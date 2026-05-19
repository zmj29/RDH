import importlib
import unittest

from gui import app


class GuiEntrypointTests(unittest.TestCase):
    def test_gui_main_exports_gui_app_main(self):
        module = importlib.import_module("gui_main")

        self.assertIs(app.main, module.main)


if __name__ == "__main__":
    unittest.main()
