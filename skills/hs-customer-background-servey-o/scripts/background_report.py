#!/usr/bin/env python3
"""Validate a single-company investigation and render report artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


CLAIM_STATUSES = {"verified", "probable", "unverified", "conflicting"}
RISK_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def web_url(value: object, *, allow_empty: bool = False) -> bool:
    if allow_empty and (value is None or value == ""):
        return True
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def text(value: object, path: str, errors: list[str], *, optional: bool = False) -> str:
    if optional and (value is None or value == ""):
        return ""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} 不能为空")
        return ""
    return value.strip()


def text_list(value: object, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{path} 必须是数组")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        cleaned = text(item, f"{path}[{index}]", errors)
        if cleaned:
            result.append(cleaned)
    return result


def bounded_score(value: object, path: str, errors: list[str]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path} 必须是 0–5 的数字")
        return 0.0
    score = float(value)
    if not 0 <= score <= 5:
        errors.append(f"{path} 必须在 0–5 之间")
    return min(5.0, max(0.0, score))


def validate(data: object) -> dict:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("输入文件顶层必须是 JSON 对象")

    subject = data.get("subject")
    if not isinstance(subject, dict):
        errors.append("subject 必须是对象")
        subject = {}
    company_name = text(subject.get("company_name"), "subject.company_name", errors)
    country = text(subject.get("country"), "subject.country", errors, optional=True)
    website = str(subject.get("website", "")).strip()
    if not web_url(website, allow_empty=True):
        errors.append("subject.website 必须为空或 http/https 链接")
    inquiry_email = text(subject.get("inquiry_email"), "subject.inquiry_email", errors, optional=True)
    analysis_date = text(data.get("analysis_date"), "analysis_date", errors)

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims 至少包含一条调查结论")
        claims = []
    clean_claims: list[dict] = []
    for index, claim in enumerate(claims):
        prefix = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        status = str(claim.get("status", "")).strip()
        if status not in CLAIM_STATUSES:
            errors.append(f"{prefix}.status 必须是 {', '.join(sorted(CLAIM_STATUSES))} 之一")
        source_url = str(claim.get("source_url", "")).strip()
        if status in {"verified", "probable", "conflicting"} and not web_url(source_url):
            errors.append(f"{prefix}.source_url 对于 {status} 结论必须是有效网页链接")
        elif status == "unverified" and not web_url(source_url, allow_empty=True):
            errors.append(f"{prefix}.source_url 必须为空或有效网页链接")
        clean_claims.append(
            {
                "topic": text(claim.get("topic"), f"{prefix}.topic", errors),
                "statement": text(claim.get("statement"), f"{prefix}.statement", errors),
                "status": status,
                "source_title": text(
                    claim.get("source_title"), f"{prefix}.source_title", errors, optional=status == "unverified"
                ),
                "source_url": source_url,
                "checked_at": text(claim.get("checked_at"), f"{prefix}.checked_at", errors),
            }
        )

    assessment = data.get("business_assessment")
    if not isinstance(assessment, dict):
        errors.append("business_assessment 必须是对象")
        assessment = {}
    clean_assessment = {
        "actual_business": text(
            assessment.get("actual_business"), "business_assessment.actual_business", errors
        ),
        "customer_role": text(assessment.get("customer_role"), "business_assessment.customer_role", errors),
        "product_match_score": bounded_score(
            assessment.get("product_match_score"), "business_assessment.product_match_score", errors
        ),
        "purchase_signal_score": bounded_score(
            assessment.get("purchase_signal_score"), "business_assessment.purchase_signal_score", errors
        ),
        "identity_confidence_score": bounded_score(
            assessment.get("identity_confidence_score"),
            "business_assessment.identity_confidence_score",
            errors,
        ),
        "risk_score": bounded_score(assessment.get("risk_score"), "business_assessment.risk_score", errors),
        "reasoning": text_list(assessment.get("reasoning"), "business_assessment.reasoning", errors),
    }
    if not clean_assessment["reasoning"]:
        errors.append("business_assessment.reasoning 至少包含一项")

    contacts = data.get("contacts", [])
    if not isinstance(contacts, list):
        errors.append("contacts 必须是数组")
        contacts = []
    clean_contacts: list[dict] = []
    for index, contact in enumerate(contacts):
        prefix = f"contacts[{index}]"
        if not isinstance(contact, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        source_url = str(contact.get("source_url", "")).strip()
        if not web_url(source_url):
            errors.append(f"{prefix}.source_url 必须是有效网页链接")
        email = text(contact.get("email"), f"{prefix}.email", errors, optional=True)
        phone = text(contact.get("phone"), f"{prefix}.phone", errors, optional=True)
        if not email and not phone:
            errors.append(f"{prefix} 至少包含 email 或 phone")
        clean_contacts.append(
            {
                "name": text(contact.get("name"), f"{prefix}.name", errors, optional=True),
                "role": text(contact.get("role"), f"{prefix}.role", errors, optional=True),
                "email": email,
                "phone": phone,
                "source_url": source_url,
            }
        )

    risk_flags = data.get("risk_flags", [])
    if not isinstance(risk_flags, list):
        errors.append("risk_flags 必须是数组")
        risk_flags = []
    clean_risks: list[dict] = []
    for index, risk in enumerate(risk_flags):
        prefix = f"risk_flags[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        severity = str(risk.get("severity", "")).strip()
        if severity not in RISK_LEVELS:
            errors.append(f"{prefix}.severity 必须是 {', '.join(RISK_LEVELS)} 之一")
        source_url = str(risk.get("source_url", "")).strip()
        if not web_url(source_url, allow_empty=True):
            errors.append(f"{prefix}.source_url 必须为空或有效网页链接")
        clean_risks.append(
            {
                "severity": severity,
                "issue": text(risk.get("issue"), f"{prefix}.issue", errors),
                "evidence": text(risk.get("evidence"), f"{prefix}.evidence", errors),
                "source_url": source_url,
            }
        )

    unknowns = text_list(data.get("unknowns", []), "unknowns", errors)
    actions = text_list(data.get("recommended_actions"), "recommended_actions", errors)
    if not actions:
        errors.append("recommended_actions 至少包含一项")
    if errors:
        raise ValueError("输入校验失败：\n- " + "\n- ".join(errors))

    return {
        "subject": {
            "company_name": company_name,
            "country": country,
            "website": website,
            "inquiry_email": inquiry_email,
        },
        "analysis_date": analysis_date,
        "claims": clean_claims,
        "business_assessment": clean_assessment,
        "contacts": clean_contacts,
        "risk_flags": sorted(clean_risks, key=lambda item: -RISK_LEVELS[item["severity"]]),
        "unknowns": unknowns,
        "recommended_actions": actions,
    }


def bullet(items: list[str], empty: str = "未记录") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def build_report(data: dict) -> str:
    subject = data["subject"]
    assessment = data["business_assessment"]
    status_counts = Counter(item["status"] for item in data["claims"])
    lines = [
        f"# {subject['company_name']} 客户背调报告",
        "",
        f"调查日期：{data['analysis_date']}",
        f"国家或地区：{subject['country'] or '待确认'}",
        f"官网：{subject['website'] or '待确认'}",
        f"询盘邮箱：{subject['inquiry_email'] or '未提供'}",
        "",
        "## 结论概览",
        "",
        f"- 实际业务：{assessment['actual_business']}",
        f"- 客户角色：{assessment['customer_role']}",
        f"- 产品匹配：{assessment['product_match_score']:g}/5",
        f"- 采购信号：{assessment['purchase_signal_score']:g}/5",
        f"- 主体可信度：{assessment['identity_confidence_score']:g}/5",
        f"- 风险水平：{assessment['risk_score']:g}/5",
        f"- 结论状态：已核实 {status_counts['verified']}；较可能 {status_counts['probable']}；"
        f"未核实 {status_counts['unverified']}；存在冲突 {status_counts['conflicting']}",
        "",
        "判断依据：",
        bullet(assessment["reasoning"]),
        "",
        "## 事实与证据",
        "",
        "| 主题 | 状态 | 结论 | 来源 | 核查日期 |",
        "|---|---|---|---|---|",
    ]
    for claim in data["claims"]:
        source = f"[{claim['source_title']}]({claim['source_url']})" if claim["source_url"] else "无公开来源"
        statement = claim["statement"].replace("|", "\\|")
        lines.append(
            f"| {claim['topic']} | {claim['status']} | {statement} | {source} | {claim['checked_at']} |"
        )

    lines.extend(["", "## 风险事项", ""])
    if data["risk_flags"]:
        for risk in data["risk_flags"]:
            source = f"（[来源]({risk['source_url']}））" if risk["source_url"] else ""
            lines.append(f"- **{risk['severity']}**｜{risk['issue']}：{risk['evidence']}{source}")
    else:
        lines.append("- 暂未记录明确风险；这不等于不存在风险。")

    lines.extend(
        [
            "",
            "## 待确认事项",
            "",
            bullet(data["unknowns"]),
            "",
            "## 建议动作",
            "",
            bullet(data["recommended_actions"]),
            "",
            "## 公开联系人",
            "",
        ]
    )
    if data["contacts"]:
        for contact in data["contacts"]:
            label = " / ".join(value for value in (contact["name"], contact["role"]) if value) or "未标注姓名"
            details = "；".join(value for value in (contact["email"], contact["phone"]) if value)
            lines.append(f"- {label}：{details}（[来源]({contact['source_url']}））")
    else:
        lines.append("- 未发现可核验的公开联系人。")
    lines.append("")
    return "\n".join(lines)


def write_contacts(path: Path, contacts: list[dict]) -> None:
    fields = ["name", "role", "email", "phone", "source_url"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(contacts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 JSON investigation file")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output directory")
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        data = validate(raw)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "customer-background.md").write_text(build_report(data), encoding="utf-8")
        write_contacts(args.out_dir / "public-contacts.csv", data["contacts"])
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"已生成：{args.out_dir / 'customer-background.md'}")
    print(f"已生成：{args.out_dir / 'public-contacts.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
