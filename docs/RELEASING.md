# Building and sharing a release

1. Update the matching versions in `pyproject.toml`, `src/phone_generator/__init__.py`, and `packaging/windows.iss`.
2. On Windows x64 with Python 3.11+ and optional Inno Setup 6, run `scripts/build_windows.ps1 -Installer` from PowerShell. This downloads build dependencies into `.venv-build` and builds locally. Omit `-Installer` for a portable-only build. PyInstaller packages must be built on the target operating system: [official usage guide](https://pyinstaller.org/en/stable/usage.html).
3. Alternatively, upload the source to GitHub, open Actions → Build Windows packages → Run workflow, and download its artifact. The Windows runner must include Inno Setup 6. The workflow also runs on `v*` tags.
4. Inspect the portable ZIP: it must contain the executable, `_internal`, README, LICENSE, and `Results/README.md`. Results must contain no generated lists. Test after extraction into a different directory, including a path containing spaces. Check the Results default with fresh user preferences and confirm a previously saved destination still wins. Do not distribute just the executable from this directory build.
5. On a fresh Windows 10/11 x64 machine without Python, test portable launch, setup install without admin, Start menu launch, uninstall, both number modes, preview, bad input, TXT and CSV, overwrite refusal/approval, and cancellation of a large export. Test 100%, 125%, 150%, and 200% display scaling. The local development machine cannot prove fresh-PC compatibility.
6. If you have a code-signing certificate, sign the app EXE before compiling the setup, then sign the setup. Never commit private signing keys. Regenerate `SHA256SUMS.txt` after signing. Unsigned builds can trigger publisher/reputation warnings; do not instruct customers to disable security controls.
7. Create a GitHub release, attach the portable ZIP, setup EXE, and SHA256SUMS. Optionally attach the Python wheel and source archive. Include the version, supported platforms, changes, and validation results. The workflows build artifacts but deliberately do not publish a release.

## First upload

Create an empty repository on GitHub. From this project directory:

```powershell
git init
git add .
git status
git commit -m "Add desktop phone number generator"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the example repository URL with your own. Inspect `git status` before committing; the original virtual environment, generated output, and build folders should be ignored. No repository, commit, push, or public release is created by the local rebuild itself.
