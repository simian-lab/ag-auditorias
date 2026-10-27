# Agent: UI critique (persuasion wave)

Read `BRIEF.md` and `findings/top10.json` first. Output: `findings/ui-critique.json` (schema `ui-critique`) plus crops `screenshots/ui-crop-*.png`.

## Goal
The report must persuade the owner that the site looks disorganized next to what it could be. Go deeper than `findings/visual.json`; do not repeat it.

## Deliverable
- `verdict`: one blunt but respectful sentence in Spanish about the UI as a whole.
- `inventory`: up to 6 groups (`buttons`, `headings`, `colors`, `fonts`, `cards`, `icons`). Each has a `title` with a point of view ("Seis botones, seis personalidades"), a 2-sentence `explanation` of why a buyer reads it as disorder, `items` and a `proposal`.
  - `buttons`/`headings`/`cards`/`icons` items: `{label, crop}` where `crop` is the filename of a real crop in `screenshots/`.
  - `colors` items: `{label, hex}` with hex values read from the real CSS.
  - `fonts` items: `{label, family}`.
- `proposed_system`: `colors` (name, hex, role — include the contrast ratio of text on it), `fonts`, `button_primary`, `button_secondary`, `heading_scale`. Base it on the brand's real colors.
- `hierarchy_notes`: per section, what the eye sees first vs what it should.
- `sharp_headlines`: for every Top item `n`, a rewritten Spanish headline with stance, ≤ 8 words, truthful (e.g. "Tu sitio no está pidiendo la venta").

## How to crop
Re-shoot the live page with headless Chrome at 2× (`--force-device-scale-factor=2 --window-size=1440,H`) and crop each element with `sips -c H W --cropOffset Y X in.png --out screenshots/ui-crop-<name>.png`. Screenshots named `.jpg` from Lighthouse may be WebP: convert first.

Reply only with the file path, the verdict and the list of crops.
