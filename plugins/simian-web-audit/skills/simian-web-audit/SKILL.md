---
name: simian-web-audit
description: Audit a prospect's website for Simian and build a short, persuasive, offline Top N micrositio (UX, accessibility, visual, technical; optional SEO/AI-search Extra) for an in-person meeting. Use when the user gives a website URL and asks to audit it for a prospect or client ("audita este sitio", "auditoría web para un prospecto", "haz la auditoría de <url>").
---

# Simian web audit

Turn a prospect URL into `./audits/<domain-slug>/` with evidence, findings and `report/index.html`: a Top N (max 10) of improvements a Simian person presents in person. The report must persuade, not just inform. Never invent data.

## Paths (read first)
When this skill loads, Claude Code prints "Base directory for this skill: <dir>". The plugin root is two levels up from that directory (`<dir>/../..`). Call it `PLUGIN`. Run every script as `python3 -I "$PLUGIN/scripts/<script>.py" ...`. Audits are written under the current working directory (`./audits/`), never inside the plugin.

Talk to the user in their language (Spanish by default). Client-facing copy: neutral professional Spanish, "tú". Ask one question at a time.

## 1. Preflight
`python3 -I "$PLUGIN/scripts/preflight.py"` — if it prints hints, show them and stop until fixed.

## 2. Intake (one question at a time; skip what the user already gave)
1. Prospect URL (required).
2. Business context: what they sell, to whom, city/country (optional; else infer from the site and say it is inferred).
3. Extra screenshots/material (optional).
4. Competitors: names/URLs, or "búscalos tú".
5. Optional blocks, yes/no each:
   - Load comparison page ("Mira cómo carga tu sitio frente a tu competencia").
   - Extra module (SEO, AI-search visibility and online presence).
   - Only if Extra = yes: real AI answers via OpenSEO (paid; follow `references/openseo.md`).

Write the answers to two JSON files in the run directory's scratch (or `/tmp`), then:
`python3 -I "$PLUGIN/scripts/init_audit.py" <url> --context-json ctx.json --options-json opts.json`
with options `{"load_page": bool, "extra": bool, "openseo": bool}`. For an internal audit of a Simian-owned site, add `"internal": true`: the report hides the "Por qué Simian" cases section, and you skip the `redesign` agent. It prints the audit folder (`AUDIT`).

## 3. Evidence (once, shared by all agents)
`python3 -I "$PLUGIN/scripts/collect_evidence.py" "$AUDIT"` (HTML, Lighthouse mobile + desktop, screenshots). Look at `screenshots/desktop-viewport.png`; if it shows a cookie wall or bot check, tell the user.

## 4. Wave 1 — area agents, in parallel (one message, four Agent calls)
For each of `ux`, `a11y`, `visual`, `tech`: a general-purpose agent whose prompt says: read `$PLUGIN/skills/simian-web-audit/references/agents/<area>.md` and `$AUDIT/BRIEF.md`, work inside `$AUDIT`, and write `findings/<area>.json`. Include `PLUGIN` and `AUDIT` absolute paths in the prompt.
Then: `python3 -I "$PLUGIN/scripts/validate_findings.py" "$AUDIT"`; fix or re-ask an agent if invalid.

## 5. Synthesis (you, not an agent)
Follow `references/synthesis.md` to write `findings/top10.json`. Validate.

## 6. Wave 2 — persuasion agents, in parallel, only the selected blocks
- Always: `ui-critique`, `redesign`, `benchmark` (references in `references/agents/`).
- If Extra: `seo`, `presence`.
After `ui-critique` returns, copy its `sharp_headlines` into `top10.json` `t` fields (keep `t_plain`). Validate again.
If OpenSEO was selected: follow `references/openseo.md` → `findings/ai-visibility.json`.

## 7. Score and build
1. `python3 -I "$PLUGIN/scripts/score.py" "$AUDIT"`
2. If the load page was selected: `python3 -I "$PLUGIN/scripts/build_load_page.py" "$AUDIT"` (run it BEFORE the report so the teaser link appears; see `references/agents/load-film.md` if a competitor has no frames).
3. `python3 -I "$PLUGIN/scripts/build_report.py" "$AUDIT"` — a warning about fewer than 5 items is acceptable; never pad.

## 8. Render check
Screenshot `report/index.html` with headless Chrome (`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=5000 --window-size=1440,<height> --screenshot=<png> file://$AUDIT/report/index.html`), look at it, and fix data problems (wrong pins, broken crops, overflowing text) before handing over. Open it for the user with `open "$AUDIT/report/index.html"`.

## 9. Hand-off message
Short: overall score, the Top N titles, which optional blocks are in, anything dropped or unverifiable, placeholders `[...]` in the redesign the user must confirm with the client, and OpenSEO credits spent.

## Rules
- No invented numbers, competitors, search results or AI answers; unmeasured → omit or `[dato por confirmar]`.
- Sensitive technical details (usernames, versions) never in client-facing text.
- Mobile screenshots: Lighthouse full-page or device emulation, never a Chrome window under 500px.
- MB = KiB / 1024.
- The report has no contact CTA and works offline.
- Update `assets/simian/cases.json` with `python3 -I "$PLUGIN/scripts/refresh_simian_cases.py"` when the portfolio changes; tag new cases' `matches` by hand.
