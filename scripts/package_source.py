"""Create a clean GitHub-ready source ZIP without local runtimes or outputs."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parent.parent
    destination = root / "release" / "PhoneNumberGenerator-Source.zip"
    destination.parent.mkdir(exist_ok=True)
    roots = [root / name for name in ("src/phone_generator", "tests", "scripts", "packaging", "docs", ".github")]
    files = [root / name for name in ("README.md", "LICENSE", "CONTRIBUTING.md", "pyproject.toml", "MANIFEST.in", ".gitignore", "Start Phone Generator.bat", "Results/README.md")]
    for folder in roots:
        files.extend(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo"))
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for file in sorted(files):
            archive.write(file, Path("PhoneNumberGenerator") / file.relative_to(root))
    print(f"Created {destination.name} ({len(files)} files)")


if __name__ == "__main__":
    main()
