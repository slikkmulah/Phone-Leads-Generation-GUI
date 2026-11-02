import tempfile
import unittest
from pathlib import Path

from phone_generator.settings import load_folder, save_folder


class SettingsTests(unittest.TestCase):
    def test_folder_round_trip_in_new_config_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config" / "settings.json"
            folder = str(Path(directory) / "Lists with spaces")
            save_folder(config, folder)
            self.assertEqual(load_folder(config), folder)
            self.assertEqual(list(config.parent.iterdir()), [config])

    def test_corrupt_or_unexpected_settings_use_default(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "settings.json"
            default = load_folder(config)
            for content in ("invalid json", "[]", '{"save_folder": 42}', '{"save_folder": ""}'):
                config.write_text(content)
                self.assertEqual(load_folder(config), default)
