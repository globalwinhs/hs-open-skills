#!/usr/bin/env python3
"""Validate and store a local, per-user skill profile."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_NAME = Path(__file__).resolve().parents[1].name
REQUIRED_SECTIONS = {
    "lc-expert-skill-2-o": {"company", "banking", "commercial_policy", "shipping", "documents", "risk_policy", "delivery"},
    "hs-target-market-analyze-o": {"product", "ideal_customers", "market_preferences"},
    "hs-bulk-customer-develop-o": {"product", "ideal_customer", "campaign_defaults"},
    "hs-customer-background-servey-o": {"seller_product", "risk_policy", "market_focus"},
}
SENSITIVE_KEY = re.compile(r"(?:password|passwd|secret|token|api[_-]?key|private[_-]?key|credential)", re.I)
MAX_BYTES = 256 * 1024


def data_root() -> Path:
    override = os.environ.get("OPEN_TRADE_SKILLS_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", "").strip()
        return Path(base) / "OpenTradeSkills" if base else Path.home() / "AppData" / "Local" / "OpenTradeSkills"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "OpenTradeSkills"
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    return (Path(xdg).expanduser() if xdg else Path.home() / ".config") / "open-trade-skills"


def profile_path() -> Path:
    return data_root() / SKILL_NAME / "profile.json"


def contains_sensitive_key(value: object, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if SENSITIVE_KEY.search(str(key)):
                hits.append(child_path)
            hits.extend(contains_sensitive_key(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(contains_sensitive_key(child, f"{path}[{index}]"))
    return hits


def load_input(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("配置文件过大；企业档案不得包含客户文件或业务附件")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("配置顶层必须是 JSON 对象")
    data.pop("_meta", None)
    required = REQUIRED_SECTIONS.get(SKILL_NAME)
    if required is None:
        raise ValueError(f"未知 Skill：{SKILL_NAME}")
    missing = sorted(required - set(data))
    unknown = sorted(set(data) - required)
    if missing:
        raise ValueError("缺少顶层字段：" + ", ".join(missing))
    if unknown:
        raise ValueError("存在未定义顶层字段：" + ", ".join(unknown))
    for section in required:
        if not isinstance(data[section], dict):
            raise ValueError(f"{section} 必须是 JSON 对象")
    sensitive = contains_sensitive_key(data)
    if sensitive:
        raise ValueError("配置中禁止保存凭证字段：" + ", ".join(sensitive))
    return data


def cmd_show() -> int:
    path = profile_path()
    if not path.exists():
        print(json.dumps({"status": "missing", "path": str(path)}, ensure_ascii=False, indent=2))
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"配置无法读取：{exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "ready", "path": str(path), "profile": data}, ensure_ascii=False, indent=2))
    return 0


def cmd_validate(input_path: Path) -> int:
    try:
        load_input(input_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"配置校验失败：{exc}", file=sys.stderr)
        return 2
    print("配置校验通过")
    return 0


def cmd_save(input_path: Path, confirmed: bool) -> int:
    if not confirmed:
        print("拒绝写入：请先向用户展示配置内容和保存路径，获得确认后加 --confirm", file=sys.stderr)
        return 2
    try:
        data = load_input(input_path)
        target = profile_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            **data,
            "_meta": {
                "skill": SKILL_NAME,
                "profile_version": 1,
                "saved_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if os.name != "nt":
            temporary.chmod(0o600)
        os.replace(temporary, target)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"配置保存失败：{exc}", file=sys.stderr)
        return 2
    print(f"已保存：{target}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("path", help="显示配置保存路径")
    subparsers.add_parser("show", help="显示当前配置；不存在时返回保存路径")
    validate_parser = subparsers.add_parser("validate", help="校验配置但不写入")
    validate_parser.add_argument("--input", required=True, type=Path)
    save_parser = subparsers.add_parser("save", help="校验并原子保存配置")
    save_parser.add_argument("--input", required=True, type=Path)
    save_parser.add_argument("--confirm", action="store_true", help="确认用户已同意本次写入")
    args = parser.parse_args()
    if args.command == "path":
        print(profile_path())
        return 0
    if args.command == "show":
        return cmd_show()
    if args.command == "validate":
        return cmd_validate(args.input)
    return cmd_save(args.input, args.confirm)


if __name__ == "__main__":
    raise SystemExit(main())

