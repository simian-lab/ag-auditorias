# Agent: competitor benchmark (persuasion wave)

Read `BRIEF.md` first. Output: `findings/benchmark.json` (schema `benchmark`), screenshots `screenshots/bench-<slug>.png`, Lighthouse files `raw/bench-<slug>-lh.json`.

## Task
1. Competitors: use the ones given in the brief context; otherwise find 3 real local competitors with live websites (WebSearch). Prefer comparable companies plus at most one big reference. Record `why_competitor`.
2. First screen of each competitor and of the client: headless Chrome `--window-size=1440,900 --virtual-time-budget=6000`. Look at every PNG; if a cookie wall or bot check covers it, accept/close it with a browser tool or retry once, otherwise note it.
3. Five-second test per site, judged by the SAME rule for every site:
   - `what`: is it clear what they sell?
   - `for_whom`: does it say for whom/which sector?
   - `text_headline`: is the main message real text (not inside an image)?
   - `trust_proof`: years, clients, certifications or numbers visible in the first screen?
   - `quote_cta`: a visible button to request a quote/contact sales (a floating chat widget alone does NOT count).
4. Lighthouse mobile for each competitor: `lighthouse URL --quiet --chrome-flags="--headless=new" --form-factor=mobile --output=json --output-path=raw/bench-<slug>-lh.json`; record performance, accessibility, seo and `total_mb` (KiB/1024). For the client reuse `raw/lighthouse-mobile.json`.
5. Each competitor gets a `slug` (lowercase, hyphens) and a one-line Spanish `notes_es`. The client object has the same fields as a competitor, with `"slug": "client"`, its `url`, and `"screenshot": "screenshots/desktop-viewport.png"`.
6. `takeaway_es`: one sharp, truthful Spanish sentence a business owner would feel.

Reply only with the file path and the takeaway.
