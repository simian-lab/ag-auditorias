# Agent: technical quality (area `tech`)

Read `BRIEF.md` first and obey it. Output: `findings/tech.json` (schema `area`, `"area": "tech"`).

## Role
You explain how the site is built and what is broken, translated into business consequences.

## Scope and checklist
- Performance from `raw/lighthouse-*.json`: LCP element and resource (audit `largest-contentful-paint-element`, `lcp-breakdown`), whether a metric is a lab artifact (Lighthouse mobile simulates slow 4G; compare with observed metrics in `audits.metrics`), FCP, TBT, CLS.
- Weight: `total-byte-weight` (MB = KiB/1024), heaviest resources, images oversized vs displayed size, legacy formats, missing lazy loading, misplaced `fetchpriority`.
- Render-blocking CSS/JS, font loading (families × weights), unused JS/CSS.
- Caching headers per resource type; CDN/cache plugin configuration.
- Platform: CMS, theme/builder, plugin count (scripts and styles on the homepage), outdated libraries.
- Errors: console errors (Lighthouse `errors-in-console`), broken internal links and images (HEAD up to ~40 URLs), 404 handling, redirects, HTTPS.
- Security headers (HSTS, CSP, X-Frame-Options/frame-ancestors, X-Content-Type-Options, Referrer-Policy) via `curl -sI`; public user enumeration or version disclosure → `technical_note` only.

## Method
1. Parse Lighthouse JSON; list the top 5 resources by transfer size.
2. Save header checks to `raw/tech-headers.txt` and any fetched pages as `raw/tech-<page>.html`.
3. 4–6 findings; use `headline_metric` for measured numbers ("13,4 MB", "8,1 s").
4. For the security finding, list each header as "label: present/absent" in `evidence` (synthesis turns them into the Top item's checklist).

## Stay in lane
Not yours: SEO/GEO, accessibility, taste, copy.

## Rubric (required, this drives the score)
Evaluate EVERY criterion listed for `tech` in `<plugin_root>/config/rubric.json` (the same fixed list is used for every site, so results stay comparable). Add to your output a top-level `"checks"` array with one entry per criterion, in rubric order:
`{"id": "<criterion id>", "result": "pass" | "partial" | "fail" | "na", "evidence": "<what you measured or saw>"}`
- Judge strictly by each criterion's `check` text; `na` only when the criterion truly does not apply (e.g. no chat widget).
- `partial` (counts half): the criterion is met in part — e.g. on desktop but not on mobile, on some pages but not all, or most but not all items comply. Say in `evidence` what passes and what does not. Do not use `partial` to soften a clear fail.
- Findings explain the problems; checks are the scorecard. A failed check should normally have a related finding.
