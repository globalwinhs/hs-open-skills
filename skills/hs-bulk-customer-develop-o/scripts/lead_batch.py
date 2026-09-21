#!/usr/bin/env python3
"""Validate, deduplicate, score, and export a batch of B2B customer leads."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def web_url(value: object, *, allow_empty: bool = False) -> bool:
    if allow_empty and (value is None or value == ""):
        return True
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def clean_text(value: object, path: str, errors: list[str], *, optional: bool = False) -> str:
    if optional and (value is None or value == ""):
        return ""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} 不能为空")
        return ""
    return value.strip()


def clean_list(value: object, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{path} 必须是数组")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        cleaned = clean_text(item, f"{path}[{index}]", errors)
        if cleaned:
            result.append(cleaned)
    return result


def score(value: object, path: str, errors: list[str]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path} 必须是 0–5 的数字")
        return 0.0
    number = float(value)
    if not 0 <= number <= 5:
        errors.append(f"{path} 必须在 0–5 之间")
    return min(5.0, max(0.0, number))


def normalized_host(url: str) -> str:
    host = urlparse(url).netloc.casefold().split(":", 1)[0]
    return host[4:] if host.startswith("www.") else host


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def contact_rows(value: object, path: str, errors: list[str]) -> list[dict]:
    if not isinstance(value, list):
        errors.append(f"{path} 必须是数组")
        return []
    result: list[dict] = []
    for index, contact in enumerate(value):
        prefix = f"{path}[{index}]"
        if not isinstance(contact, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        source_url = str(contact.get("source_url", "")).strip()
        if not web_url(source_url):
            errors.append(f"{prefix}.source_url 必须是有效网页链接")
        email = clean_text(contact.get("email"), f"{prefix}.email", errors, optional=True)
        phone = clean_text(contact.get("phone"), f"{prefix}.phone", errors, optional=True)
        if not email and not phone:
            errors.append(f"{prefix} 至少包含 email 或 phone")
        result.append(
            {
                "name": clean_text(contact.get("name"), f"{prefix}.name", errors, optional=True),
                "role": clean_text(contact.get("role"), f"{prefix}.role", errors, optional=True),
                "email": email,
                "phone": phone,
                "source_url": source_url,
            }
        )
    return result


def validate(data: object) -> tuple[dict, list[dict]]:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("输入文件顶层必须是 JSON 对象")

    campaign = data.get("campaign")
    if not isinstance(campaign, dict):
        errors.append("campaign 必须是对象")
        campaign = {}
    clean_campaign = {
        "product": clean_text(campaign.get("product"), "campaign.product", errors),
        "market": clean_text(campaign.get("market"), "campaign.market", errors),
        "customer_type": clean_text(campaign.get("customer_type"), "campaign.customer_type", errors),
        "exclusions": clean_list(campaign.get("exclusions", []), "campaign.exclusions", errors),
        "analysis_date": clean_text(data.get("analysis_date"), "analysis_date", errors),
    }

    leads = data.get("leads")
    if not isinstance(leads, list) or not leads:
        errors.append("leads 至少包含一家公司")
        leads = []
    validated: list[dict] = []
    for index, lead in enumerate(leads):
        prefix = f"leads[{index}]"
        if not isinstance(lead, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        company_name = clean_text(lead.get("company_name"), f"{prefix}.company_name", errors)
        country = clean_text(lead.get("country"), f"{prefix}.country", errors)
        website = str(lead.get("website", "")).strip()
        if not web_url(website):
            errors.append(f"{prefix}.website 必须是有效网页链接")
        customer_role = clean_text(lead.get("customer_role"), f"{prefix}.customer_role", errors)
        match_reason = clean_text(lead.get("match_reason"), f"{prefix}.match_reason", errors)

        scores = lead.get("scores")
        if not isinstance(scores, dict):
            errors.append(f"{prefix}.scores 必须是对象")
            scores = {}
        clean_scores = {
            field: score(scores.get(field), f"{prefix}.scores.{field}", errors)
            for field in ("product_match", "purchase_signal", "reachability", "risk")
        }

        sources = lead.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{prefix}.sources 至少包含一条来源")
            sources = []
        clean_sources: list[dict] = []
        for source_index, source in enumerate(sources):
            sp = f"{prefix}.sources[{source_index}]"
            if not isinstance(source, dict):
                errors.append(f"{sp} 必须是对象")
                continue
            url = str(source.get("url", "")).strip()
            if not web_url(url):
                errors.append(f"{sp}.url 必须是有效网页链接")
            clean_sources.append(
                {
                    "title": clean_text(source.get("title"), f"{sp}.title", errors),
                    "url": url,
                    "supports": clean_text(source.get("supports"), f"{sp}.supports", errors),
                }
            )

        contacts = contact_rows(lead.get("contacts", []), f"{prefix}.contacts", errors)
        unknowns = clean_list(lead.get("unknowns", []), f"{prefix}.unknowns", errors)
        outreach_angle = clean_text(
            lead.get("outreach_angle"), f"{prefix}.outreach_angle", errors, optional=True
        )
        composite = (
            clean_scores["product_match"] * 0.45
            + clean_scores["purchase_signal"] * 0.30
            + clean_scores["reachability"] * 0.20
            + (5 - clean_scores["risk"]) * 0.05
        ) * 20
        if composite >= 75 and clean_scores["risk"] <= 3:
            priority = "A"
        elif composite >= 55 and clean_scores["risk"] <= 4:
            priority = "B"
        else:
            priority = "C"
        validated.append(
            {
                "company_name": company_name,
                "country": country,
                "website": website,
                "customer_role": customer_role,
                "match_reason": match_reason,
                "scores": clean_scores,
                "composite_score": round(composite, 1),
                "priority": priority,
                "contacts": contacts,
                "sources": clean_sources,
                "unknowns": unknowns,
                "outreach_angle": outreach_angle,
                "source_index": index,
            }
        )

    if errors:
        raise ValueError("输入校验失败：\n- " + "\n- ".join(errors))
    return clean_campaign, validated


def deduplicate(leads: list[dict]) -> tuple[list[dict], list[dict]]:
    kept: dict[str, dict] = {}
    removed: list[dict] = []
    for lead in leads:
        host = normalized_host(lead["website"])
        key = f"domain:{host}" if host else f"name:{normalized_name(lead['company_name'])}:{lead['country'].casefold()}"
        existing = kept.get(key)
        if existing is None:
            kept[key] = lead
            continue
        better = max((existing, lead), key=lambda item: (item["composite_score"], -item["source_index"]))
        worse = lead if better is existing else existing
        kept[key] = better
        removed.append(
            {
                "removed": worse["company_name"],
                "kept": better["company_name"],
                "reason": f"相同官网域名：{host}" if host else "公司名称与国家相同",
            }
        )
    result = sorted(
        kept.values(),
        key=lambda item: ({"A": 0, "B": 1, "C": 2}[item["priority"]], -item["composite_score"], item["company_name"]),
    )
    return result, removed


def join_contacts(contacts: list[dict], field: str) -> str:
    return " | ".join(item[field] for item in contacts if item[field])


def write_leads(path: Path, leads: list[dict]) -> None:
    fields = [
        "priority",
        "composite_score",
        "company_name",
        "country",
        "website",
        "customer_role",
        "match_reason",
        "product_match",
        "purchase_signal",
        "reachability",
        "risk",
        "contact_names",
        "contact_roles",
        "emails",
        "phones",
        "contact_sources",
        "evidence_sources",
        "unknowns",
        "outreach_angle",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for lead in leads:
            writer.writerow(
                {
                    "priority": lead["priority"],
                    "composite_score": lead["composite_score"],
                    "company_name": lead["company_name"],
                    "country": lead["country"],
                    "website": lead["website"],
                    "customer_role": lead["customer_role"],
                    "match_reason": lead["match_reason"],
                    **lead["scores"],
                    "contact_names": join_contacts(lead["contacts"], "name"),
                    "contact_roles": join_contacts(lead["contacts"], "role"),
                    "emails": join_contacts(lead["contacts"], "email"),
                    "phones": join_contacts(lead["contacts"], "phone"),
                    "contact_sources": join_contacts(lead["contacts"], "source_url"),
                    "evidence_sources": " | ".join(item["url"] for item in lead["sources"]),
                    "unknowns": " | ".join(lead["unknowns"]),
                    "outreach_angle": lead["outreach_angle"],
                }
            )


def build_summary(campaign: dict, leads: list[dict], duplicates: list[dict]) -> str:
    count = {grade: sum(lead["priority"] == grade for lead in leads) for grade in "ABC"}
    lines = [
        f"# {campaign['product']}｜{campaign['market']} 批量客户开发摘要",
        "",
        f"分析日期：{campaign['analysis_date']}",
        f"目标客户类型：{campaign['customer_type']}",
        f"有效客户数：{len(leads)}（A 级 {count['A']}；B 级 {count['B']}；C 级 {count['C']}）",
        f"去重记录数：{len(duplicates)}",
        "",
        "## 优先跟进",
        "",
        "| 优先级 | 公司 | 综合分 | 匹配理由 | 联系切入点 |",
        "|---|---|---:|---|---|",
    ]
    for lead in leads:
        reason = lead["match_reason"].replace("|", "\\|")
        angle = (lead["outreach_angle"] or "根据公开业务信息人工制定").replace("|", "\\|")
        lines.append(
            f"| {lead['priority']} | [{lead['company_name']}]({lead['website']}) | "
            f"{lead['composite_score']:.1f} | {reason} | {angle} |"
        )

    lines.extend(["", "## 纳入与排除边界", "", "排除条件："])
    if campaign["exclusions"]:
        lines.extend(f"- {item}" for item in campaign["exclusions"])
    else:
        lines.append("- 未提供额外排除条件。")

    lines.extend(["", "## 去重记录", ""])
    if duplicates:
        lines.extend(
            f"- 移除 `{item['removed']}`，保留 `{item['kept']}`；{item['reason']}。" for item in duplicates
        )
    else:
        lines.append("- 未发现重复记录。")

    lines.extend(
        [
            "",
            "## 评分说明",
            "",
            "优先级综合考虑产品匹配、公开采购信号、联系可达性和风险。它只用于安排销售跟进顺序，不代表客户已经确认采购。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 JSON lead file")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output directory")
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        campaign, candidates = validate(raw)
        leads, duplicates = deduplicate(candidates)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        write_leads(args.out_dir / "customer-leads.csv", leads)
        (args.out_dir / "batch-summary.md").write_text(
            build_summary(campaign, leads, duplicates), encoding="utf-8"
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"已生成：{args.out_dir / 'customer-leads.csv'}")
    print(f"已生成：{args.out_dir / 'batch-summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
