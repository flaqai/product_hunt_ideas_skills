# Product and contact data schema

## Contents

- Root fields
- Product fields
- Evidence objects
- Enumerations
- CSV behavior

## Root fields

The canonical UTF-8 JSON uses `schema_version: 2` and contains:

```json
{
  "schema_version": 2,
  "leaderboard_date": "2026-08-13",
  "day_timezone": "America/Los_Angeles",
  "leaderboard_url": "https://www.producthunt.com/leaderboard/daily/2026/8/13",
  "inventory_source": "product_hunt_in_app_browser",
  "inventory_source_tier": "official_visible_webpage",
  "accessed_at": "2026-08-13T08:30:00-07:00",
  "data_status": "in_progress",
  "collection_scope": "all",
  "sort_order": "visible_all_view_order",
  "inventory_complete": true,
  "browser_collection": {
    "all_end_reached": true,
    "all_stable_passes": 2,
    "all_displayed_total": 87,
    "all_final_recheck_matches": true,
    "featured_end_reached": true,
    "featured_stable_passes": 2,
    "featured_displayed_total": 18,
    "detail_page_count": 87
  },
  "source_row_count": 87,
  "duplicate_row_count": 0,
  "expected_product_count": 87,
  "extracted_product_count": 87,
  "expected_featured_count": 18,
  "extracted_featured_count": 18,
  "expected_unfeatured_count": 69,
  "extracted_unfeatured_count": 69,
  "products": []
}
```

`data_status` is `in_progress` for a complete current-day browser snapshot, `completed` for a reconciled past date, or `partial` when browser completeness checks fail. Export/audit accept only complete normalized inventories.

`collection_scope` is normally `all`. It becomes `official_view_union` only when two verified official passes show a numbered Featured product missing from All; the canonical inventory then preserves the union and its per-product observation evidence. `displayed_rank` and `displayed_featured_rank` must each be unique positive values in their view; gaps are evidence, not a reason to renumber the source.

## Product fields

Each product contains inventory facts and an independent enrichment state:

```json
{
  "rank": 1,
  "displayed_rank": 1,
  "product_hunt_id": "",
  "slug": "example-product",
  "is_featured": true,
  "featured_rank": 1,
  "displayed_featured_rank": 1,
  "featured_rank_source": "visible_featured_view_position",
  "observed_in_all": true,
  "observed_in_featured": true,
  "recovered_from_view": "",
  "product_name": "Example Product",
  "tagline": "A concise tagline",
  "description": "Product Hunt description",
  "upvotes": 523,
  "comments": 42,
  "reviews_count": 2,
  "reviews_rating": 4.5,
  "created_at": "2026-08-13T07:01:00-07:00",
  "featured_at": "2026-08-13T08:00:00-07:00",
  "product_hunt_url": "https://www.producthunt.com/posts/example-product",
  "product_hunt_visit_url": "https://example.com/",
  "official_website_url": "https://example.com/",
  "thumbnail": {"type": "image", "url": "https://...", "videoUrl": null},
  "media": [{"type": "image", "url": "https://...", "videoUrl": null}],
  "topics": [{"name": "Developer Tools", "slug": "developer-tools", "url": "https://www.producthunt.com/topics/developer-tools"}],
  "product_links": [{"type": "Website", "url": "https://example.com/"}],
  "developers": [{
    "product_hunt_user_id": "789",
    "name": "Alex Example",
    "username": "alex",
    "role": "Maker",
    "headline": "Founder at Example",
    "source_url": "https://www.producthunt.com/@alex",
    "website_url": "https://alex.example",
    "x_url": "https://x.com/alex"
  }],
  "submitter": {"name": "Sam Submitter", "role": "Submitter", "source_url": "https://www.producthunt.com/@sam"},
  "company": {"name": "Example Labs, Inc.", "source_url": "https://example.com/terms", "confidence": "high"},
  "enrichment_status": "partial",
  "contact_status": "found",
  "contact_form_url": "https://example.com/contact",
  "last_verified_at": "2026-08-13T08:45:00-07:00",
  "emails": [],
  "public_channels": [],
  "pages_checked": [],
  "notes": ""
}
```

Leave unavailable text empty, numeric values null, and arrays empty. Inventory-only products use `enrichment_status: not_started` and `contact_status: not_checked`.

## Evidence objects

Company requires `name`, `source_url`, and `confidence`.

Email requires:

```json
{
  "email": "hello@example.com",
  "type": "general",
  "contact_name": "",
  "source_url": "https://example.com/contact",
  "source_context": "Visible public business email on Contact page",
  "source_tier": "official_site",
  "is_publicly_listed": true,
  "confidence": "high"
}
```

Public channel requires:

```json
{
  "type": "linkedin",
  "value": "https://www.linkedin.com/company/example",
  "label": "Company LinkedIn",
  "owner": "Example Labs, Inc.",
  "source_url": "https://example.com/about",
  "source_context": "Linked from official About page",
  "source_tier": "official_linked_profile",
  "confidence": "high"
}
```

## Enumerations

- `enrichment_status`: `not_started`, `partial`, `enriched`, `blocked`
- `contact_status`: `found`, `contact_form_only`, `not_publicly_listed`, `site_unavailable`, `not_checked`
- confidence: `high`, `medium`, `low`
- email type: `general`, `support`, `sales`, `press`, `founder_developer`, `security`, `other`
- channel type: `contact_form`, `booking`, `phone`, `github`, `linkedin`, `x`, `discord`, `app_store`, `other`
- source tier: `official_legal`, `official_site`, `official_product_store`, `official_linked_profile`, `product_hunt`, `public_code_host`, `company_registry`, `credible_secondary`

Never use low confidence to store a guessed email.

## CSV behavior

Generate CSV with `scripts/export_contacts.py`. It emits one row per verified email. Products without an email still emit one row with their explicit contact status, preserving full inventory coverage. Product details and nested media/link fields are retained in flat or JSON-string columns; maker names/profile URLs and public channels remain pipe-delimited. JSON remains the canonical nested artifact.
