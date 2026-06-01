#!/usr/bin/env python3
"""Print per-dataset modality summary from mri_info.tsv."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from preprocessing.config import DATA_ROOT  # noqa: E402

SUFFIX_RE = re.compile(r"(?:^|_)([A-Za-z0-9]+)\.nii\.gz$")


def extract_modality(filename: str) -> str:
    m = SUFFIX_RE.search(filename.split("/")[-1])
    return m.group(1) if m else "unknown"


def categorize(mod: str) -> str:
    m = mod.lower()
    if m in ("t1w", "t1"):
        return "T1w"
    if m in ("mp2rage", "flash", "gre", "unit1", "t1map", "r1map"):
        return "T1-like"
    if m == "scan":
        return "scan"
    if m in ("t2w", "t2"):
        return "T2w"
    if m == "pdw":
        return "PDw"
    if m == "flair":
        return "FLAIR"
    if m == "t1c":
        return "T1c"
    if m in ("swi", "mtrmap"):
        return "SWI/MTR"
    if m in ("asl", "cbf", "m0scan", "att"):
        return "ASL/perfusion"
    if m.startswith("bval") or m == "dwi" or m == "adc":
        return "DWI"
    if m == "angio":
        return "Angio"
    return "Other"


def pt_key(name: str) -> int:
    m = re.search(r"PT(\d+)", name)
    return int(m.group(1)) if m else 999


def main() -> None:
    path = DATA_ROOT / "mri_info.tsv"
    by_pt: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with open(path) as f:
        f.readline()
        for line in f:
            parts = line.split("\t", 4)
            if len(parts) < 4:
                continue
            dataset, filename = parts[0], parts[3]
            pt = "PT030_OpenNeuro" if dataset.startswith("PT030_OpenNeuro") else dataset
            by_pt[pt][extract_modality(filename)] += 1

    print(f"{'Dataset':<40} {'Scans':>8}  Families")
    print("-" * 90)
    for pt in sorted(by_pt, key=pt_key):
        mods = by_pt[pt]
        total = sum(mods.values())
        t1w = mods.get("T1w", 0) + mods.get("T1", 0)
        families = []
        seen = set()
        for mod, cnt in sorted(mods.items(), key=lambda x: -x[1]):
            fam = categorize(mod)
            if fam not in seen:
                families.append(fam)
                seen.add(fam)
        flag = f"yes ({t1w:,})" if t1w else "no explicit T1w"
        print(f"{pt:<40} {total:>8,}  {flag} — {', '.join(families)}")


if __name__ == "__main__":
    main()
