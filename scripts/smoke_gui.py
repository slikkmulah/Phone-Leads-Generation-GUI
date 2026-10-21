"""Exercise real Tk widgets and background export without a UI robot."""
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from phone_generator.gui import App


def main():
    app = App()
    app.withdraw()
    errors = []
    try:
        with tempfile.TemporaryDirectory() as directory, patch("phone_generator.gui.messagebox.showerror", side_effect=lambda *a, **k: errors.append(a)):
            app.entries.insert("1.0", "206-234,425-234")
            app.preview()
            assert "+1" in app.sample_box.get("1.0", "end")
            for mode, entries in (("nanp", "206-234 425-234"), ("custom", "7700 7701")):
                app.mode.set(mode)
                app.change_mode()
                app.entries.delete("1.0", "end")
                app.entries.insert("1.0", entries)
                target = Path(directory) / f"{mode}.csv"
                with patch("phone_generator.gui.filedialog.asksaveasfilename", return_value=str(target)):
                    app.save()
                deadline = time.monotonic() + 20
                while app.busy and time.monotonic() < deadline:
                    app.update()
                    time.sleep(0.01)
                assert not app.busy, "Export timed out"
                assert target.exists(), errors
                assert len(target.read_text().splitlines()) == 1001
            assert not errors, errors
        print("Tk smoke passed: preview, both modes, background exports, completion state.")
    finally:
        app.destroy()


if __name__ == "__main__":
    main()
