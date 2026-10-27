# Auditoría de prospectos

Repository for the `simian-web-audit` Claude Code plugin and the audits it produces.

- **Plugin:** `plugins/simian-web-audit/`, a copy of the one in [`mis_skills`](https://github.com/mager19/mis_skills).
- **Audits:** `audits/<domain>/`, with the published micrositio in `report/index.html`.
- **GitHub Pages:** https://simian-lab.github.io/ag-auditorias/

## Install the plugin

The repo is also a Claude Code marketplace. In Claude Code, run:

```
/plugin marketplace add simian-lab/ag-auditorias
/plugin install simian-web-audit@ag-auditorias
```

To work from a local clone instead:

```
git clone https://github.com/simian-lab/ag-auditorias.git
/plugin marketplace add ./ag-auditorias
/plugin install simian-web-audit@ag-auditorias
```

Then ask Claude to audit a site, for example: `audita https://example.com`.

## Publishing a new audit

1. Run the audit from the repo root. Output lands in `audits/<domain>/`.
2. Add a link to `index.html`.
3. Commit and push. GitHub Pages redeploys automatically.

> Pages is public. Everything under `audits/` is reachable by anyone with the URL.
