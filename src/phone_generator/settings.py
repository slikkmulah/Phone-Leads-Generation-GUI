"""Local user preferences, kept outside the installed application directory."""

import json
import os
import sys
import tempfile
from pathlib import Path


def default_settings_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "PhoneNumberGenerator" / "settings.json"


def results_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "pyproject.toml").is_file() and (checkout / "src" / "phone_generator").is_dir():
        return checkout
    # A Python package installation may live in a protected site-packages folder.
    return default_settings_path().parent


def default_results_folder() -> Path:
    candidates = (results_root() / "Results", default_settings_path().parent / "Results")
    for folder in candidates:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=folder):
                pass
            return folder
        except OSError:
            continue
    # Keep the GUI available even if neither location can be created.
    return candidates[-1]


def load_folder(path: Path) -> str:
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("save_folder")
        if isinstance(value, str) and value.strip():
            return value
    except (OSError, ValueError, AttributeError):
        pass
    return str(default_results_folder())


def save_folder(path: Path, folder: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".settings-", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump({"save_folder": folder}, handle)
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
