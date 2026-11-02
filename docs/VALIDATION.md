# Local validation

## Version 1.1.1 — 2026-11-02

- 21 core/settings tests pass on Python 3.12.14, including Results directory creation, source/portable/Python-install locations, fallback when the app directory is not writable, and preservation of a saved destination.
- Source GUI smoke checks and frozen executable diagnostics pass. The diagnostics verify that a fresh GUI defaults to an existing Results directory and passes the destination field to the Save dialog, alongside the existing generation, export, persistence, overwrite, and cancellation checks.
- Windows installer and portable packages rebuilt as 1.1.1. Results contains only its explanatory README in distributed archives; generated lists are excluded from Git and source packages.
- This version has not been rerun in the clean Windows VM. Native dialogs, installer wizard interaction, display scaling, and accessibility retain the limitations documented below.

## Version 1.1.0 — 2026-11-02

- 16 core/settings tests pass on Python 3.12.14. Added tests for arbitrary starts, hyphen normalization, mixed prefix lengths, capacity limits, zero remaining digits, leading zeroes, and settings recovery/persistence.
- Source and frozen GUI diagnostics test all four requested starts (`12067745`, `20677456`, `206-332-7`, `2063327`), generating 50 distinct TXT/CSV rows for each with 3 appended digits.
- GUI checks verify restoration of both a Save-dialog-selected folder and a manually entered folder after closing/reopening. Tests use isolated configuration files rather than changing real user preferences.
- Windows installer and portable packages rebuilt as 1.1.0. Native dialog interaction, visual layout, and a fresh-VM rerun of this version have not been verified; the VM results below refer to the earlier 1.0.0 packages.

## Version 1.0.0 — 2026-10-21

## Completed

- All 11 core tests pass on CPython 3.12.10 and 3.14.7 (Windows x64).
- Tests cover mixed inputs, overlap removal, invalid input, full exchange exhaustion, zero-padded suffixes, numbering structure, custom prefixes, formats, TXT/CSV, overwrite protection, cancellation cleanup, and a competing writer creating the destination.
- Automated real-Tk checks on Python 3.12.10 pass: preview, mode switching, background generation, CSV saves in both modes, and completion state.
- A million-number TXT export produced 1,000,000 distinct rows (13,000,000 bytes) in approximately 1.8 seconds including reading/checking the result on this PC. This is an observation, not a performance guarantee.
- The complete Windows build script succeeded: PyInstaller 6.22.3 directory build, portable ZIP, Inno Setup 6.7.3 installer, wheel, and source archive.
- Portable ZIP integrity passed. The extracted app launched from a separate path containing spaces. Windows Computer Use verified range entry, a two-exchange preview, scrolling, reachable Save/status controls, and the native Save dialog.
- Source archives exclude the original `phone_gen/` directory and local build runtimes. The GitHub-ready source ZIP includes workflows, tests, build scripts, installer definition, documentation, and license.
- Fresh Windows 11 Enterprise evaluation VM (build 26300), without external Python: the portable and installed executables both passed the frozen GUI diagnostics, including preview, TXT/CSV, mixed area/prefix input, international mode, validation errors, overwrite refusal/replacement, and cancellation preserving existing output.
- Both packages launched a normal GUI window in the guest's interactive desktop session. The portable build ran from a path containing spaces.
- Per-user silent installation, the uninstall entry, Start menu shortcut target, and silent uninstall were verified. Uninstall removed the executable, registry entry, and Start menu shortcut. See [VM test results](VM-TEST-RESULTS.md).

## Remaining release checks

- A completed save through the packaged application's native Save dialog was not verified. The UI automation helper returned stale/inconsistent filename-control state; the dialog was dismissed. Source-level Tk exports passed as described above.
- Installation/uninstallation were tested silently in the Windows 11 guest; visually checking the installer wizard remains a manual review step.
- Windows 10 and additional Windows 11 versions/physical machines remain untested.
- Frozen diagnostics drive the actual GUI callbacks and worker, supplying file/message dialogs through the harness. Manual operation of native dialogs in the guest remains separate.
- The full display-scaling matrix and screen-reader accessibility remain untested. Tk supplied limited accessibility information to the inspection tool.
- Python 3.11 and 3.13 are configured in GitHub Actions but were not run locally. Python 3.14 core tests used the official embedded runtime; GUI checks used Python 3.12. GitHub workflows await repository upload.
- Packages are unsigned. Code signing and public publishing are distributor steps.

The original bytecode and batch launchers remain untouched in the local `phone_gen/` folder.
