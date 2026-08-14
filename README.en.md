# Product Hunt Daily Skill

<p align="center"><strong>Collect a dated Product Hunt inventory, product details, launch teams, and publicly listed professional contact routes through the Codex in-app browser—without a Product Hunt API token.</strong></p>

<p align="center">
  <a href="README.md">简体中文</a> · <strong>English</strong> ·
  <a href="i18n/ja-JP.md">日本語</a> · <a href="i18n/es-ES.md">Español</a> ·
  <a href="i18n/fr-FR.md">Français</a> · <a href="i18n/de-DE.md">Deutsch</a> ·
  <a href="i18n/ko-KR.md">한국어</a> · <a href="i18n/pt-BR.md">Português</a> ·
  <a href="i18n/README.md">12 languages</a>
</p>

![Languages](https://img.shields.io/badge/languages-12-00b894)
![Browser only](https://img.shields.io/badge/acquisition-in--app_browser-6c5ce7)
![API token](https://img.shields.io/badge/Product_Hunt_API_token-not_required-0984e3)
![License](https://img.shields.io/badge/license-MIT-blue)

## What this project does

`product-hunt-daily` is a reusable Codex Skill for researching products launched on a specific Product Hunt day. It reads visible official pages in the in-app browser and does not require an API token or use a third-party leaderboard to fill gaps.

A complete run can collect:

- official All and Featured inventories;
- names, taglines, descriptions, votes, comments, topics, and Visit URLs;
- explicitly displayed Launch Team, Makers, and Hunter/Submitter roles;
- public business email, contact forms, GitHub, LinkedIn, X, Discord, and other professional channels;
- auditable JSON, CSV, Markdown, contact coverage, and source ledgers;
- validated real-world examples indexed by Product Hunt date.

## Why Product Hunt matters

Product Hunt can support product discovery, competitor research, launch feedback, early visibility, founder and ecosystem discovery, partnership research, content planning, and long-term trend monitoring. Its ranking is not proof of retention, revenue, product quality, or durable success; use leaderboard evidence together with websites, comments, product progress, and independent judgment.

## Quick start

Copy [`product-hunt-daily`](product-hunt-daily/) into your Codex Skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R product-hunt-daily ~/.codex/skills/product-hunt-daily
```

Example request:

```text
Use the product-hunt-daily Skill and the in-app browser to collect today's complete Product Hunt All and Featured inventories, open every product for launch-team details, check official public contact routes, and export JSON, CSV, and Markdown.
```

“Today” is resolved in Product Hunt's `America/Los_Angeles` calendar, which may differ from your local date.

## Data integrity

- Preserve the displayed Product Hunt rank separately from the normalized export position.
- Exclude unnumbered promoted cards.
- Require repeated All/Featured checks and complete detail-page coverage.
- Use a guarded official-view union only when a persistent cross-view discrepancy is recorded.
- Treat Product Hunt launch members as launch roles, not a complete company organization chart.
- Collect only intentionally public professional contacts; never guess email patterns or submit forms.
- Preserve evidence URLs, verification time, confidence, pages checked, and blockers.

## Real examples

<!-- examples-table:start -->
| Date | Status | Visible products | Featured | Detail pages | Contact checks | Public email | Example |
|---|---|---:|---:|---:|---:|---:|---|
| 2026-08-12 | completed | 18 | 17 | 18/18 | 18/18 | 5 | [Open](examples/2026-08-12/) |
<!-- examples-table:end -->

Browse the [dated example index](examples/README.md) or the [machine-readable index](examples/index.json). A validated example includes the raw browser capture, canonical JSON, CSV, readable list, contact audit, and source ledger.

## Product Hunt mutual-support WeChat community

People preparing a Product Hunt launch or exchanging launch feedback can add WeChat **aihelloleo** with the note **Product Hunt**. The community currently includes **3 mutual-support groups** and **1,000+ members**. Participation should focus on authentic feedback, experience sharing, and legitimate support—not fake accounts, bots, paid votes, or ranking manipulation.

## Contributing and license

New validated dates, browser compatibility fixes, schema improvements, translations, and data-quality cases are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md). The project is available under the [MIT License](LICENSE).

## About Flaq AI

[Flaq AI](https://flaq.ai/about/) is a multi-model AI platform operated by FLAQ AI PTE. LTD. It brings image, video, audio, and language models into one platform for model discovery, comparison, API integration, and production workflows.

Product Hunt teams can use Flaq AI to create launch images, demos, social assets, and advertising creative; prototype multimodal product features; compare models; and turn launch feedback into updated tutorials and campaigns. Visit [Flaq AI](https://flaq.ai/) or read the [company and platform overview](https://flaq.ai/about/).

## Flaq AI Affiliate Program

Developers, creators, educators, agent builders, and model reviewers can join the [Flaq AI Affiliate Program](https://flaq.ai/affiliate-program/) and create a personal referral link. As publicly listed on August 13, 2026, the program offers 20% on a referred user's first valid paid order and 10% on following valid paid orders within 60 days after registration. Attribution, refunds, chargebacks, risk review, and the active agreement affect final eligibility.

Terms can change. Check the official program before publishing, disclose the affiliate relationship clearly, and do not promise earnings or product results. See the [affiliate guide](docs/flaq-ai-affiliate-program.md).
