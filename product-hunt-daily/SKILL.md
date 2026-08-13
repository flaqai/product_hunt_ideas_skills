---
name: product-hunt-daily
description: Use the Codex in-app browser, without a Product Hunt API token, to collect a complete Product Hunt daily All inventory and Featured view, open every launch for full product details and maker/team profiles, follow official websites for publicly listed company contact routes, and normalize, validate, export, and audit JSON/CSV. Use for today's or a dated Product Hunt list, all launches rather than only Featured products, product research, maker/team discovery, founder or company contact research, lead lists, daily rankings, and Chinese Product Hunt reports.
---

# Product Hunt Daily

Use the Codex in-app browser as the only network acquisition surface. Do not request or use a Product Hunt API token. Do not replace the browser with `web` search, `curl`, `urllib`, a standalone browser, or an unofficial feed.

## Required references

- Read `references/browser-collection.md` before opening Product Hunt or collecting a date.
- Read `references/contact-enrichment-schema.md` before building the capture JSON.
- Read `references/contact-enrichment-playbook.md` before visiting official websites or collecting contacts.
- Read `references/wechat-markdown-template.md` only when writing a WeChat article.

## Browser collection workflow

1. Select the in-app browser exactly as required by the installed Browser skill and read its complete documentation before interaction. Keep research tabs in the background.
2. Resolve “today” to the current Product Hunt calendar date in `America/Los_Angeles`. State the exact date because it can differ from the user's timezone.
3. Open `https://www.producthunt.com/leaderboard/daily/YYYY/M/D`. Inspect a fresh DOM snapshot before locating controls; never rely on memorized CSS classes.
4. Confirm the `All` destination from visible UI, then click it or navigate directly to that confirmed URL in the same browser. Collect virtualized cards in scroll segments until two consecutive end checks add no new canonical Product Hunt URLs and the page is visibly at its end. Record printed rank numbers and sort by them; do not trust DOM order.
5. Select `Featured`, repeat the end checks, and record its visible order. Merge Featured membership into the All inventory by canonical Product Hunt URL. Never drop non-Featured products. If two verified official passes show a numbered Featured product absent from All, explicitly enable the documented official-view union recovery; preserve both views and never treat an unnumbered promoted card as a product.
6. Open every All product page in a bounded set of reusable tabs. For each launch, collect the visible name, tagline, description, votes, comments, reviews if shown, topics, media URLs, Product Hunt URL, official Visit URL, launch timestamp/status, all displayed Makers, and the separately labeled submitter/hunter when visible.
7. If the requested scope includes company or contact data, follow the official Visit destination in the same in-app browser and run the public-contact workflow. Do not submit forms, log in, or transmit data.
8. Save the browser observations in `browser-capture.json` using the schema reference. Normalize and validate them:

   ```bash
   python3 scripts/normalize_browser_capture.py browser-capture.json contacts.json --markdown all-products.md
   python3 scripts/export_contacts.py contacts.json contacts.csv
   python3 scripts/audit_contacts.py contacts.json contact-audit.md
   python3 scripts/write_sources.py contacts.json sources.md
   ```

9. Fix any validation error rather than weakening the completeness marker. Finalize browser tabs after extraction, retaining none unless the user explicitly needs a live page.

## Completeness rules

Call the inventory complete only when all conditions hold:

- All view reached a visible end and two consecutive saved URL arrays produced the same unique set.
- Every All row has a canonical Product Hunt URL and unique position.
- Featured view reached a visible end and its URLs are a subset of All, or a persistent official-view discrepancy is explicitly preserved by the guarded union recovery.
- Any displayed All/Featured total matches the extracted unique count.
- Every All product page was opened, has a matching detail record, and records that description, metrics, Topics, media, team, and Visit sections were checked.
- The second final All-view pass produces the same URL set as the first final pass.

For a live Product Hunt date, use `data_status: in_progress` even when the current browser snapshot reconciles. State that new products, ordering, votes, comments, and Featured decisions can still change. Use `partial` and explain the gap when sign-in, CAPTCHA, rate limiting, rendering failure, missing cards, or a count mismatch blocks completion.

## Team and contact rules

Treat Product Hunt Makers as the launch-team starting point, not the full company org chart. Keep Maker, submitter/hunter, founder, employee, advisor, and repository contributor roles distinct.

Collect only intentionally public professional contact information from visible webpages: company identity, business email, contact or booking form, labeled business phone, and official GitHub, LinkedIn, X, Discord, app-store, or other linked profiles. Preserve the exact visible source URL and a short evidence note.

Never guess email patterns, inspect hidden application state, mine Git commits or WHOIS personal data, bypass login/CAPTCHA/robots/paywalls, use leaked or brokered data, or send test messages. Keep security contacts classified as security-only.

## Deliverables

Create only the requested artifacts under `product-hunt-daily-YYYY-MM-DD/`:

```text
browser-capture.json   raw structured observations from visible browser pages
contacts.json          canonical complete inventory and nested evidence
all-products.md        readable full list
contacts.csv           detailed product/contact export
contact-audit.md       contact evidence coverage and research gaps
sources.md             Product Hunt and official-site evidence ledger
article.md             optional report
```

In the handoff, state the Product Hunt date/timezone, live/completed status, All and Featured counts, both end checks, detail-page coverage, contact scope, inaccessible pages, and output paths.

For a local run, write under `product-hunt-daily/output/product-hunt-daily-YYYY-MM-DD/`. When the user explicitly asks to publish a validated run as an open-source project example, copy the final artifacts to the repository-level `examples/YYYY-MM-DD/`, add a concise date-level `README.md`, then run `python3 product-hunt-daily/scripts/update_example_index.py`. This command strictly validates every dated `contacts.json` and rebuilds `examples/index.json`, `examples/README.md`, and the repository README date table. Never publish partial or unvalidated captures as completed examples.

## QA

- Confirm `inventory_source == product_hunt_in_app_browser` and no token/API path was used.
- Confirm URL-set/count reconciliation for All and Featured and complete detail-page coverage.
- Confirm `rank` is the All-view position and `featured_rank` is only the Featured-view position.
- Confirm every Maker/profile and every contact fact has a visible source URL.
- Confirm inventory-only contact rows remain `not_started`/`not_checked`.
- Confirm JSON normalization, CSV export, audit, and source-ledger scripts all exit successfully.
- Confirm the written report distinguishes a live browser snapshot from a frozen day-end result.
