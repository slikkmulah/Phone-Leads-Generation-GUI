"""Maintainer checks for frozen builds on PCs without Python installed.

The GUI callbacks and worker are exercised with file/message dialogs supplied
by the harness. Native dialog interaction and visual layout remain manual checks.
"""

from __future__ import annotations

import csv
import json
import platform
import sys
import time
import traceback
from pathlib import Path
from unittest.mock import patch

from . import __version__
from .core import FORMATS
from .gui import App


def run_checks(destination: Path) -> int:
    destination = Path(destination).resolve()
    # Never run file-replacement tests in an existing user directory.
    destination.mkdir(parents=True, exist_ok=False)
    report = {"version": __version__, "platform": platform.platform(), "python": sys.version,
              "frozen": bool(getattr(sys, "frozen", False)), "checks": [], "passed": False,
              "limitation": "Native dialogs are supplied by the harness; visual/manual checks remain separate."}
    app = None
    errors: list[tuple] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            raise AssertionError(message)

    def wait_for_export() -> None:
        deadline = time.monotonic() + 30
        while app.busy and time.monotonic() < deadline:
            app.update()
            time.sleep(0.01)
        check(not app.busy, "Background export timed out")

    def configure(entries: str, mode: str = "nanp", count: int = 1000) -> None:
        app.mode.set(mode)
        app.change_mode()
        app.entries.delete("1.0", "end")
        app.entries.insert("1.0", entries)
        app.count.set(str(count))
        app.output_format.set(FORMATS[0])

    def save(path: Path, approve: bool = True, cancel: bool = False) -> None:
        with patch("phone_generator.gui.filedialog.asksaveasfilename", return_value=str(path)), \
             patch("phone_generator.gui.messagebox.askyesno", return_value=approve):
            app.save()
            if cancel:
                app.cancel()
        wait_for_export()

    try:
        app = App()
        app.withdraw()
        with patch("phone_generator.gui.messagebox.showerror", side_effect=lambda *a, **k: errors.append(a)):
            configure("206-234,425-234")
            app.preview()
            check("+1" in app.sample_box.get("1.0", "end"), "Preview did not show international numbers")
            report["checks"].append("GUI preview")
            for suffix in ("txt", "csv"):
                target = destination / f"nanp.{suffix}"
                save(target)
                if suffix == "csv":
                    with target.open(newline="", encoding="utf-8") as handle:
                        reader = csv.DictReader(handle)
                        check(reader.fieldnames == ["phone_number"], "Incorrect CSV header")
                        rows = [row["phone_number"] for row in reader]
                else:
                    rows = target.read_text(encoding="utf-8").splitlines()
                check(len(rows) == 1000 and len(set(rows)) == 1000, f"Incorrect count/duplicates in {suffix}")
                check(all(n.startswith(("+1206234", "+1425234")) and len(n) == 12 for n in rows), "Wrong NANP ranges")
                report["checks"].append(f"GUI background {suffix.upper()} export: 1000 unique numbers")

            configure("206,425,503-234")
            save(destination / "mixed.txt")
            rows = (destination / "mixed.txt").read_text().splitlines()
            check(len(rows) == 1000 and len(set(rows)) == 1000, "Mixed ranges export failed")
            check(all(n.startswith(("+1206", "+1425", "+1503234")) for n in rows), "Wrong mixed ranges")
            report["checks"].append("Mixed area-code and NPA-NXX input")

            configure("7700 7701", "custom")
            app.country.set("44")
            app.remaining.set("6")
            save(destination / "international.csv")
            with (destination / "international.csv").open(newline="") as handle:
                rows = [row["phone_number"] for row in csv.DictReader(handle)]
            check(len(rows) == 1000 and len(set(rows)) == 1000, "Custom export count/uniqueness failed")
            check(all(n.startswith(("+447700", "+447701")) and len(n) == 13 for n in rows), "Wrong custom ranges")
            report["checks"].append("Custom international GUI export")

            existing = destination / "existing.txt"
            existing.write_text("preserve this content", encoding="utf-8")
            configure("206-234")
            save(existing, approve=False)
            check(existing.read_text() == "preserve this content", "Overwrite refusal changed the file")
            save(existing)
            check(len(existing.read_text().splitlines()) == 1000, "Approved replacement failed")
            report["checks"].append("GUI overwrite refusal and approved replacement")

            existing.write_text("preserve on cancellation", encoding="utf-8")
            configure("206 425", count=1_000_000)
            save(existing, cancel=True)
            check(existing.read_text() == "preserve on cancellation", "Cancellation changed existing output")
            check(not list(destination.glob(".phonegen-*.tmp")), "Cancellation left temporary output")
            report["checks"].append("GUI cancellation and preservation of existing output")

            check(not errors, f"Unexpected GUI errors: {errors}")
            configure("123")
            app.preview()
            check(len(errors) == 1 and "Check your entries" in errors[0], "Invalid input did not show validation error")
            report["checks"].append("GUI validation error")
            report["passed"] = True
    except Exception:
        report["error"] = traceback.format_exc()
    finally:
        if app is not None:
            app.destroy()
        (destination / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["passed"] else 1
