# Changelog

## [0.3.0] - 2026-10-27

### Changed
- Report and load page follow the Simian visual identity manual: Green forest `#0B785D` as the brand accent (replaces the lavender/purple), Banana light and Dark trunk for category tags, the warm 0-900 gray scale, and `#3F47A9` for links.
- The showcase band uses a Green forest gradient instead of the purple-to-blue one.
- Typography: Vollkorn for `h1`/`h2`, Source Sans 3 for body text, both bundled as local woff2 so reports still work offline. Inter is removed.
- Secondary text uses `#7A746F` and banana tag text uses `#7A5F14` so both pass WCAG AA (the manual's gray 400 and banana 700 fall below 4.5:1 as text).

## [0.2.1] - 2026-10-24

### Added
- Rubric result `partial` (counts half weight) for criteria met in part (e.g. desktop but not mobile). Shown as ◐ in the criteria list and as "· N parcial(es)" next to each area count.

## [0.2.0] - 2026-10-24

### Changed
- Scoring v3 (method B): each area is the weighted share of a fixed rubric of criteria the site passes (`config/rubric.json`, v1), blended with Lighthouse for accessibility and technical quality. The same site now gives the same score regardless of how many findings an agent writes.
- Area agents (ux, a11y, visual, tech, seo) must return a `checks` entry for every rubric criterion; the validator rejects missing, unknown or duplicate criteria.
- Score section shows "X de Y criterios" per area and an expandable list of every criterion with ✓/✕.
- Load-page teaser button no longer wraps ("Ver comparación ▶").

## [0.1.1] - 2026-10-24

### Changed
- Scoring formula v2: 2 points per impact point (was 4), so areas with many findings no longer collapse to 0.

### Fixed
- Final review: missing area files are rejected instead of scored 100; schema/renderer mismatches; redesign lists solved items; plan and Extra share one predicate; portfolio refresh never wipes cases; fixtures use a fictional brand.

## [0.1.0] - 2026-10-24

### Added
- Orchestrator skill `simian-web-audit`: intake, shared evidence collection, two agent waves, synthesis, scoring, build and render check.
- Per-client audit folders under `./audits/<domain-slug>/` with `BRIEF.md` and `findings/meta.json` (plugin and scoring versions).
- Evidence collector (HTML via curl, Lighthouse mobile + desktop, desktop viewport and Lighthouse full-page screenshots).
- JSON schemas and validator for every findings file.
- Deterministic scoring from findings impact, blended with Lighthouse (`config/scoring.json`, v1).
- Offline report renderer: hero, notch showcase with error pins, scores, big stat, Top N, design critique, 5-second benchmark, before/after redesign slider, optional Extra (search tests, Google/WhatsApp previews, NAP, AI answers, AEO fixes), plan with optional stage and table, Simian cases.
- Optional load-comparison page (Lighthouse filmstrips vs competitors, vision simulator).
- Agent references (ux, a11y, visual, tech, ui-critique, redesign, benchmark, seo, presence, load-film), synthesis and OpenSEO guides.
- Simian assets (logo, portfolio cases, images) and `refresh_simian_cases.py`.
- Bundled Inter variable font (OFL).
