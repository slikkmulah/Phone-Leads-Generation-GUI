# Contributing

Use Python 3.11 or newer and install the project in a virtual environment with `python -m pip install -e .`. Keep the runtime dependency-free unless a new dependency materially improves the user experience.

Generation, parsing, and export code belongs in `src/phone_generator/core.py`; Tk widgets belong in `gui.py`. Worker threads must not access Tk. Export changes must preserve cancellation cleanup, duplicate prevention, and existing-file safety.

Before submitting a pull request, run `python -m unittest discover -s tests -v` and `python scripts/smoke_gui.py`. For UI changes, also open the app and check both modes, keyboard navigation, validation errors, a TXT/CSV save, cancellation, and display scaling.

Do not commit virtual environments, build output, generated number lists, customer data, or the legacy `phone_gen/` directory. Describe what changed and how you tested it.

For a packaged executable on a PC without Python, run `PhoneNumberGenerator.exe --self-test C:\Path\To\New-Test-Folder`. The folder must not already exist. This maintainer mode drives the actual GUI callbacks and background worker, writes synthetic exports and a JSON report, and returns a process exit code. It supplies file/message dialogs through the harness; manually inspect native dialogs and visual layout separately. The Windows build script runs it automatically before packaging.
