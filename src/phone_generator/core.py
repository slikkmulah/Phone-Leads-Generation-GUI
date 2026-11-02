"""Number spaces, unique random sampling, and transactional exports."""

from __future__ import annotations

import bisect
import csv
import os
import random
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from typing import Callable, Iterator

MAX_COUNT = 1_000_000
FORMATS = ("International (+12062340000)", "Digits only (12062340000)", "10 digits (2062340000)", "Formatted ((206) 234-0000)")
NXX_CODES = tuple(str(n) for n in range(200, 1000) if n % 100 != 11)


def split_entries(text: str) -> list[str]:
    return [part for part in re.split(r"[,;\s]+", text.strip()) if part]


@dataclass(frozen=True)
class Block:
    prefix: str
    remaining: int
    area_only: bool = False

    @property
    def capacity(self) -> int:
        return len(NXX_CODES) * 10_000 if self.area_only else 10**self.remaining

    def number(self, index: int) -> str:
        if self.area_only:
            nxx, suffix = divmod(index, 10_000)
            return self.prefix + NXX_CODES[nxx] + f"{suffix:04d}"
        if self.remaining == 0:
            return self.prefix
        return self.prefix + str(index).zfill(self.remaining)


@dataclass(frozen=True)
class NumberSpace:
    blocks: tuple[Block, ...]
    nanp: bool = True

    @property
    def capacity(self) -> int:
        return sum(block.capacity for block in self.blocks)

    def sample(self, count: int, rng: random.Random | None = None) -> Iterator[str]:
        if not 1 <= count <= min(MAX_COUNT, self.capacity):
            raise ValueError(f"Choose 1 to {min(MAX_COUNT, self.capacity):,} numbers.")
        rng = rng or random.SystemRandom()
        ends: list[int] = []
        total = 0
        for block in self.blocks:
            total += block.capacity
            ends.append(total)
        # Sparse Fisher-Yates avoids duplicate retries near exhaustion.
        swaps: dict[int, int] = {}
        for remaining in range(total, total - count, -1):
            chosen = rng.randrange(remaining)
            index = swaps.get(chosen, chosen)
            last = swaps.pop(remaining - 1, remaining - 1)
            if chosen != remaining - 1:
                swaps[chosen] = last
            block_index = bisect.bisect_right(ends, index)
            offset = ends[block_index - 1] if block_index else 0
            yield self.blocks[block_index].number(index - offset)


def nanp_space(text: str) -> NumberSpace:
    entries = split_entries(text)
    if not entries:
        raise ValueError("Add at least one area code or NPA-NXX pair.")
    normalized: set[str] = set()
    for entry in entries:
        if not re.fullmatch(r"(?:[2-9][0-9]{2}|[2-9][0-9]{2}-?[2-9][0-9]{2})", entry):
            raise ValueError(f"'{entry}': use 206 or 206-234 (three or six digits).")
        digits = entry.replace("-", "")
        if digits[1:3] == "11" or (len(digits) == 6 and digits[4:6] == "11"):
            raise ValueError(f"'{entry}': N11 service codes cannot be used here.")
        normalized.add(digits)
    areas = {entry for entry in normalized if len(entry) == 3}
    prefixes = sorted(entry for entry in normalized if len(entry) == 3 or entry[:3] not in areas)
    return NumberSpace(tuple(Block("1" + p, 7 if len(p) == 3 else 4, len(p) == 3) for p in prefixes))


def prefix_space(text: str, remaining: int) -> NumberSpace:
    """Append digits literally, without adding or inferring a country code."""
    if not 0 <= remaining <= 1000:
        raise ValueError("Remaining digits must be between 0 and 1000.")
    entries = split_entries(text)
    if not entries:
        raise ValueError("Enter at least one number start, such as 12067745 or 206-332-7.")
    prefixes: set[str] = set()
    for entry in entries:
        if not re.fullmatch(r"[0-9]+(?:-[0-9]+)*", entry):
            raise ValueError(f"'{entry}': use digits, optionally separated by hyphens, such as 206-332-7.")
        prefixes.add(entry.replace("-", ""))
    # Equal-length duplicates collapse; different-length starts yield different
    # output lengths and therefore cannot overlap when remaining is fixed.
    return NumberSpace(tuple(Block(p, remaining) for p in sorted(prefixes)), nanp=False)


def custom_space(country: str, text: str, remaining: int) -> NumberSpace:
    country = country.strip().removeprefix("+")
    if not re.fullmatch(r"[1-9][0-9]{0,2}", country):
        raise ValueError("Enter a country calling code of 1 to 3 digits, without a leading zero.")
    if not 1 <= remaining <= 14:
        raise ValueError("Remaining digits must be between 1 and 14.")
    prefixes = sorted(set(split_entries(text)))
    if not prefixes:
        raise ValueError("Add a prefix, such as 7700. Leave out the domestic trunk zero.")
    for prefix in prefixes:
        if not re.fullmatch(r"[0-9]+", prefix) or len(country + prefix) + remaining > 15:
            raise ValueError(f"'{prefix}': use digits only, with at most 15 digits in the complete number.")
    if len({len(prefix) for prefix in prefixes}) != 1:
        raise ValueError("Custom prefixes must all have the same length to avoid overlapping ranges.")
    return NumberSpace(tuple(Block(country + p, remaining) for p in prefixes), nanp=False)


def format_number(number: str, style: str, nanp: bool = True) -> str:
    if style not in FORMATS:
        raise ValueError("Unknown number format.")
    if style == FORMATS[0]:
        return "+" + number
    if style == FORMATS[1]:
        return number
    if not nanp:
        raise ValueError("Custom mode supports international or digits-only output.")
    national = number[1:]
    if style == FORMATS[2]:
        return national
    return f"({national[:3]}) {national[3:6]}-{national[6:]}"


class Cancelled(Exception):
    """The export was cancelled before committing its output."""


def export_numbers(space: NumberSpace, count: int, destination: Path,
                   style: str = FORMATS[0], *, overwrite: bool = False,
                   cancel: Event | None = None,
                   progress: Callable[[int], None] | None = None) -> None:
    destination = Path(destination)
    if destination.suffix.lower() not in (".txt", ".csv"):
        raise ValueError("Choose a .txt or .csv file.")
    if not 1 <= count <= min(MAX_COUNT, space.capacity):
        raise ValueError(f"Choose 1 to {min(MAX_COUNT, space.capacity):,} numbers.")
    format_number(space.blocks[0].number(0), style, space.nanp)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"{destination.name} already exists. Choose another filename.")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", prefix=".phonegen-", suffix=".tmp", dir=destination.parent, delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.writer(handle) if destination.suffix.lower() == ".csv" else None
            if writer:
                writer.writerow(["phone_number"])
            for done, number in enumerate(space.sample(count), 1):
                if cancel and cancel.is_set():
                    raise Cancelled()
                value = format_number(number, style, space.nanp)
                if writer:
                    writer.writerow([value])
                else:
                    handle.write(value + "\n")
                if progress and (done % 1000 == 0 or done == count):
                    progress(done)
            handle.flush()
            os.fsync(handle.fileno())
        if cancel and cancel.is_set():
            raise Cancelled()
        if overwrite:
            os.replace(temporary, destination)
        elif os.name == "nt":
            # Windows rename fails if the target exists, including on FAT/exFAT.
            os.rename(temporary, destination)
        else:
            # POSIX rename replaces targets, so use an exclusive hard link.
            os.link(temporary, destination)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
