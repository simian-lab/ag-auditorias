# Agent: online presence (Extra module)

Read `BRIEF.md` first. Output: `findings/presence.json` (schema `presence`).

## Blocks
1. `serp`: `today` = how the home and products pages appear as a Google result: real `<title>`, `meta_description` (or null — then Google improvises; never guess the text), URL breadcrumb. `proposed` = title ≤ 60 chars and description ≤ 155 chars, truthful, using only facts from the site.
2. `share_preview`: real Open Graph / Twitter tags found (verify home and products); what WhatsApp/LinkedIn show today; `proposed` with `og:title`, `og:description`, `og:image` (a real image URL from the site that works at 1200×630). Download that image, convert/crop to a light JPEG at `screenshots/og-source.jpg` and set `"og_image_local": "og-source.jpg"`.
3. `ai_answer`: AEO only (being recommended/cited by answer engines). Do NOT query AI engines yourself and NEVER write an answer from your own knowledge; real answers come from the OpenSEO step. Set `"status": "not_collected"` and fill `aeo_fixes`: 5–6 concrete, plain-Spanish improvements tied to evidence (FAQ page, Organization/LocalBusiness schema, fact sheet with verifiable figures, one page per product, consistent contact data, `llms.txt`).
4. `nap`: compare business name, phones, email, address, hours across every site page, the chat widget config, structured data and public listings found with WebSearch. Rows `{field, source, value}` and `inconsistencies` (plain Spanish sentences; empty list if none — the report hides the block then).

Reply only with the file path and the number of NAP inconsistencies.
