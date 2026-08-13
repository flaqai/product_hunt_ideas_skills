# Public contact enrichment playbook

## Contents

- Research order
- Evidence tiers
- Identity and team rules
- First-party website pass
- Official ecosystem and search pass
- Stopping rules
- Prohibited methods

## Research order

Collect and validate the full daily inventory before contact work. Enrich Featured products first unless the user explicitly requests all products or a different segment. Never drop a product because its site or contact data is unavailable.

For each attempted product:

1. Resolve the Product Hunt Visit redirect to the official domain.
2. Verify maker identities and roles from the visible Product Hunt launch page.
3. Inspect first-party contact, company, team, legal, docs, and support pages.
4. Follow professional profiles linked from those first-party pages.
5. Use the official site's visible navigation or its visible search UI to locate a public page; open and verify the page before saving a fact.
6. Save exact source URLs, short paraphrased evidence context, confidence, and verification time.

## Evidence tiers

Prefer evidence in this order:

1. `official_legal`: terms, privacy, imprint, regulatory disclosure, warranty.
2. `official_site`: homepage, About, Team, Contact, Support, Sales, Press, Careers, docs, blog.
3. `official_product_store`: official app/browser/package marketplace profile.
4. `official_linked_profile`: GitHub, LinkedIn, X, Discord, booking profile linked by a verified first-party source.
5. `product_hunt`: visible Maker profile/label or explicit Maker launch comment.
6. `public_code_host`: public repository or profile; contributors remain contributors.
7. `company_registry`: official regulator/government record.
8. `credible_secondary`: reputable investor, accelerator, or press profile when first-party evidence is absent.

Repeated weak sources do not become first-party evidence.

## Identity and team rules

- Product Hunt `makers` are launch makers. Keep their profile URL as evidence.
- The post submitter/user, hunter, commenter, investor, advisor, and repository contributor are not automatically makers, founders, employees, or company contacts.
- Save “Founder”, “CEO”, “Developer”, or similar roles only when the Product Hunt headline, official Team/About page, or another admissible source explicitly supports it.
- Keep company identity separate from product/brand name. Prefer a legal page for the legal entity and an About page for a trading name.

## First-party website pass

Check the smallest useful public link graph:

- homepage, About, Team, Contact, Support, Sales, Press, Careers
- Terms, Privacy, Imprint, Legal, Disclosures, Warranty
- Docs, Help, Blog, Changelog, Status
- `sitemap.xml`, `robots.txt`, and `/.well-known/security.txt` during the manual verification pass

Record only intentionally public information: visible email text, `mailto:` links, labeled `tel:` numbers, contact/booking forms, Organization JSON-LD, and linked professional/social profiles. Do not submit forms. Treat security contacts as security-only.

Browser research is a visible-page discovery pass, not automatic proof. Review unexpected domains, personal addresses, generic footer text, redirects, and ambiguous company names before outreach use.

## Official ecosystem and search pass

Follow first-party-linked GitHub organizations, LinkedIn pages, X profiles, Discord invites, stores, and package registries in the in-app browser. Accept a public profile email only when the rendered visible profile intentionally exposes it. Do not mine commits.

When the official site exposes search, use focused queries such as:

```text
site:official-domain (contact OR support OR sales OR press OR team OR about)
site:official-domain (privacy OR terms OR imprint OR legal)
"Exact Product Name" (founder OR co-founder OR maker OR CEO OR CTO)
"Known Maker" "Exact Product Name"
```

Search snippets alone are not evidence. Open the result and confirm identity.

## Stopping rules

Stop when one condition is met:

- one high-confidence business email plus two corroborated professional channels
- one contact/booking route plus two verified professional profiles and no public email
- all relevant public first-party pages, linked profiles, and focused searches were checked without more results
- further work requires login, CAPTCHA, access-control bypass, a data broker, guessing, or personal-data mining

Set an explicit status and document checked pages or the blocker.

## Prohibited methods

- guessed/permuted email addresses or deliverability claims
- SMTP probing, catch-all testing, or test messages
- hidden app data, private repos, leaks, breaches, or login/paywall bypass
- WHOIS personal records as outreach contacts
- Git commit/patch metadata and noreply addresses
- people-search/data-broker enrichment without explicit user request and a compliant approved workflow
- reclassifying hunters, commenters, investors, or contributors as team members without evidence
