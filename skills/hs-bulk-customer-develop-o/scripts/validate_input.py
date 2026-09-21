#!/usr/bin/env python3
"""Validate bulk customer-development input without creating exports."""

import argparse
import json
import sys
from pathlib import Path

from lead_batch import validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        _, leads = validate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"校验通过：{len(leads)} 条候选客户")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
