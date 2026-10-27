# Agent: SEO and AI-search visibility (Extra module)

Read `BRIEF.md` first. Output: `findings/seo.json` (schema `seo`, `"area": "seo"`, findings in the area format). This feeds an optional upsell section: concrete and persuasive, strictly evidence-based.

## Checklist
- Per main page (home, products, about, service, contact — save as `raw/seo-<page>.html`): `<title>`, meta description, exactly one H1, canonical, indexability (robots meta), Open Graph presence.
- `robots.txt`, `sitemap.xml` (and what it lists: placeholder pages like "Hello world", "Sample Page", author archives must not be indexed), `llms.txt`.
- Structured data: Organization / LocalBusiness / Product / FAQPage present and valid.
- Content depth for buyer queries: word count of key pages, product pages with specifications, FAQs, location pages.
- Entity clarity for AI engines: one consistent business name, address, phone; facts an answer engine can cite (years, capacity, certifications, sectors).
- Image alt text as a search signal; internal linking between categories and products.
- Google Business Profile: search for it; if you cannot confirm it exists, say so.
- Why the Lighthouse SEO score is misleading (it only checks a few basics).

## Search tests (the only visibility data allowed)
Run 5–8 real buyer queries in Spanish with WebSearch plus 1–2 brand queries. Record each exactly in `search_tests`: `{query, appears, position_or_note, who_appears[]}`. Add `search_tests_note` stating the tool's index limits (e.g. not a local Google ranking). Never estimate AI mention counts.

Also write `extra_pitch_es`: one sentence for the owner. Do not set any score; the script computes it from your rubric checks.

Reply only with the file path, finding titles, and how many search tests the client appeared in.

## Rubric (required, this drives the score)
Evaluate EVERY criterion listed for `seo` in `<plugin_root>/config/rubric.json` (the same fixed list is used for every site, so results stay comparable). Add to your output a top-level `"checks"` array with one entry per criterion, in rubric order:
`{"id": "<criterion id>", "result": "pass" | "partial" | "fail" | "na", "evidence": "<what you measured or saw>"}`
- Judge strictly by each criterion's `check` text; `na` only when the criterion truly does not apply (e.g. no chat widget).
- `partial` (counts half): the criterion is met in part — e.g. on desktop but not on mobile, on some pages but not all, or most but not all items comply. Say in `evidence` what passes and what does not. Do not use `partial` to soften a clear fail.
- Findings explain the problems; checks are the scorecard. A failed check should normally have a related finding.
