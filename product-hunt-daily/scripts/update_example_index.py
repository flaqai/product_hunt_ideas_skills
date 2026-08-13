#!/usr/bin/env python3
"""Validate dated examples and regenerate the project example indexes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from export_contacts import validate


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
START_MARKER = "<!-- examples-table:start -->"
END_MARKER = "<!-- examples-table:end -->"


def collect(examples_dir: Path) -> tuple[list[dict], list[str]]:
    entries: list[dict] = []
    errors: list[str] = []
    required_files = {
        "README.md", "all-products.md", "contacts.json", "contacts.csv",
        "contact-audit.md", "sources.md", "browser-capture.json",
    }
    for directory in sorted(examples_dir.iterdir(), reverse=True):
        if not directory.is_dir() or not DATE_RE.fullmatch(directory.name):
            continue
        canonical = directory / "contacts.json"
        missing_files = sorted(name for name in required_files if not (directory / name).is_file())
        if missing_files:
            errors.append(f"{directory.name}: missing required artifacts: {', '.join(missing_files)}")
            continue
        try:
            data = json.loads(canonical.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{directory.name}: unable to read contacts.json: {exc}")
            continue
        data_errors = validate(data)
        if data_errors:
            errors.extend(f"{directory.name}: {error}" for error in data_errors)
            continue
        if data.get("leaderboard_date") != directory.name:
            errors.append(f"{directory.name}: leaderboard_date does not match directory name")
            continue
        products = data["products"]
        entries.append({
            "date": directory.name,
            "status": data["data_status"],
            "product_count": len(products),
            "featured_count": data["extracted_featured_count"],
            "collection_scope": data["collection_scope"],
            "detail_pages_checked": data["browser_collection"]["detail_page_count"],
            "contact_checks": sum(item["enrichment_status"] != "not_started" for item in products),
            "public_email_products": sum(bool(item["emails"]) for item in products),
            "path": f"{directory.name}/",
        })
    return entries, errors


def examples_readme(entries: list[dict]) -> str:
    lines = [
        "# Product Hunt 日期示例索引", "",
        "所有示例以 Product Hunt 日历日期（`America/Los_Angeles`）为索引，最新日期在前。", "",
        "| 日期 | 状态 | 官方可见产品 | Featured | 视图范围 | 详情覆盖 | 联系覆盖 | 公开邮箱 |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for item in entries:
        count = item["product_count"]
        lines.append(
            f"| [{item['date']}]({item['path']}) | {item['status']} | {count} | {item['featured_count']} | "
            f"{item['collection_scope']} | {item['detail_pages_checked']}/{count} | {item['contact_checks']}/{count} | "
            f"{item['public_email_products']} |"
        )
    lines.extend([
        "", "## 如何增加日期", "",
        "1. 使用 `product-hunt-daily` Skill 完成目标日期采集及全部校验。",
        "2. 将最终交付物保存到 `examples/YYYY-MM-DD/`。",
        "3. 以该日期目录的 `README.md` 记录结果摘要、官网异常、阻断项和数据边界。",
        "4. 在仓库根目录运行 `python3 product-hunt-daily/scripts/update_example_index.py`，自动校验并重建索引。", "",
        "临时或未完成的运行结果应留在 `product-hunt-daily/output/`。只有通过标准化、CSV 导出、审计和来源清单校验的结果才能进入本目录。", "",
    ])
    return "\n".join(lines)


def root_table(entries: list[dict], language: str = "zh-CN") -> str:
    if language == "en":
        lines = [
            START_MARKER,
            "| Date | Status | Visible products | Featured | Detail pages | Contact checks | Public email | Example |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    else:
        lines = [
            START_MARKER,
            "| 日期 | 状态 | 官方可见产品 | Featured | 详情页 | 联系检查 | 公开邮箱 | 示例 |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    for item in entries:
        count = item["product_count"]
        link_label = "Open" if language == "en" else "查看示例"
        lines.append(
            f"| {item['date']} | {item['status']} | {count} | {item['featured_count']} | "
            f"{item['detail_pages_checked']}/{count} | {item['contact_checks']}/{count} | "
            f"{item['public_email_products']} | [{link_label}](examples/{item['date']}/) |"
        )
    lines.append(END_MARKER)
    return "\n".join(lines)


def replace_root_table(readme: str, table: str) -> str:
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start < 0 or end < start:
        raise ValueError("root README is missing example table markers")
    end += len(END_MARKER)
    return readme[:start] + table + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    examples_dir = repo_root / "examples"
    root_readme = repo_root / "README.md"
    english_readme = repo_root / "README.en.md"
    if not examples_dir.is_dir() or not root_readme.is_file() or not english_readme.is_file():
        print("ERROR: repository examples/, README.md, and README.en.md are required", file=sys.stderr)
        return 2
    entries, errors = collect(examples_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if not entries:
        print("ERROR: no validated dated examples found", file=sys.stderr)
        return 1
    try:
        updated_root = replace_root_table(root_readme.read_text(encoding="utf-8"), root_table(entries, "zh-CN"))
        updated_english = replace_root_table(english_readme.read_text(encoding="utf-8"), root_table(entries, "en"))
    except (OSError, ValueError) as exc:
        print(f"ERROR: unable to update root README: {exc}", file=sys.stderr)
        return 2
    (examples_dir / "index.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (examples_dir / "README.md").write_text(examples_readme(entries), encoding="utf-8")
    root_readme.write_text(updated_root, encoding="utf-8")
    english_readme.write_text(updated_english, encoding="utf-8")
    print(f"Indexed {len(entries)} validated example date(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
