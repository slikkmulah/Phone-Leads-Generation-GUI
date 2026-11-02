import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phone_generator.settings import default_results_folder, load_folder, results_root, save_folder


class SettingsTests(unittest.TestCase):
    def test_folder_round_trip_in_new_config_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config" / "settings.json"
            folder = str(Path(directory) / "Lists with spaces")
            save_folder(config, folder)
            self.assertEqual(load_folder(config), folder)
            self.assertEqual(list(config.parent.iterdir()), [config])

    def test_corrupt_or_unexpected_settings_use_default(self):
        with tempfile.TemporaryDirectory() as directory, patch("phone_generator.settings.results_root", return_value=Path(directory)):
            config = Path(directory) / "settings.json"
            default = load_folder(config)
            self.assertEqual(default, str(Path(directory) / "Results"))
            self.assertTrue(Path(default).is_dir())
            for content in ("invalid json", "[]", '{"save_folder": 42}', '{"save_folder": ""}'):
                config.write_text(content)
                self.assertEqual(load_folder(config), default)

    def test_saved_choice_does_not_create_default_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "settings.json"
            save_folder(config, directory)
            with patch("phone_generator.settings.default_results_folder") as default:
                self.assertEqual(load_folder(config), directory)
                default.assert_not_called()

    def test_frozen_app_uses_executable_directory(self):
        with patch("phone_generator.settings.sys.frozen", True, create=True), \
             patch("phone_generator.settings.sys.executable", str(Path.cwd() / "Portable App" / "PhoneNumberGenerator.exe")):
            self.assertEqual(results_root(), Path.cwd() / "Portable App")

    def test_source_checkout_uses_repository_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "src" / "phone_generator"
            package.mkdir(parents=True)
            (root / "pyproject.toml").touch()
            with patch("phone_generator.settings.__file__", str(package / "settings.py")), \
                 patch("phone_generator.settings.sys.frozen", False, create=True):
                self.assertEqual(results_root(), root.resolve())

    def test_installed_python_package_uses_user_data_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "user data" / "settings.json"
            with patch("phone_generator.settings.__file__", str(root / "site-packages" / "phone_generator" / "settings.py")), \
                 patch("phone_generator.settings.sys.frozen", False, create=True), \
                 patch("phone_generator.settings.default_settings_path", return_value=config):
                self.assertEqual(default_results_folder(), config.parent / "Results")

    def test_unwritable_app_folder_falls_back_to_user_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blocked = root / "blocked"
            blocked.write_text("a file cannot contain a Results directory")
            config = root / "user data" / "settings.json"
            with patch("phone_generator.settings.results_root", return_value=blocked), \
                 patch("phone_generator.settings.default_settings_path", return_value=config):
                self.assertEqual(default_results_folder(), config.parent / "Results")
