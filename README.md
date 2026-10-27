# ag-auditorias

Claude Code plugin that audits a prospect's website and builds a persuasive Top N micrositio (UX, accessibility, visual, technical, plus an optional SEO/AI-search module) for in-person meetings. The repo also stores the published audits.

- **Plugin:** `plugins/simian-web-audit/`
- **Audits:** `audits/<domain>/`, with the micrositio in `report/index.html`
- **GitHub Pages:** https://simian-lab.github.io/ag-auditorias/

## Requirements

- macOS (the scripts use `sips`)
- Python 3 (standard library only, no `pip install` needed)
- Google Chrome at `/Applications/Google Chrome.app`
- Lighthouse CLI: `npm i -g lighthouse`
- [Claude Code](https://claude.com/claude-code)
- Optional: an OpenSEO connection in Claude, for real AI-search answers (uses paid credits)

The plugin runs a preflight check at the start of every audit and tells you what is missing.

## Setup

```bash
git clone https://github.com/simian-lab/ag-auditorias.git
cd ag-auditorias
claude
```

Inside Claude Code, register this repo as a marketplace and install the plugin:

```
/plugin marketplace add ./
/plugin install simian-web-audit@ag-auditorias
```

Restart Claude Code if the skill does not show up right away.

## Running an audit

Always start Claude Code from the repo root. Audits are written to `./audits/`.

```
audita https://example.com
```

Claude asks one question at a time:

1. The prospect URL
2. Business context (optional; inferred from the site if skipped)
3. Competitors, or let Claude find them
4. Optional blocks: load comparison page, Extra module (SEO and AI-search visibility), and OpenSEO real AI answers (paid; Claude asks for approval before spending credits)

It then collects evidence, runs the analysis agents, scores the site and builds `audits/<domain>/report/index.html`.

## Publishing an audit

1. Add a link to the new report in `index.html`.
2. Commit and push to `main`. GitHub Pages redeploys automatically.

> Everything under `audits/` is served by GitHub Pages. Do not commit anything that should not be visible to whoever has the link.

## Updating the plugin

Edit the files under `plugins/simian-web-audit/` and bump `version` in `plugins/simian-web-audit/.claude-plugin/plugin.json`. To pick up the change in Claude Code, run `/plugin marketplace update ag-auditorias`.
