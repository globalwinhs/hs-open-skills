#!/usr/bin/env python3
"""Validate target-market analysis input without generating deliverables."""

import argparse
import json
import sys
from pathlib import Path

from market_report import validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        _, markets = validate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"校验通过：{len(markets)} 个市场")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

