# Synthesis: from area findings to `findings/top10.json`

The orchestrator does this itself (no agent), after wave 1 validates.

## Steps
1. Read `findings/{ux,a11y,visual,tech}.json`.
2. Drop findings whose evidence is unreliable (e.g. based on a mobile screenshot taken with a narrow Chrome window, unverified assumptions). Note what you dropped in your hand-off message.
3. Merge duplicates across areas (the same root problem reported by several agents, e.g. "headline is an image" from ux, a11y and visual). Keep the strongest wording and evidence; list all ids in `src`.
4. Rank by business impact (`impact`, then breadth of evidence, then low effort). Keep at most 10 items; never pad with weak items. Fewer than 5 is acceptable but say so.
5. For each item write, in neutral Spanish addressing the owner as "tú":
   - `t`: sharp headline with stance, ≤ 8 words (use `ui-critique.json` `sharp_headlines` when available).
   - `t_plain`: plain descriptive title (used in tables).
   - `s`, `now`, `fix`, `why`; `c` ∈ `ux|a11y|vis|tec`; `imp`; `eff`.
   - `stage`: 1 = quick wins (≤ 2 weeks, low effort, high impact), 2 = "que entiendan qué vendes" (content/structure), 3 = "que te elijan" (trust, brand, design system).
   - `shot`: `{img, x, y}` pointing to the screenshot and percentage position where the problem is visible (`desktop-fullpage.jpg`, `mobile-fullpage.jpg`, `desktop-viewport.png` or another file in `screenshots/`), or `checks` for non-visual items (e.g. security headers: `[["HSTS","no"], ...]`), or `shot: null`.
6. `big_stat`: the single most painful MEASURED number (e.g. page weight, LCP), with `value`, optional `count_to`/`suffix`, `headline`, `explain` (plain Spanish "¿Qué significa?"), optional `grid_pct` + `grid_legend` for the 100-cell grid, and `source`.
7. Fill `client` (clean company name), `domain`, `date` ("Mes AAAA" in Spanish).
8. Validate: `python3 -I <plugin_root>/scripts/validate_findings.py <audit>`.
