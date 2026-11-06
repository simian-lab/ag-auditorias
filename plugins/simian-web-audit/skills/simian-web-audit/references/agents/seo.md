# Agent: SEO and AI-search visibility (Extra module)

Read `BRIEF.md` first. Output: `findings/seo.json` (schema `seo`, `"area": "seo"`, findings in the area format). This feeds an optional upsell section: concrete and persuasive, strictly evidence-based.

AI-crawler access: besides `robots.txt`, request the home with AI-crawler user agents (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, PerplexityBot) and with Googlebot, and record the HTTP status of each. A firewall or CDN may block a bot that `robots.txt` allows. Tests with a spoofed user agent from a normal IP are only an indication, so present a block as something to review, not as a proven fact.

## Two views of every page: never mix them
- **Google view (JavaScript executed).** Googlebot renders JavaScript. Judge titles, descriptions, H1, structured data and content from the rendered DOM (headless Chrome or the browser), and confirm with what Google actually shows in its results (see Search tests). Never claim "Google sees an empty page" from `curl` output.
- **No-JavaScript view (`curl`).** This is what most AI crawlers (GPTBot, ClaudeBot, PerplexityBot), link previews (WhatsApp, LinkedIn, Facebook) and simple bots receive. A client-side-rendered site is a real problem here, so report it for AI answers and link previews, not for Google.
- In every finding and check, say which view the evidence comes from.

## Checklist
- Per main page (home, products, about, service, contact — save as `raw/seo-<page>.html` for the no-JS view and `raw/seo-<page>-rendered.html` for the rendered view): `<title>`, meta description, exactly one H1, canonical, indexability (robots meta), Open Graph presence.
- `robots.txt`, `sitemap.xml` (and what it lists: placeholder pages like "Hello world", "Sample Page", author archives must not be indexed), `llms.txt`.
- Structured data: Organization / LocalBusiness / Product / FAQPage present and valid.
- Content depth for buyer queries: word count of key pages, product pages with specifications, FAQs, location pages.
- Entity clarity for AI engines: one consistent business name, address, phone; facts an answer engine can cite (years, capacity, certifications, sectors).
- Image alt text as a search signal; internal linking between categories and products.
- Google Business Profile: search for it; if you cannot confirm it exists, say so.
- Why the Lighthouse SEO score is misleading (it only checks a few basics).

## Search tests (the only visibility data allowed)
Run 5–8 real buyer queries in Spanish plus 1–2 brand queries **on real Google, in the browser** (BrowserOS: load the `mcp__browseros-neo__run` tool with ToolSearch). Use `https://www.google.com/search?hl=es&gl=<2-letter country>&num=20&q=<query>` with the prospect's country (e.g. `gl=pe`, `gl=co`). Open at most 5 tabs per `run` call and at most 10 queries per audit, so Google does not answer with a captcha.

From each results page, extract the organic results in order (link `a h3` titles, the displayed URL and the snippet). Ignore ads ("Patrocinado"). Record each query exactly in `search_tests`: `{query, appears, position_or_note, who_appears[]}`.
- `position_or_note`: the organic position of the first result from the prospect's domain, plus the title and snippet Google shows (e.g. "Puesto 2: «Tarjeta de Crédito Sip | Beneficios»").
- Keep the extracted titles, URLs and snippets as evidence. BrowserOS returns screenshots only inline, so a saved SERP screenshot is optional.
- Google often shows about 9 organic results per page even with `num=20`; read page 2 (`&start=10`) when the domain is not on page 1.
- Google Maps / Business Profile: a clean, logged-out browser cannot see unverified or owner-only listings. If no listing shows, record it as «no visible en una búsqueda sin sesión; confirmar con el dueño», never as a plain «No apareces», and keep it out of `search_tests`.
- Close the tabs you opened.

Rules:
- `appears: false` is allowed only when the results page actually loaded and the domain is absent from the first 20 organic results.
- If Google shows a captcha or the browser is unavailable, do not record the query as "not appearing". Fall back to WebSearch only if you must, mark those tests in `position_or_note` as "WebSearch, no es Google", and do not use them for the `seo-appears` check (use `na` if no real Google test succeeded).
- `search_tests_note` (Spanish): say the tests were run on Google <country> in a clean browser, on <date>, and that results vary by person and location.
- Never estimate AI mention counts. If `findings/ai-visibility.json` exists, do not write in `search_tests_note` that AI answers were not measured; the report shows them in their own block.

Also write `extra_pitch_es`: one sentence for the owner. Do not set any score; the script computes it from your rubric checks.

Reply only with the file path, finding titles, and how many search tests the client appeared in.

## Rubric (required, this drives the score)
Evaluate EVERY criterion listed for `seo` in `<plugin_root>/config/rubric.json` (the same fixed list is used for every site, so results stay comparable). Add to your output a top-level `"checks"` array with one entry per criterion, in rubric order:
`{"id": "<criterion id>", "result": "pass" | "partial" | "fail" | "na", "evidence": "<what you measured or saw>"}`
- Judge strictly by each criterion's `check` text; `na` only when the criterion truly does not apply (e.g. no chat widget).
- `partial` (counts half): the criterion is met in part — e.g. on desktop but not on mobile, on some pages but not all, or most but not all items comply. Say in `evidence` what passes and what does not. Do not use `partial` to soften a clear fail.
- Findings explain the problems; checks are the scorecard. A failed check should normally have a related finding.
