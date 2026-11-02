# Windows VM package test results

Completed for version **1.0.0** on 2026-10-21 against Windows 11 Enterprise Evaluation, build 26300, x64. These results do not cover later builds. The VM used 4 virtual CPUs, 4–8 GB RAM, Secure Boot, and a virtual TPM. No external Python installation was present. A clean checkpoint was retained before testing.

## Passed

- Extract the portable ZIP into a path containing spaces.
- Launch the portable application normally in the interactive Windows desktop session.
- Run the frozen executable's diagnostic mode: preview; 1,000 distinct TXT and CSV rows; mixed area-code/NPA-NXX ranges; international prefixes; invalid-input errors; overwrite refusal and replacement; cancellation preserving an existing file; temporary-file cleanup.
- Install with the per-user installer in silent mode, with exit code 0.
- Verify the per-user uninstall registration and the Start menu shortcut's target.
- Run the same frozen diagnostics against the installed executable and launch its normal GUI in the interactive desktop session.
- Uninstall silently with exit code 0. Verify removal of the installed executable, uninstall registration, and Start menu shortcut.

## Tested packages

| Package | SHA-256 |
| --- | --- |
| `PhoneNumberGenerator-Windows-Portable.zip` | `0f84b5212cf8b46c7bb2302b8855a768b59d46c9e22f0e23879a7d513ea288c1` |
| `PhoneNumberGenerator-Windows-Setup.exe` | `046e8e2c51005ee445c67132ce45c55e9e1c90eb6b372a6a5ca1e6ac6abdaff0` |

These hashes identify the packages tested locally; they do not represent signed or publicly published releases. Check the current `SHA256SUMS.txt` when sharing packages.

## Limits of the checks

The diagnostic harness creates real Tk widgets and invokes the application's actual callbacks and background worker. It supplies file/message dialog responses, so it does not verify manual interaction with native Save dialogs. Normal window launch was checked separately by observing the expected window title in the interactive guest session; that is not a visual-layout or accessibility test.

Installer/uninstaller checks used silent mode. Manual wizard interaction, display scaling, screen readers, Windows 10, and other Windows versions/physical machines remain review work. No generated numbers were contacted, and no HLR or carrier lookups were performed.
