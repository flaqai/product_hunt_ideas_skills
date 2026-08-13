#!/usr/bin/env python3
"""Write a deduplicated Markdown source ledger from canonical Product Hunt JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from export_contacts import validate


def build_sources(data: dict) -> str:
    sources: dict[str, set[str]] = {}

    def add(url: object, label: str) -> None:
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            sources.setdefault(url, set()).add(label)

    add(data.get("leaderboard_url"), "Product Hunt leaderboard")
    add(data.get("inventory_source_url"), f"Inventory source ({data.get('inventory_source_tier', '')})")
    for product in data["products"]:
        name = product["product_name"]
        add(product.get("product_hunt_url"), f"{name}: Product Hunt launch")
        add(product.get("official_website_url"), f"{name}: official website")
        add(product.get("company", {}).get("source_url"), f"{name}: company evidence")
        for developer in product.get("developers", []):
            add(developer.get("source_url"), f"{name}: {developer.get('role', 'team')} {developer.get('name', '')}")
        for email in product.get("emails", []):
            add(email.get("source_url"), f"{name}: public email evidence")
        for channel in product.get("public_channels", []):
            add(channel.get("source_url"), f"{name}: {channel.get('type', 'channel')} evidence")
        for page in product.get("pages_checked", []):
            add(page, f"{name}: page checked")
    lines = [f"# Sources: Product Hunt {data['leaderboard_date']}", "", f"Accessed: {data['accessed_at']}", ""]
    for url, labels in sources.items():
        lines.append(f"- [{'; '.join(sorted(labels))}]({url})")
    return "\n".join(lines) + "\n"


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
    args.output_markdown.write_text(build_sources(data), encoding="utf-8")
    print(f"Wrote source ledger to {args.output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
