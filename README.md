# Phone Leads Generation GUI

A free, offline desktop utility for creating phone number **candidates** for lookup workflows. Paste your ranges, choose how many numbers you want, and save a TXT or CSV file. No account, API key, or Python installation is needed for the Windows portable app or installer.

## Get started on Windows

Download a package from this repository's **Releases** section when its owner publishes a release:

- **Setup:** run `PhoneNumberGenerator-Windows-Setup.exe`, then open Phone Number Generator from the Start menu. Installs for your user without administrator rights; uninstall through Windows Settings.
- **Portable:** extract `PhoneNumberGenerator-Windows-Portable.zip` completely, open its folder, and double-click `PhoneNumberGenerator.exe`. Keep the `_internal` folder beside the executable.

Windows 10/11 x64 is the intended distribution target. Packages are unsigned unless the distributor signs them. Check the release publisher and SHA256 checksum before running downloaded software. Signing instructions are in [the release guide](docs/RELEASING.md).

## Make your first list

1. Keep **North America (+1)** selected.
2. Enter area codes, area code / exchange pairs, or both:

   ```text
   206, 425
   503-234, 503-235
   ```

3. Enter the **total** number of results, such as `1000`. This is the total across all ranges, not a quantity per range.
4. Choose a number format. **International** adds the `+1` country code and is the default.
5. Optionally click **Preview sample**, then click **Generate & save**. Choose `.txt` for one number per line or `.csv` for a `phone_number` column.

Commas, spaces, semicolons, and new lines separate entries. Both `206-234` and `206234` work. Repeated entries are removed. An area code already includes all its exchanges, so entering `206, 206-234` does not give exchange 234 extra weight. A complete NPA-NXX pair has 10,000 candidate numbers, including suffix `0000`.

Every export contains unique numbers. Separate exports can overlap. Selection is random across all possible numbers in the ranges: a whole area code contributes more candidates than one exchange. Preview is a separate random sample, not the beginning of your saved list. Each export supports up to 1,000,000 numbers. The app remains responsive, shows progress, and allows cancellation. Existing files are replaced only after confirmation and successful completion; cancellation discards temporary output.

The **Save folder** field remembers your destination between launches. Enter a
folder or use **Browse**. Choosing another folder in the Save dialog updates it
too. Preferences are stored locally per Windows user at
`%LOCALAPPDATA%\PhoneNumberGenerator\settings.json`, so they survive app upgrades.
If a saved folder is unavailable, choose an existing folder before exporting.

## Any starting digits

Select **Any starting digits**, paste the exact starts you want, and answer
**How many digits remain?** The app appends that many random digits without
adding or removing a country code. Hyphens inside an entry are ignored.

| Starting digits | Digits remaining | Quantity | Result |
| --- | --- | --- | --- |
| `12067745` | `3` | `50` | 50 unique numbers matching `12067745XXX` |
| `20677456` | `2` | `50` | 50 unique numbers matching `20677456XX` |
| `206-332-7` or `2063327` | `3` | `50` | 50 unique numbers matching `2063327XXX` |

Multiple starts may have different lengths and can be separated by commas,
spaces, semicolons, or new lines. Duplicate starts are removed after stripping
hyphens. Leading zeroes are preserved. Output is digits only, exactly as entered
plus the requested suffix. Choose 0 remaining digits to export the unique starts
themselves. Up to 1,000 remaining digits are supported; this mode creates literal
digit combinations and does not enforce phone-number length or allocation rules.
One start with 2 remaining digits offers only 100 unique combinations, so a request
for more than 100 is rejected rather than repeating numbers.

## Custom international mode

Choose **Custom international**, supply the country calling code (for example `44`), enter same-length prefixes without country code or domestic trunk zero (for example `7700, 7701`), and set the number of random remaining digits (for example `6`). This produces `+447700XXXXXX` or `+447701XXXXXX`. Choose international or digits-only output. This mode checks input shape and the 15-digit maximum, not country-specific allocation rules.

## What generation means

This app creates combinations; it does **not** confirm assignment, activity, carrier, mobile status, reachability, or consent, and it does not perform any sort of phone number validation or contact any generated number. There is no bundled allocation database that can go stale. North American mode checks the basic NPA/NXX structure and excludes N11 service codes; other reserved or unassigned ranges can still appear. Use explicit NPA-NXX inputs from a current data source when you need a narrower candidate set.

NANPA documents the [NPA-NXX structure](https://www.nanpa.com/numbering/co-codesthousands-blocks) and publishes [CO code assignment records](https://www.nanpa.com/reports/co-code-reports/cocodes_assign). Assignment records and a generated candidate are not proof that an individual number is active.

CSV contains literal phone strings. Spreadsheet programs may interpret a leading `+` or long digits as numeric values. When opening in Excel, import the column as **Text** to preserve it.

## Find number ranges and carriers with NANPA

The public [NANPA Thousands-Block Report](https://secure.nanpa.com/public-report/tbco/thousands-block) helps you find which phone companies have been assigned groups of numbers. NANPA is the **North American Numbering Plan Administrator**, which manages numbering resources. The report opens in your browser and requires JavaScript.

Think of phone numbers as **address labels handed out to phone companies in packs**. A six-digit area-code/prefix combination covers 10,000 numbers. Dividing it into smaller packs of 1,000 lets companies receive smaller allocations, helping conserve numbers. Different packs under the same prefix can belong to different companies.

### Read a row without the jargon

Here is an **illustrative example**, not a claim about a real carrier assignment:

| Report term | Example | Plain meaning |
| --- | --- | --- |
| **NPA** | `206` | The area code. |
| **NXX** | `332` | The next three digits, often called the prefix or exchange. |
| **Block** | `7` | The next digit, identifying one pack of 1,000 numbers. |
| **Company / carrier** | A phone company name | The company listed as holding that pack. |

Together, `206-332-7` means **206-332-7000 through 206-332-7999**. The final three digits run from `000` to `999`. A neighboring block, such as `206-332-8`, may be held by another company, so checking only `206-332` can miss that distinction.

When using the report, narrow your search to the area you want and read the **NPA, NXX, block, and company together**. If you also see **OCN**, it is a company identifier; **rate center** means a telephone calling area, not a person's precise location. Assignment/effective dates describe the block allocation, not when an individual customer activated a phone.

### Use a block in this generator

For the example above, select **Any starting digits**, enter `206-332-7` or `2063327`, set **How many digits remain?** to `3`, and request up to **1,000 unique numbers**. To include country code `1`, enter `12063327` instead. This selects the smaller block rather than the entire 10,000-number prefix.

The report is an **allocation directory**, not a list of subscribers. An assigned or retained block does not mean every number in it is active. People can also keep their numbers when switching carriers, so the listed block holder may differ from a particular number's current carrier. NANPA explains this distinction in its [carrier-identification guide](https://www.nanpa.com/sites/default/files/2024-10/InstructionsForLawEnforcement.pdf); the [NPAC glossary](https://www.npac.com/resources/public-knowledgebase/glossary) also defines thousand-number blocks and their holders.

## Run from source

Install Python **3.11 or newer** with Tcl/Tk. The project uses the standard library at runtime; no third-party GUI dependency is required. On Windows, the python.org installer includes Tcl/Tk when that option is selected. On Linux, install your distribution's `python3-tk` package if needed.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\phone-generator.exe
```

For source editing without reinstalling:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m phone_generator
```

Or double-click `Start Phone Generator.bat` on Windows; it uses a local packaged app when present, otherwise runs the source with Python on PATH. Other desktop platforms can run `python -m phone_generator` after installation but are not packaged here.

## Development and distribution

```powershell
python -m unittest discover -s tests -v
python scripts/smoke_gui.py
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
# Also build the installer (requires Inno Setup 6):
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -Installer
```

Install the project before running tests. The build script creates an isolated build environment and writes the portable ZIP, Python wheel/source archive, checksums, and optional setup EXE into `release/`. See [RELEASING.md](docs/RELEASING.md) for publishing and fresh-PC checks. GitHub Actions tests Python 3.11–3.14 on Windows; the package workflow runs manually or on a `v*` tag and uploads downloadable build artifacts without publishing them automatically.

```text
src/phone_generator/   GUI and generation/export logic
tests/                Input, uniqueness, formatting, file-safety tests
scripts/              Windows build and GUI smoke checks
packaging/            Executable entry point and Inno Setup installer
.github/workflows/    Compatibility tests and package builds
docs/                 Release instructions and validation notes
```

The original `phone_gen/` directory remains untouched locally and is excluded from Git and release packages. The supplied original was Python 3.9 bytecode (`gen.pyc`), with two batch launchers and a virtual environment; no original `.py` source was present. This is a readable-source replacement based on inspection of that bytecode. It improves on append-only output and permits multiple prefixes.

## Contributing

Open an issue with the app version, Windows/Python version, steps to reproduce, and a small example input. Avoid attaching customer lists or private lookup results. For code changes, include a focused test for changed generation or export behavior and run the checks above. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Validation

See [the validation record](docs/VALIDATION.md) for completed tests and remaining fresh-PC release checks. The clean `PhoneNumberGenerator-Source.zip` in `release/` is suitable for uploading the source to GitHub; it excludes local runtimes and output.

## License

[MIT](LICENSE). Free to use, modify, and redistribute, including with a commercial service.
