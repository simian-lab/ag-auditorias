# Audit brief — bedbathandbarrel.com

Audit folder: the folder that contains this file. All paths below are relative to it.
Site: https://bedbathandbarrel.com/
Business context: business: not provided — infer from the site and say it is inferred (appears to be an outdoor furniture store, WooCommerce, Spanish); competitors: not provided — find them yourself (búscalos tú); never invent

## Purpose
Simian produces a short "Top N improvements" micrositio for a prospect, presented in person. The reader is the business owner, non-technical. Each finding must be explainable in one plain sentence about business impact.

## Evidence already collected (read, do not re-collect unless needed)
- raw/home.html — homepage HTML
- raw/lighthouse-mobile.json, raw/lighthouse-desktop.json — Lighthouse reports
- screenshots/desktop-viewport.png (1440x900)
- screenshots/desktop-fullpage.jpg, screenshots/mobile-fullpage.jpg (from Lighthouse)

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
