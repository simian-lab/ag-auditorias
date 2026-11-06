# Audit brief — {{domain}}

Audit folder: the folder that contains this file. All paths below are relative to it.
Site: {{url}}
Business context: {{context}}

## Purpose
Simian produces a short "Top N improvements" micrositio for a prospect, presented in person. The reader is the business owner, non-technical. Each finding must be explainable in one plain sentence about business impact.

## Evidence already collected (read, do not re-collect unless needed)
{{evidence_index}}

You may fetch other pages of the site with curl or take extra screenshots with headless Chrome
("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --screenshot=... --window-size=W,H URL).
Never take a mobile screenshot with a window narrower than 500px (Chrome does not apply the mobile layout): use the Lighthouse mobile screenshot or device emulation.
Lighthouse screenshots named `.jpg` may be WebP internally; convert with `sips` before cropping.
Save any extra evidence under raw/ or screenshots/ with a prefix of your area name.

## Rules
- Evidence only. Every finding cites concrete evidence (selector, measured value, Lighthouse audit id, screenshot + coordinates). NEVER invent numbers, percentages of users lost, competitor data, search results or AI answers.
- Prefer 5–8 strong findings over many weak ones. Merge duplicates.
- Plain-language fields (title, summary, now, fix, why) in neutral professional Spanish for a non-technical owner, addressing them as "tú". Technical detail goes in `evidence` and `technical_note` (English OK).
- Sensitive details (exposed usernames, internal paths, credentials) go only in `technical_note`, never in client-facing fields.
- Page weight: MB = KiB / 1024.
- Do not edit files outside your own output file and your prefixed evidence files.
- Scores are computed by a script from the fixed rubric checks (`config/rubric.json`); do not invent an area score.

## Verification rules (past audits failed on each of these)
- Real source, not a proxy. Visibility in Google is checked on real Google; the site's behavior is checked on the live rendered page. A search tool, a directory or a third-party listing is a lead to confirm, not proof; if you cannot confirm it, mark it `[dato por confirmar]`.
- Rendered view vs. no-JavaScript view. Users and Google see the page after JavaScript runs (judge it with headless Chrome or the browser). `curl` shows only what link previews and most AI crawlers get. Never describe the `curl` HTML as what users or Google see.
- Lab metrics are not fixed facts. Lighthouse simulated values (LCP, FCP, TBT) vary between runs: run it at least twice for any number you headline, give a range or "más de X", and say it is a simulation. Observed (unthrottled) values come from a desktop machine emulating a phone; never call them "en un celular" or "usuarios reales".
- No generalizations from shared CSS. Before writing "todos", "ninguno" or "cada", check each element (e.g. every main button's real colors), and keep exceptions such as the 3:1 contrast minimum for large text.
- Measure interactions for real. Keyboard order with real Tab presses (CDP `Input.dispatchKeyEvent`), focus styles on the focused element, console errors on more than one load (report a range if the count varies).
- Root cause from the original asset. Before blaming a file (broken logo, wrong image), open the original asset and compare it with the rendered result; CSS filters, cropping or lazy loading are often the real cause.
- Business framing must match the evidence. If only one tool or element fails, name it; do not widen it ("tus campañas no se miden" when only one marketing tool fails).
- Content that changes per visit (carousels, A/B tests, pop-ups) must be stated as such, and a competitor's metric dominated by a pop-up or cookie wall must be flagged.
- User-supplied screenshots may be stitched; reproduce an artifact live before reporting it.

## Output — area agents write exactly one JSON file: findings/<area>.json
{
  "area": "ux | a11y | visual | tech",
  "findings": [
    {
      "id": "<area>-1",
      "title": "≤ 9 words, plain Spanish, states the problem",
      "summary": "one sentence, the consequence for the business",
      "now": "what happens today (concrete)",
      "fix": "what we propose (concrete, outcome-oriented)",
      "why": "why it matters for sales/trust/reach, one sentence",
      "impact": 1-5,
      "effort": "Bajo | Medio | Alto",
      "headline_metric": "optional big number with unit, ONLY if measured",
      "evidence": ["..."],
      "technical_note": "...",
      "pin": {"screenshot": "desktop-viewport.png | desktop-fullpage.jpg | mobile-fullpage.jpg", "x_pct": 0-100, "y_pct": 0-100} or null
    }
  ],
  "checks": [{"id": "<rubric criterion id>", "result": "pass | partial | fail | na", "evidence": "..."}]
}
Validate with: python3 -I <plugin_root>/scripts/validate_findings.py <audit folder>
When done, reply with only: the file path and the titles of your findings.
