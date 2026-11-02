import csv
import random
import tempfile
import unittest
from pathlib import Path
from threading import Event

from phone_generator.core import Cancelled, FORMATS, custom_space, export_numbers, format_number, nanp_space, prefix_space


class GenerationTests(unittest.TestCase):
    def test_arbitrary_start_examples(self):
        for prefix in ("12067745", "20677456", "2063327", "0", "12345678901234567890"):
            with self.subTest(prefix=prefix):
                numbers = list(prefix_space(prefix, 3).sample(50))
                self.assertEqual(len(set(numbers)), 50)
                self.assertTrue(all(n.startswith(prefix) and len(n) == len(prefix) + 3 for n in numbers))

    def test_hyphenated_starts_deduplicate_and_allow_different_lengths(self):
        space = prefix_space("206-332-7,2063327;12067745\n20677456", 2)
        self.assertEqual(space.capacity, 300)
        numbers = list(space.sample(300))
        self.assertEqual(len(set(numbers)), 300)
        self.assertIn("206332700", numbers)
        self.assertIn("1206774500", numbers)
        with self.assertRaises(ValueError):
            list(space.sample(301))

    def test_prefix_zero_remaining_and_validation(self):
        self.assertEqual(set(prefix_space("206-332-7 2063327 12067745", 0).sample(2)), {"2063327", "12067745"})
        for entry in ("", "abc", "206--332", "-206", "206-", "+1206", "２０６"):
            with self.subTest(entry=entry), self.assertRaises(ValueError):
                prefix_space(entry, 3)
        for remaining in (-1, 1001):
            with self.assertRaises(ValueError):
                prefix_space("206", remaining)

    def test_mixed_entries_normalize_and_remove_overlap(self):
        space = nanp_space("206, 206-234; 425-234\n425234 206")
        self.assertEqual([b.prefix for b in space.blocks], ["1206", "1425234"])
        self.assertEqual(space.capacity, 7_930_000)

    def test_full_exchange_has_no_duplicates_and_keeps_zeroes(self):
        numbers = list(nanp_space("206-234").sample(10_000, random.Random(3)))
        self.assertEqual(len(set(numbers)), 10_000)
        self.assertEqual(set(numbers), {f"1206234{i:04d}" for i in range(10_000)})

    def test_area_generation_excludes_n11_and_invalid_exchanges(self):
        for n in nanp_space("206,425").sample(20_000):
            self.assertIn(n[1:4], ("206", "425"))
            self.assertIn(n[4], "23456789")
            self.assertNotEqual(n[5:7], "11")
            self.assertEqual(len(n), 11)

    def test_invalid_inputs(self):
        for text in ("", "123", "206-111", "211", "206-911", "2062345", "206-23", "２０６", "abc"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                nanp_space(text)
        for count in (0, -1, 10_001, 1_000_001):
            with self.subTest(count=count), self.assertRaises(ValueError):
                list(nanp_space("206-234").sample(count))

    def test_custom_prefixes(self):
        space = custom_space("+44", "7700 7701 7700", 6)
        self.assertEqual(space.capacity, 2_000_000)
        for n in space.sample(100):
            self.assertTrue(n.startswith(("447700", "447701")))
            self.assertEqual(len(n), 12)
        for args in (("0", "77", 6), ("44", "77 770", 6), ("44", "77", 14), ("44", "", 6)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                custom_space(*args)

    def test_formats(self):
        n = "12062340000"
        self.assertEqual([format_number(n, style) for style in FORMATS], ["+12062340000", n, "2062340000", "(206) 234-0000"])
        with self.assertRaises(ValueError):
            format_number("447700000000", FORMATS[2], False)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.space = nanp_space("206-234 425-234")

    def test_txt_and_csv(self):
        for suffix in ("txt", "csv"):
            path = self.folder / f"numbers.{suffix}"
            progress = []
            export_numbers(self.space, 101, path, progress=progress.append)
            with path.open(newline="") as handle:
                rows = list(csv.reader(handle))
            if suffix == "csv":
                self.assertEqual(rows.pop(0), ["phone_number"])
            self.assertEqual(len(rows), 101)
            self.assertEqual(len({r[0] for r in rows}), 101)
            self.assertEqual(progress, [101])

    def test_existing_file_preserved_and_explicit_replace(self):
        path = self.folder / "numbers.txt"
        path.write_text("original")
        with self.assertRaises(FileExistsError):
            export_numbers(self.space, 10, path)
        self.assertEqual(path.read_text(), "original")
        export_numbers(self.space, 10, path, overwrite=True)
        self.assertEqual(len(path.read_text().splitlines()), 10)

    def test_cancel_mid_export_preserves_existing_file_and_cleans_temp(self):
        path = self.folder / "numbers.txt"
        path.write_text("original")
        cancel = Event()
        with self.assertRaises(Cancelled):
            export_numbers(self.space, 5000, path, overwrite=True, cancel=cancel, progress=lambda _: cancel.set())
        self.assertEqual(path.read_text(), "original")
        self.assertEqual(list(self.folder.iterdir()), [path])

    def test_racing_file_creation_does_not_overwrite(self):
        path = self.folder / "race.txt"
        with self.assertRaises(FileExistsError):
            export_numbers(self.space, 10, path, progress=lambda _: path.write_text("other writer"))
        self.assertEqual(path.read_text(), "other writer")
        self.assertEqual(list(self.folder.iterdir()), [path])

    def test_bad_extension_does_not_write(self):
        with self.assertRaises(ValueError):
            export_numbers(self.space, 10, self.folder / "numbers.xlsx")
        self.assertEqual(list(self.folder.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
