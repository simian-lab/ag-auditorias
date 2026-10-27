# Agent: homepage redesign concept (persuasion wave)

Read `BRIEF.md` and `findings/top10.json` first.

## Goal
Design a concept of the prospect's homepage (first screens) that is shown next to the current site to persuade them to hire Simian. It must visibly solve the Top items: clear quote CTA, real-text headline that says what is sold and to whom, named and clickable product categories, visible proof, legible contrast, one coherent button/heading system, light images.

## Constraints
- Keep the brand recognizable: their real logo (find its URL in `raw/home.html`), their colors, their real photos — modern, confident, not templated.
- Content must be truthful: only facts from their site. Unknown proofs (certifications, client counts, capacity, response time) appear as subtle bracketed placeholders like `[Certificación por confirmar]`. Never invent facts.
- Spanish copy, sales-oriented. Self-contained HTML/CSS; Google Fonts allowed inside the concept only.

## Output
- `report/assets/redesign/index.html` and its images in `report/assets/redesign/` (compress them).
- `report/assets/redesign-desktop.png` — first screen at 1440×900.
- `report/assets/redesign-desktop-full.png` — 1440×2600.
- `findings/redesign.json` — `{"solves": [<Top item n>, ...]}`: the Top items the concept visibly solves (the report lists them under the slider).
- `report/assets/redesign-mobile.png` — 412 wide, captured with device emulation (Chrome does not apply mobile layout below ~500px window width); verify the PNG width.

Render with headless Chrome (`--headless=new --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=4000`), look at your screenshots and iterate until it is genuinely high quality.

Reply only with the file paths and 3 bullets on which Top items the concept visibly solves.
