"""Command line interface for the Word accessibility fixer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .core import audit_and_fix_docx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="word-a11y-fix",
        description="Audit and automatically fix common Word DOCX accessibility issues.",
    )
    parser.add_argument("input", type=Path, help="Path to the source .docx file.")
    parser.add_argument("output", type=Path, help="Path where the fixed .docx file will be written.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = audit_and_fix_docx(args.input, args.output, args.report)
    except Exception as exc:  # noqa: BLE001 - CLI must turn errors into readable messages.
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    print(f"Documento corretto: {result.output_path}")
    print(f"Problemi rilevati: {len(result.issues)}; correzioni applicate: {result.fixed_count}")
    if result.report_path:
        print(f"Report JSON: {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
