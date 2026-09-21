#!/usr/bin/env python3
"""Validate market evidence and build a ranked Markdown/CSV delivery."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


WEIGHTS = {
    "demand": 0.30,
    "product_fit": 0.25,
    "market_access": 0.15,
    "channel_access": 0.15,
    "competitive_opportunity": 0.10,
}
REQUIRED_MARKET_LISTS = (
    "customer_types",
    "reasons",
    "barriers",
    "unknowns",
    "next_actions",
)


def is_web_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def score_value(value: object, path: str, errors: list[str]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path} 必须是 0–5 的数字")
        return 0.0
    number = float(value)
    if not 0 <= number <= 5:
        errors.append(f"{path} 必须在 0–5 之间")
    return max(0.0, min(5.0, number))


def require_text(value: object, path: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} 不能为空")
        return ""
    return value.strip()


def require_text_list(value: object, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{path} 必须是数组")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        text = require_text(item, f"{path}[{index}]", errors)
        if text:
            result.append(text)
    return result


def validate(data: object) -> tuple[dict, list[dict]]:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("输入文件顶层必须是 JSON 对象")

    product = data.get("product")
    if not isinstance(product, dict):
        errors.append("product 必须是对象")
        product = {}
    require_text(product.get("name"), "product.name", errors)
    require_text(data.get("analysis_date"), "analysis_date", errors)

    markets = data.get("markets")
    if not isinstance(markets, list) or not markets:
        errors.append("markets 至少包含一个市场")
        markets = []

    normalized: list[dict] = []
    names: set[str] = set()
    for index, market in enumerate(markets):
        prefix = f"markets[{index}]"
        if not isinstance(market, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        name = require_text(market.get("name"), f"{prefix}.name", errors)
        key = name.casefold()
        if key and key in names:
            errors.append(f"{prefix}.name 与其他市场重复：{name}")
        names.add(key)

        scores = market.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{prefix}.scores 必须是对象")
            scores = {}
        clean_scores = {
            field: score_value(scores.get(field), f"{prefix}.scores.{field}", errors)
            for field in (*WEIGHTS, "risk")
        }

        lists = {
            field: require_text_list(market.get(field), f"{prefix}.{field}", errors)
            for field in REQUIRED_MARKET_LISTS
        }
        for field in ("customer_types", "reasons", "next_actions"):
            if not lists[field]:
                errors.append(f"{prefix}.{field} 至少包含一项")

        evidence = market.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 2:
            errors.append(f"{prefix}.evidence 至少包含两条来源")
            evidence = evidence if isinstance(evidence, list) else []
        clean_evidence: list[dict] = []
        for evidence_index, item in enumerate(evidence):
            ep = f"{prefix}.evidence[{evidence_index}]"
            if not isinstance(item, dict):
                errors.append(f"{ep} 必须是对象")
                continue
            title = require_text(item.get("title"), f"{ep}.title", errors)
            url = item.get("url")
            if not is_web_url(url):
                errors.append(f"{ep}.url 必须是 http 或 https 链接")
                url = ""
            supports = require_text(item.get("supports"), f"{ep}.supports", errors)
            published_at = str(item.get("published_at", "")).strip()
            clean_evidence.append(
                {"title": title, "url": url, "supports": supports, "published_at": published_at}
            )

        weighted = sum(clean_scores[field] * weight for field, weight in WEIGHTS.items())
        weighted += (5 - clean_scores["risk"]) * 0.05
        normalized.append(
            {
                "name": name,
                "scores": clean_scores,
                "weighted_score": round(weighted * 20, 1),
                "evidence": clean_evidence,
                **lists,
            }
        )

    if errors:
        raise ValueError("输入校验失败：\n- " + "\n- ".join(errors))
    normalized.sort(key=lambda item: (-item["weighted_score"], item["name"]))
    return product, normalized


def bullets(items: list[str], empty: str = "未记录") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def build_markdown(product: dict, analysis_date: str, markets: list[dict]) -> str:
    lines = [
        f"# {product['name']} 目标市场分析",
        "",
        f"分析日期：{analysis_date}",
        "",
        "## 市场排序",
        "",
        "| 排名 | 市场 | 综合分 | 需求 | 产品匹配 | 准入 | 渠道 | 竞争机会 | 风险 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, market in enumerate(markets, 1):
        score = market["scores"]
        lines.append(
            f"| {rank} | {market['name']} | {market['weighted_score']:.1f} | "
            f"{score['demand']:g} | {score['product_fit']:g} | {score['market_access']:g} | "
            f"{score['channel_access']:g} | {score['competitive_opportunity']:g} | {score['risk']:g} |"
        )

    for rank, market in enumerate(markets, 1):
        lines.extend(
            [
                "",
                f"## {rank}. {market['name']}",
                "",
                f"综合分：{market['weighted_score']:.1f}/100",
                "",
                "适合开发的客户类型：",
                bullets(market["customer_types"]),
                "",
                "优先理由：",
                bullets(market["reasons"]),
                "",
                "主要障碍：",
                bullets(market["barriers"]),
                "",
                "待验证事项：",
                bullets(market["unknowns"]),
                "",
                "下一步：",
                bullets(market["next_actions"]),
                "",
                "证据：",
            ]
        )
        for item in market["evidence"]:
            date_note = f"，{item['published_at']}" if item["published_at"] else ""
            lines.append(f"- [{item['title']}]({item['url']}){date_note}：{item['supports']}")

    lines.extend(
        [
            "",
            "## 评分说明",
            "",
            "综合分用于候选市场的相对比较，由需求、产品匹配、准入、渠道、竞争机会和风险组成；它不是销量或成交概率预测。",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(path: Path, markets: list[dict]) -> None:
    fields = [
        "rank",
        "market",
        "weighted_score",
        "demand",
        "product_fit",
        "market_access",
        "channel_access",
        "competitive_opportunity",
        "risk",
        "customer_types",
        "next_actions",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rank, market in enumerate(markets, 1):
            writer.writerow(
                {
                    "rank": rank,
                    "market": market["name"],
                    "weighted_score": market["weighted_score"],
                    **market["scores"],
                    "customer_types": " | ".join(market["customer_types"]),
                    "next_actions": " | ".join(market["next_actions"]),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 JSON evidence file")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output directory")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        product, markets = validate(data)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        report = build_markdown(product, str(data["analysis_date"]), markets)
        (args.out_dir / "market-analysis.md").write_text(report, encoding="utf-8")
        write_csv(args.out_dir / "market-ranking.csv", markets)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"已生成：{args.out_dir / 'market-analysis.md'}")
    print(f"已生成：{args.out_dir / 'market-ranking.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
