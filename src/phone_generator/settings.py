"""Local user preferences, kept outside the installed application directory."""

import json
import os
import tempfile
from pathlib import Path


def default_settings_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "PhoneNumberGenerator" / "settings.json"


def load_folder(path: Path) -> str:
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("save_folder")
        if isinstance(value, str) and value.strip():
            return value
    except (OSError, ValueError, AttributeError):
        pass
    documents = Path.home() / "Documents"
    return str(documents if documents.is_dir() else Path.home())


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
