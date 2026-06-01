#!/usr/bin/env python3
"""Run minimal preprocessing on a FOMO300K constituent dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from preprocessing.pipeline import run  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="FOMO300K minimal preprocessing")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to PTxxx dataset folder",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "preprocessed",
        help="Output root directory",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of sessions to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without writing NIfTI files",
    )
    args = parser.parse_args()

    out = run(
        input_dir=args.input.resolve(),
        output_dir=args.output.resolve(),
        limit=args.limit,
        dry_run=args.dry_run,
    )
    print(f"Done. Output: {out}")


if __name__ == "__main__":
    main()
