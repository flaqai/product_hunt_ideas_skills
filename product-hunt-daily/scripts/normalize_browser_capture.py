#!/usr/bin/env python3
"""Normalize a complete in-app-browser Product Hunt capture into canonical JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

from export_contacts import validate


PRODUCT_HUNT_HOSTS = {"producthunt.com", "www.producthunt.com"}


def canonical_url(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    parts = urlsplit(value.strip())
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def is_product_url(value: str) -> bool:
    parts = urlsplit(value)
    return parts.scheme in {"http", "https"} and parts.netloc.lower() in PRODUCT_HUNT_HOSTS and (
        parts.path.startswith("/posts/") or parts.path.startswith("/products/")
    )


def require_object(value: object, label: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return {}
    return value


def require_array(value: object, label: str, errors: list[str]) -> list:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array")
        return []
    return value


def normalize_rows(rows: list, rank_key: str, label: str, errors: list[str]) -> tuple[list[dict], int]:
    unique: list[dict] = []
    seen: set[str] = set()
    duplicate_count = 0
    ranked: list[tuple[int, dict]] = []
    for index, raw in enumerate(rows, 1):
        if not isinstance(raw, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        url = canonical_url(raw.get("product_hunt_url"))
        if not is_product_url(url):
            errors.append(f"{label}[{index}] requires a canonical Product Hunt post/product URL")
            continue
        if url in seen:
            duplicate_count += 1
            continue
        seen.add(url)
        visible_rank = raw.get(rank_key)
        if not isinstance(visible_rank, int) or visible_rank < 1:
            errors.append(f"{label}[{index}] requires a positive visible {rank_key}")
            continue
        row = dict(raw)
        row["product_hunt_url"] = url
        ranked.append((visible_rank, row))
    seen_ranks: set[int] = set()
    for visible_rank, row in sorted(ranked, key=lambda item: item[0]):
        if visible_rank in seen_ranks:
            errors.append(f"{label} duplicates visible {rank_key} {visible_rank}")
            continue
        seen_ranks.add(visible_rank)
        row[f"displayed_{rank_key}"] = visible_rank
        row[rank_key] = len(unique) + 1
        unique.append(row)
    return unique, duplicate_count


def check_view(view: dict, label: str, rows: list[dict], errors: list[str]) -> None:
    if view.get("end_reached") is not True:
        errors.append(f"{label}.end_reached must be true")
    if not isinstance(view.get("stable_passes"), int) or view.get("stable_passes", 0) < 2:
        errors.append(f"{label}.stable_passes must be at least 2")
    displayed = view.get("displayed_total")
    if displayed is not None and displayed != len(rows):
        errors.append(f"{label}.displayed_total {displayed!r} does not match {len(rows)} unique products")
    expected = {item["product_hunt_url"] for item in rows}
    stable_sets = view.get("stable_url_sets")
    if not isinstance(stable_sets, list) or len(stable_sets) < 2:
        errors.append(f"{label}.stable_url_sets must contain at least two URL arrays")
    else:
        for pass_index, url_list in enumerate(stable_sets[-2:], 1):
            if not isinstance(url_list, list):
                errors.append(f"{label}.stable_url_sets pass {pass_index} must be an array")
                continue
            observed = {canonical_url(url) for url in url_list if canonical_url(url)}
            if observed != expected or len(url_list) != len(expected):
                errors.append(f"{label}.stable_url_sets pass {pass_index} does not equal the unique product URL set")


def slug_from_url(url: str) -> str:
    return urlsplit(url).path.rstrip("/").split("/")[-1]


def detail_product(row: dict, detail: dict, featured: Optional[dict]) -> dict:
    def arr(name: str) -> list:
        value = detail.get(name, [])
        return value if isinstance(value, list) else []

    official = canonical_url(detail.get("official_website_url"))
    visit = str(detail.get("product_hunt_visit_url") or official or "")
    return {
        "rank": row["rank"],
        "displayed_rank": row["displayed_rank"],
        "product_hunt_id": str(detail.get("product_hunt_id") or ""),
        "slug": str(detail.get("slug") or slug_from_url(row["product_hunt_url"])),
        "is_featured": featured is not None,
        "featured_rank": featured["featured_rank"] if featured is not None else None,
        "displayed_featured_rank": featured["displayed_featured_rank"] if featured is not None else None,
        "featured_rank_source": "visible_featured_view_position" if featured is not None else "",
        "observed_in_all": row.get("observed_in_all", True),
        "observed_in_featured": featured is not None,
        "recovered_from_view": row.get("recovered_from_view", ""),
        "product_name": str(detail.get("product_name") or row.get("product_name") or "").strip(),
        "tagline": str(detail.get("tagline") or row.get("tagline") or "").strip(),
        "description": str(detail.get("description") or "").strip(),
        "upvotes": detail.get("upvotes", row.get("upvotes")),
        "comments": detail.get("comments", row.get("comments")),
        "reviews_count": detail.get("reviews_count"),
        "reviews_rating": detail.get("reviews_rating"),
        "created_at": str(detail.get("created_at") or ""),
        "featured_at": str(detail.get("featured_at") or ""),
        "product_hunt_url": row["product_hunt_url"],
        "product_hunt_visit_url": visit,
        "official_website_url": official,
        "thumbnail": detail.get("thumbnail"),
        "media": arr("media"),
        "topics": arr("topics"),
        "product_links": arr("product_links"),
        "developers": arr("developers"),
        "submitter": detail.get("submitter") if isinstance(detail.get("submitter"), dict) else {},
        "company": detail.get("company") if isinstance(detail.get("company"), dict) else {"name": "", "source_url": "", "confidence": ""},
        "enrichment_status": str(detail.get("enrichment_status") or "not_started"),
        "contact_status": str(detail.get("contact_status") or "not_checked"),
        "contact_form_url": str(detail.get("contact_form_url") or ""),
        "last_verified_at": str(detail.get("last_verified_at") or ""),
        "emails": arr("emails"),
        "public_channels": arr("public_channels"),
        "pages_checked": arr("pages_checked"),
        "notes": str(detail.get("notes") or ""),
    }


def normalize(capture: object) -> Tuple[Optional[dict], list[str]]:
    errors: list[str] = []
    root = require_object(capture, "root", errors)
    if not root:
        return None, errors
    for key in ("leaderboard_date", "day_timezone", "leaderboard_url", "accessed_at"):
        if not isinstance(root.get(key), str) or not root.get(key):
            errors.append(f"root.{key} is required")
    if root.get("day_timezone") != "America/Los_Angeles":
        errors.append("root.day_timezone must be America/Los_Angeles")

    all_view = require_object(root.get("all_view"), "all_view", errors)
    featured_view = require_object(root.get("featured_view"), "featured_view", errors)
    all_raw = require_array(all_view.get("products"), "all_view.products", errors)
    featured_raw = require_array(featured_view.get("products"), "featured_view.products", errors)
    all_rows, all_duplicates = normalize_rows(all_raw, "rank", "all_view.products", errors)
    featured_rows, featured_duplicates = normalize_rows(featured_raw, "featured_rank", "featured_view.products", errors)
    check_view(all_view, "all_view", all_rows, errors)
    check_view(featured_view, "featured_view", featured_rows, errors)
    if all_view.get("final_recheck_matches") is not True:
        errors.append("all_view.final_recheck_matches must be true")
    final_recheck = all_view.get("final_recheck_urls")
    if not isinstance(final_recheck, list):
        errors.append("all_view.final_recheck_urls must be an array")
    else:
        final_urls = {canonical_url(url) for url in final_recheck if canonical_url(url)}
        if final_urls != {item["product_hunt_url"] for item in all_rows} or len(final_recheck) != len(all_rows):
            errors.append("all_view.final_recheck_urls does not equal the unique All URL set")

    all_source_urls = {item["product_hunt_url"] for item in all_rows}
    featured_urls = {item["product_hunt_url"] for item in featured_rows}
    missing_featured = sorted(featured_urls - all_source_urls)
    allow_union = root.get("allow_official_view_union") is True
    if missing_featured and not allow_union:
        errors.append(
            "Featured URLs absent from All; set allow_official_view_union=true only after verifying and documenting the official view discrepancy: "
            + ", ".join(missing_featured)
        )
    if allow_union and not missing_featured:
        errors.append("allow_official_view_union=true requires an observed Featured URL absent from All")

    for row in all_rows:
        row["observed_in_all"] = True
        row["recovered_from_view"] = ""
    if allow_union:
        featured_by_url_for_recovery = {item["product_hunt_url"]: item for item in featured_rows}
        for url in missing_featured:
            featured_row = featured_by_url_for_recovery[url]
            recovered = dict(featured_row)
            recovered["displayed_rank"] = featured_row["displayed_featured_rank"]
            recovered["observed_in_all"] = False
            recovered["recovered_from_view"] = "featured"
            all_rows.append(recovered)
        all_rows.sort(key=lambda item: (item["displayed_rank"], item["product_hunt_url"]))
        for index, row in enumerate(all_rows, 1):
            row["rank"] = index
    all_urls = {item["product_hunt_url"] for item in all_rows}

    details_raw = require_array(root.get("details"), "details", errors)
    detail_by_url: dict[str, dict] = {}
    for index, raw in enumerate(details_raw, 1):
        if not isinstance(raw, dict):
            errors.append(f"details[{index}] must be an object")
            continue
        url = canonical_url(raw.get("product_hunt_url"))
        if not is_product_url(url):
            errors.append(f"details[{index}] requires a Product Hunt URL")
            continue
        if url in detail_by_url:
            errors.append(f"details[{index}] duplicates {url}")
            continue
        if raw.get("page_opened") is not True:
            errors.append(f"details[{index}].page_opened must be true")
        sections = raw.get("sections_checked")
        required_sections = {"name_tagline", "description", "metrics", "topics", "media", "team", "visit"}
        if not isinstance(sections, list) or not required_sections.issubset(set(sections)):
            errors.append(f"details[{index}].sections_checked must include: {', '.join(sorted(required_sections))}")
        detail_by_url[url] = raw
    missing_details = sorted(all_urls - set(detail_by_url))
    extra_details = sorted(set(detail_by_url) - all_urls)
    if missing_details:
        errors.append("All products missing detail records: " + ", ".join(missing_details))
    if extra_details:
        errors.append("Detail records absent from All: " + ", ".join(extra_details))
    collection_errors = require_array(root.get("collection_errors"), "collection_errors", errors)
    if collection_errors:
        errors.append(f"collection_errors contains {len(collection_errors)} unresolved item(s)")
    if errors:
        return None, errors

    featured_by_url = {item["product_hunt_url"]: item for item in featured_rows}
    products = [detail_product(row, detail_by_url[row["product_hunt_url"]], featured_by_url.get(row["product_hunt_url"])) for row in all_rows]
    featured_count = len(featured_rows)
    data = {
        "schema_version": 2,
        "leaderboard_date": root["leaderboard_date"],
        "day_timezone": root["day_timezone"],
        "leaderboard_url": canonical_url(root["leaderboard_url"]),
        "inventory_source": "product_hunt_in_app_browser",
        "inventory_source_url": canonical_url(root["leaderboard_url"]),
        "inventory_source_tier": "official_visible_webpage",
        "accessed_at": root["accessed_at"],
        "data_status": "in_progress" if root.get("is_live_day") is True else "completed",
        "collection_scope": "official_view_union" if allow_union else "all",
        "sort_order": "displayed_product_hunt_rank",
        "inventory_complete": True,
        "browser_collection": {
            "all_end_reached": True,
            "all_stable_passes": all_view["stable_passes"],
            "all_displayed_total": all_view.get("displayed_total"),
            "all_final_recheck_matches": True,
            "featured_end_reached": True,
            "featured_stable_passes": featured_view["stable_passes"],
            "featured_displayed_total": featured_view.get("displayed_total"),
            "detail_page_count": len(detail_by_url),
            "all_source_product_count": len(all_source_urls),
            "official_union_product_count": len(all_rows),
            "recovered_from_featured_count": len(missing_featured),
            "featured_urls_absent_from_all": missing_featured,
            "all_displayed_rank_gaps": sorted(set(range(1, max((item["displayed_rank"] for item in all_rows), default=0) + 1)) - {item["displayed_rank"] for item in all_rows}),
            "featured_displayed_rank_gaps": sorted(set(range(1, max((item["displayed_featured_rank"] for item in featured_rows), default=0) + 1)) - {item["displayed_featured_rank"] for item in featured_rows}),
        },
        "source_row_count": len(all_raw) + len(missing_featured),
        "duplicate_row_count": all_duplicates,
        "featured_source_row_count": len(featured_raw),
        "featured_duplicate_row_count": featured_duplicates,
        "expected_product_count": len(all_rows),
        "extracted_product_count": len(products),
        "expected_featured_count": featured_count,
        "extracted_featured_count": featured_count,
        "expected_unfeatured_count": len(products) - featured_count,
        "extracted_unfeatured_count": len(products) - featured_count,
        "products": products,
    }
    canonical_errors = validate(data)
    if canonical_errors:
        return None, canonical_errors
    return data, []


def render_markdown(data: dict) -> str:
    lines = [
        f"# Product Hunt complete browser inventory: {data['leaderboard_date']}", "",
        f"- Product Hunt timezone: {data['day_timezone']}",
        f"- Snapshot status: {data['data_status']}",
        f"- All products: {data['extracted_product_count']}",
        f"- Featured / non-Featured: {data['extracted_featured_count']} / {data['extracted_unfeatured_count']}",
        f"- Detail pages opened: {data['browser_collection']['detail_page_count']}",
        f"- Official view scope: {data['collection_scope']}",
        f"- Featured-only recovered products: {data['browser_collection'].get('recovered_from_featured_count', 0)}",
        f"- Displayed rank gaps: {', '.join(map(str, data['browser_collection'].get('all_displayed_rank_gaps', []))) or 'none'}",
        f"- Accessed at: {data['accessed_at']}", "",
        "| List | Displayed | Featured | Product | Makers | Votes | Comments | Topics |",
        "|---:|---:|---:|---|---|---:|---:|---|",
    ]
    for product in data["products"]:
        name = product["product_name"].replace("|", "\\|")
        makers = ", ".join(item.get("name", "") for item in product["developers"]).replace("|", "\\|")
        topics = ", ".join(item.get("name", "") for item in product["topics"]).replace("|", "\\|")
        featured = product["featured_rank"] if product["featured_rank"] is not None else "—"
        lines.append(f"| {product['rank']} | {product['displayed_rank']} | {featured} | [{name}]({product['product_hunt_url']}) | {makers or '—'} | {product['upvotes'] if product['upvotes'] is not None else '—'} | {product['comments'] if product['comments'] is not None else '—'} | {topics or '—'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_capture", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    try:
        capture = json.loads(args.input_capture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to read browser capture: {exc}", file=sys.stderr)
        return 2
    data, errors = normalize(capture)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(data), encoding="utf-8")
    print(f"Normalized {data['extracted_product_count']} complete browser products ({data['extracted_featured_count']} Featured)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
