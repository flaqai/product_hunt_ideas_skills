#!/usr/bin/env python3
"""Strictly validate Product Hunt inventory/contact JSON and export flat CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


CONTACT_STATUSES = {"found", "contact_form_only", "not_publicly_listed", "site_unavailable", "not_checked"}
ENRICHMENT_STATUSES = {"not_started", "partial", "enriched", "blocked"}
EMAIL_TYPES = {"general", "support", "sales", "press", "founder_developer", "security", "other"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
CHANNEL_TYPES = {"contact_form", "booking", "phone", "github", "linkedin", "x", "discord", "app_store", "other"}
SOURCE_TIERS = {"official_legal", "official_site", "official_product_store", "official_linked_profile", "product_hunt", "public_code_host", "company_registry", "credible_secondary"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
CSV_FIELDS = [
    "leaderboard_date", "rank", "displayed_rank", "is_featured", "featured_rank", "displayed_featured_rank", "observed_in_all", "observed_in_featured", "recovered_from_view", "product_name", "tagline",
    "description", "upvotes", "comments", "reviews_count", "reviews_rating", "created_at", "featured_at",
    "product_hunt_url", "product_hunt_visit_url", "official_website_url", "thumbnail", "media", "product_links",
    "topics", "company_name", "company_source_url", "maker_names", "maker_roles", "maker_profile_urls",
    "submitter_name", "submitter_profile_url", "pages_checked",
    "contact_status", "enrichment_status", "contact_form_url", "public_channels", "public_channel_sources",
    "email", "email_type", "contact_name", "email_source_url", "source_context", "email_source_tier",
    "confidence", "last_verified_at", "notes",
]


def is_http_url(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def require_keys(value: dict, keys: set[str], label: str, errors: list[str]) -> bool:
    missing = sorted(keys - set(value))
    if missing:
        errors.append(f"{label}: missing keys: {', '.join(missing)}")
        return False
    return True


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]
    roots = {
        "schema_version", "leaderboard_date", "day_timezone", "leaderboard_url", "inventory_source", "inventory_source_tier", "accessed_at",
        "data_status", "collection_scope", "sort_order", "inventory_complete", "source_row_count",
        "duplicate_row_count", "expected_product_count", "extracted_product_count", "expected_featured_count",
        "extracted_featured_count", "expected_unfeatured_count", "extracted_unfeatured_count", "products",
    }
    if not require_keys(data, roots, "root", errors):
        return errors
    if data["collection_scope"] not in {"all", "official_view_union"}:
        errors.append("root: collection_scope must be all or official_view_union")
    if data["inventory_source"] != "product_hunt_in_app_browser":
        errors.append("root: inventory_source must be product_hunt_in_app_browser")
    if data["inventory_source_tier"] != "official_visible_webpage":
        errors.append("root: inventory_source_tier must be official_visible_webpage")
    if data["schema_version"] != 2:
        errors.append("root: schema_version must be 2")
    if data["data_status"] not in {"completed", "in_progress", "partial"}:
        errors.append("root: invalid data_status")
    if not isinstance(data["inventory_complete"], bool):
        errors.append("root: inventory_complete must be boolean")
    elif not data["inventory_complete"]:
        errors.append("root: inventory_complete must be true before export or audit")
    if data["data_status"] == "partial":
        errors.append("root: partial datasets cannot be exported as complete inventories")
    if not is_http_url(data["leaderboard_url"]):
        errors.append("root: leaderboard_url must be HTTP(S)")
    if not isinstance(data["products"], list):
        return errors + ["root: products must be an array"]
    count = len(data["products"])
    for key in ("expected_product_count", "extracted_product_count"):
        if data[key] != count:
            errors.append(f"root: {key} {data[key]!r} does not equal products length {count}")
    if not isinstance(data["source_row_count"], int) or not isinstance(data["duplicate_row_count"], int):
        errors.append("root: source_row_count and duplicate_row_count must be integers")
    elif data["source_row_count"] - data["duplicate_row_count"] != count:
        errors.append("root: source rows minus duplicates must equal unique product count")
    browser_collection = data.get("browser_collection")
    if not isinstance(browser_collection, dict):
        errors.append("root: browser_collection evidence is required")
    else:
        required_collection = {
            "all_end_reached", "all_stable_passes", "all_final_recheck_matches", "featured_end_reached",
            "featured_stable_passes", "detail_page_count",
        }
        require_keys(browser_collection, required_collection, "root.browser_collection", errors)
        if browser_collection.get("all_end_reached") is not True or browser_collection.get("featured_end_reached") is not True:
            errors.append("root.browser_collection: All and Featured must reach a visible end")
        if browser_collection.get("all_stable_passes", 0) < 2 or browser_collection.get("featured_stable_passes", 0) < 2:
            errors.append("root.browser_collection: All and Featured require at least two stable end passes")
        if browser_collection.get("all_final_recheck_matches") is not True:
            errors.append("root.browser_collection: final All recheck must match")
        if browser_collection.get("detail_page_count") != count:
            errors.append("root.browser_collection: detail_page_count must equal product count")
        absent = browser_collection.get("featured_urls_absent_from_all", [])
        recovered_count = browser_collection.get("recovered_from_featured_count", 0)
        if data["collection_scope"] == "official_view_union":
            if not isinstance(absent, list) or not absent or recovered_count != len(absent):
                errors.append("root.browser_collection: official_view_union requires non-empty, reconciled Featured recovery evidence")
        elif absent or recovered_count:
            errors.append("root.browser_collection: All scope cannot contain Featured recovery evidence")

    product_keys = {
        "rank", "displayed_rank", "product_hunt_id", "slug", "is_featured", "featured_rank", "displayed_featured_rank", "observed_in_all", "observed_in_featured", "recovered_from_view", "product_name", "tagline", "description",
        "upvotes", "comments", "reviews_count", "reviews_rating", "created_at", "featured_at", "product_hunt_url",
        "product_hunt_visit_url", "official_website_url", "thumbnail", "media", "topics", "product_links", "developers",
        "submitter", "company", "contact_status", "enrichment_status", "contact_form_url", "emails", "public_channels",
        "pages_checked", "notes",
    }
    ranks, displayed_ranks, identities, featured_ranks, displayed_featured_ranks = set(), set(), set(), set(), set()
    featured_count = 0
    for index, product in enumerate(data["products"], 1):
        label = f"product[{index}]"
        if not isinstance(product, dict) or not require_keys(product, product_keys, label, errors):
            continue
        rank = product["rank"]
        if not isinstance(rank, int) or rank < 1 or rank in ranks:
            errors.append(f"{label}: rank must be a unique positive integer")
        ranks.add(rank)
        displayed_rank = product["displayed_rank"]
        if not isinstance(displayed_rank, int) or displayed_rank < 1 or displayed_rank in displayed_ranks:
            errors.append(f"{label}: displayed_rank must be a unique positive integer")
        displayed_ranks.add(displayed_rank)
        identity = str(product["product_hunt_id"] or product["product_hunt_url"])
        if not identity or identity in identities:
            errors.append(f"{label}: Product Hunt identity must be present and unique")
        identities.add(identity)
        if not product["product_name"]:
            errors.append(f"{label}: product_name is required")
        for array_key in ("media", "topics", "product_links", "pages_checked"):
            if not isinstance(product[array_key], list):
                errors.append(f"{label}: {array_key} must be an array")
        if not isinstance(product["submitter"], dict):
            errors.append(f"{label}: submitter must be an object")
        if not is_http_url(product["product_hunt_url"]):
            errors.append(f"{label}: product_hunt_url must be HTTP(S)")
        if product["product_hunt_visit_url"] and not is_http_url(product["product_hunt_visit_url"]):
            errors.append(f"{label}: product_hunt_visit_url must be empty or HTTP(S)")
        if product["official_website_url"] and not is_http_url(product["official_website_url"]):
            errors.append(f"{label}: official_website_url must be empty or HTTP(S)")
        if not isinstance(product["is_featured"], bool):
            errors.append(f"{label}: is_featured must be boolean")
        elif product["is_featured"]:
            featured_count += 1
            if product["featured_rank"] is not None:
                if not isinstance(product["featured_rank"], int) or product["featured_rank"] < 1 or product["featured_rank"] in featured_ranks:
                    errors.append(f"{label}: featured_rank must be null or a unique positive integer")
                featured_ranks.add(product["featured_rank"])
            displayed_featured_rank = product["displayed_featured_rank"]
            if not isinstance(displayed_featured_rank, int) or displayed_featured_rank < 1 or displayed_featured_rank in displayed_featured_ranks:
                errors.append(f"{label}: Featured products require a unique positive displayed_featured_rank")
            displayed_featured_ranks.add(displayed_featured_rank)
        elif product["featured_rank"] is not None:
            errors.append(f"{label}: non-Featured product requires featured_rank null")
        elif product["displayed_featured_rank"] is not None:
            errors.append(f"{label}: non-Featured product requires displayed_featured_rank null")
        if not isinstance(product["observed_in_all"], bool) or not isinstance(product["observed_in_featured"], bool):
            errors.append(f"{label}: observed_in_all and observed_in_featured must be boolean")
        if product["recovered_from_view"] not in {"", "featured"}:
            errors.append(f"{label}: recovered_from_view must be empty or featured")
        if product["recovered_from_view"] == "featured" and (product["observed_in_all"] or not product["observed_in_featured"]):
            errors.append(f"{label}: featured recovery requires observed_in_all=false and observed_in_featured=true")
        if not product["observed_in_all"] and data["collection_scope"] != "official_view_union":
            errors.append(f"{label}: products absent from All require collection_scope official_view_union")
        if product["contact_status"] not in CONTACT_STATUSES:
            errors.append(f"{label}: invalid contact_status")
        if product["enrichment_status"] not in ENRICHMENT_STATUSES:
            errors.append(f"{label}: invalid enrichment_status")
        if product["enrichment_status"] == "not_started" and product["contact_status"] != "not_checked":
            errors.append(f"{label}: not_started enrichment requires not_checked contact status")
        if product["enrichment_status"] == "not_started" and (
            product["emails"] or product["public_channels"] or product["contact_form_url"]
        ):
            errors.append(f"{label}: not_started enrichment cannot contain researched contacts")
        if product["contact_form_url"] and not is_http_url(product["contact_form_url"]):
            errors.append(f"{label}: contact_form_url must be empty or HTTP(S)")

        company = product["company"]
        if not isinstance(company, dict) or not require_keys(company, {"name", "source_url", "confidence"}, f"{label}.company", errors):
            pass
        elif company["name"]:
            if not is_http_url(company["source_url"]):
                errors.append(f"{label}.company: a name requires source_url")
            if company["confidence"] not in CONFIDENCE_LEVELS:
                errors.append(f"{label}.company: invalid confidence")

        if not isinstance(product["developers"], list):
            errors.append(f"{label}: developers must be an array")
        else:
            for dev_index, developer in enumerate(product["developers"], 1):
                dev_label = f"{label}.developers[{dev_index}]"
                if not isinstance(developer, dict) or not require_keys(developer, {"name", "role", "source_url"}, dev_label, errors):
                    continue
                if not developer["name"] or not is_http_url(developer["source_url"]):
                    errors.append(f"{dev_label}: name and Product Hunt/official source_url are required")

        if not isinstance(product["pages_checked"], list) or any(not is_http_url(page) for page in product["pages_checked"]):
            errors.append(f"{label}: pages_checked must contain only HTTP(S) URLs")
        if product["enrichment_status"] != "not_started" and not product["pages_checked"]:
            errors.append(f"{label}: attempted enrichment requires at least one page_checked URL")

        emails = product["emails"]
        if not isinstance(emails, list):
            errors.append(f"{label}: emails must be an array")
            continue
        if emails and product["contact_status"] != "found":
            errors.append(f"{label}: email records require contact_status found")
        if not emails and product["contact_status"] == "found":
            errors.append(f"{label}: found contact_status requires an email record")
        if product["contact_status"] == "contact_form_only" and not product["contact_form_url"]:
            errors.append(f"{label}: contact_form_only requires contact_form_url")
        if product["contact_status"] == "not_checked" and product["enrichment_status"] != "not_started":
            errors.append(f"{label}: not_checked contact status is only valid before enrichment")
        seen_emails = set()
        for email_index, email in enumerate(emails, 1):
            email_label = f"{label}.emails[{email_index}]"
            required = {"email", "type", "contact_name", "source_url", "source_context", "source_tier", "is_publicly_listed", "confidence"}
            if not isinstance(email, dict) or not require_keys(email, required, email_label, errors):
                continue
            address = str(email["email"]).lower()
            if not EMAIL_RE.fullmatch(address) or address in seen_emails:
                errors.append(f"{email_label}: email must be valid and unique per product")
            seen_emails.add(address)
            if email["type"] not in EMAIL_TYPES or email["source_tier"] not in SOURCE_TIERS or email["confidence"] not in CONFIDENCE_LEVELS:
                errors.append(f"{email_label}: invalid type, source_tier, or confidence")
            if not is_http_url(email["source_url"]) or not email["source_context"] or email["is_publicly_listed"] is not True:
                errors.append(f"{email_label}: public source URL/context and is_publicly_listed=true are required")

        channels = product["public_channels"]
        if not isinstance(channels, list):
            errors.append(f"{label}: public_channels must be an array")
        else:
            seen_channels = set()
            for channel_index, channel in enumerate(channels, 1):
                channel_label = f"{label}.public_channels[{channel_index}]"
                required = {"type", "value", "label", "owner", "source_url", "source_context", "source_tier", "confidence"}
                if not isinstance(channel, dict) or not require_keys(channel, required, channel_label, errors):
                    continue
                key = (str(channel["type"]), str(channel["value"]).lower())
                if key in seen_channels:
                    errors.append(f"{channel_label}: duplicate channel")
                seen_channels.add(key)
                if channel["type"] not in CHANNEL_TYPES or channel["source_tier"] not in SOURCE_TIERS or channel["confidence"] not in CONFIDENCE_LEVELS:
                    errors.append(f"{channel_label}: invalid type, source_tier, or confidence")
                if not channel["value"] or not is_http_url(channel["source_url"]) or not channel["source_context"]:
                    errors.append(f"{channel_label}: value and evidence source/context are required")

    if ranks != set(range(1, count + 1)):
        errors.append("root: product ranks must be contiguous from 1 through product count")
    unfeatured_count = count - featured_count
    for key in ("expected_featured_count", "extracted_featured_count"):
        if data[key] != featured_count:
            errors.append(f"root: {key} must equal marked Featured count {featured_count}")
    for key in ("expected_unfeatured_count", "extracted_unfeatured_count"):
        if data[key] != unfeatured_count:
            errors.append(f"root: {key} must equal marked non-Featured count {unfeatured_count}")
    return errors


def export_rows(data: dict) -> list[dict[str, object]]:
    rows = []
    for product in sorted(data["products"], key=lambda item: item["rank"]):
        makers = product["developers"]
        channels = product["public_channels"]
        company = product["company"]
        common = {
            "leaderboard_date": data["leaderboard_date"], "rank": product["rank"], "displayed_rank": product["displayed_rank"],
            "is_featured": product["is_featured"], "featured_rank": product["featured_rank"] or "",
            "displayed_featured_rank": product["displayed_featured_rank"] or "",
            "observed_in_all": product["observed_in_all"], "observed_in_featured": product["observed_in_featured"],
            "recovered_from_view": product["recovered_from_view"],
            "product_name": product["product_name"], "tagline": product["tagline"],
            "description": product["description"],
            "upvotes": product["upvotes"] if product["upvotes"] is not None else "", "comments": product["comments"] if product["comments"] is not None else "",
            "reviews_count": product["reviews_count"] if product["reviews_count"] is not None else "",
            "reviews_rating": product["reviews_rating"] if product["reviews_rating"] is not None else "",
            "created_at": product["created_at"], "featured_at": product["featured_at"],
            "product_hunt_url": product["product_hunt_url"], "product_hunt_visit_url": product["product_hunt_visit_url"],
            "official_website_url": product["official_website_url"],
            "thumbnail": json.dumps(product["thumbnail"], ensure_ascii=False, separators=(",", ":")),
            "media": json.dumps(product["media"], ensure_ascii=False, separators=(",", ":")),
            "product_links": json.dumps(product["product_links"], ensure_ascii=False, separators=(",", ":")),
            "topics": " | ".join(item["name"] for item in product["topics"]),
            "company_name": company["name"], "company_source_url": company["source_url"],
            "maker_names": " | ".join(item["name"] for item in makers), "maker_roles": " | ".join(item["role"] for item in makers),
            "maker_profile_urls": " | ".join(item["source_url"] for item in makers),
            "submitter_name": product["submitter"].get("name", ""),
            "submitter_profile_url": product["submitter"].get("source_url", ""),
            "pages_checked": " | ".join(product["pages_checked"]),
            "contact_status": product["contact_status"],
            "enrichment_status": product["enrichment_status"], "contact_form_url": product["contact_form_url"],
            "public_channels": " | ".join(f"{item['type']}:{item['value']}" for item in channels),
            "public_channel_sources": " | ".join(item["source_url"] for item in channels),
            "last_verified_at": product.get("last_verified_at", ""), "notes": product["notes"],
        }
        for email in product["emails"] or [None]:
            row = dict(common)
            row.update({
                "email": email["email"] if email else "", "email_type": email["type"] if email else "",
                "contact_name": email["contact_name"] if email else "", "email_source_url": email["source_url"] if email else "",
                "source_context": email["source_context"] if email else "", "email_source_tier": email["source_tier"] if email else "",
                "confidence": email["confidence"] if email else "",
            })
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_csv", type=Path)
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
    rows = export_rows(data)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Validated {len(data['products'])} products and wrote {len(rows)} CSV rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
