# OpenSEO: real AI answers (optional, Extra only)

Goal: get real answers from AI engines to 2 buyer questions and record whether the client is mentioned. Never write an AI answer yourself.

## Preconditions
- The OpenSEO MCP tools are connected. If they are not (no `mcp__*OpenSEO*` tools, or `whoami` fails), tell the user and offer exactly two options:
  1. Connect OpenSEO: in Claude Code run `/mcp`, add/authenticate the OpenSEO connector (claude.ai connectors → OpenSEO), then re-run this step.
  2. Skip this step: the AI-answers block is omitted; the AEO fixes still appear.
- If the account lacks the required plan or credits, say so and offer to skip.

## Flow
1. `whoami` → show the account email and credit balance to the user.
2. `list_projects`; reuse a project for this domain or `create_project` named EXACTLY the clean company name (not "X (auditoría Simian)"), with the domain and the country market (e.g. Colombia 2170, language `es`).
3. `update_project_context`: business overview + competitors from `findings/benchmark.json`.
4. Draft 2 buyer prompts in Spanish (category + city/country). Use engines `chatgpt`, `gemini`, `google_ai_overview` (Perplexity costs much more).
5. `estimate_ai_visibility_cost` with those prompts/engines → show `runNowCostCredits` and ask for explicit approval. Cap: `openseo_credit_cap` in `config/settings.json` (50); above it, require a second explicit confirmation.
6. After approval: `save_ai_visibility_tracker` → immediately `set_ai_visibility_schedule(enabled=false)` (no recurring charges) → `run_ai_visibility_check(maxCostUsd=<approved runNowCostUsd>)`.
7. Wait (`get_ai_visibility_run`, do not re-run), then `get_ai_visibility_results` and `get_ai_visibility_answer` for each answered observation.
8. Read every answer yourself: the brand matcher can miss variants ("E Biopacking S.A.S."). Decide `mentioned` manually.
9. Write `findings/ai-visibility.json`: `source` (tool + run id), `date`, `brand`, `answers[]` `{engine, prompt, mentioned, named[] (companies in the answer, in order), note_es}`, `no_answer[]`.
