#!/usr/bin/env python3
"""Audit Product Hunt team/contact evidence and write a prioritized gap report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from export_contacts import validate


def score_product(product: dict) -> tuple[int, list[str]]:
    score, gaps = 0, []
    if product.get("official_website_url"):
        score += 10
    else:
        gaps.append("official site")
    if product.get("company", {}).get("name"):
        score += 15
    else:
        gaps.append("company")
    makers = product.get("developers", [])
    if makers:
        score += min(20, len(makers) * 10)
    else:
        gaps.append("maker/team")
    emails = product.get("emails", [])
    if emails:
        score += 25
    else:
        gaps.append("public email")
    if product.get("contact_form_url"):
        score += 10
    elif not emails:
        gaps.append("contact route")
    channels = product.get("public_channels", [])
    score += min(15, len(channels) * 5)
    if len(channels) < 2:
        gaps.append("2 professional channels")
    if emails and all(item.get("confidence") == "high" for item in emails):
        score += 5
    return min(score, 100), gaps


def build_report(data: dict) -> str:
    products = data["products"]
    attempted = [item for item in products if item.get("enrichment_status") != "not_started"]
    scored = [(score_product(item)[0], item, score_product(item)[1]) for item in attempted]
    average = round(sum(item[0] for item in scored) / len(scored)) if scored else 0
    lines = [
        f"# Contact evidence audit: {data['leaderboard_date']}", "",
        f"- Complete inventory: {len(products)} products",
        f"- Featured / non-Featured: {data['extracted_featured_count']} / {data['extracted_unfeatured_count']}",
        f"- Enrichment attempted: {len(attempted)}",
        f"- Products with a public email: {sum(bool(item.get('emails')) for item in products)}",
        f"- Average attempted coverage: {average}/100", "",
        "## Coverage", "",
        "| All | Featured | Product | Status | Score | Email | Channels | Gaps |",
        "|---:|---:|---|---|---:|---|---:|---|",
    ]
    for score, product, gaps in sorted(scored, key=lambda item: item[1]["rank"]):
        featured = product["featured_rank"] if product.get("featured_rank") is not None else ("yes" if product.get("is_featured") else "—")
        lines.append(
            f"| {product['rank']} | {featured} | {product['product_name']} | {product['enrichment_status']} | "
            f"{score} | {'yes' if product.get('emails') else 'no'} | {len(product.get('public_channels', []))} | "
            f"{', '.join(gaps) if gaps else 'complete'} |"
        )
    lines.extend(["", "## Priority queue", ""])
    for score, product, gaps in sorted(scored, key=lambda item: (item[0], item[1]["rank"])):
        if gaps:
            lines.append(f"- **{product['product_name']} ({score}/100):** {', '.join(gaps)}")
    not_started = [item for item in products if item.get("enrichment_status") == "not_started"]
    if not_started:
        lines.extend(["", "## Not researched", "", f"{len(not_started)} inventory products have not entered contact enrichment."])
    lines.extend(["", "Coverage measures sourced evidence, not lead quality. Never fill a gap with inferred contact data.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_markdown", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to read JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text(build_report(data), encoding="utf-8")
    attempted = sum(item.get("enrichment_status") != "not_started" for item in data["products"])
    print(f"Audited {len(data['products'])} products; enrichment attempted for {attempted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
