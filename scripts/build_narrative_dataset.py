#!/usr/bin/env python3
"""Build reviewable narrative JSONL and provenance artifacts from HTML sources."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from core.narrative_data_pipeline import (
    NarrativeDataSanitizer,
    build_dpo_pairs,
    write_jsonl_atomic,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--dpo", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.source.is_dir():
        raise SystemExit(f"source directory does not exist: {args.source}")
    records, provenance = NarrativeDataSanitizer().process_directory(args.source)
    write_jsonl_atomic(args.dataset, records)
    write_jsonl_atomic(args.provenance, (asdict(item) for item in provenance))
    if args.dpo:
        write_jsonl_atomic(args.dpo, build_dpo_pairs(records))
    print(f"candidates_for_hitl={len(records)} audited_files={len(provenance)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
