# FAQ API workflow

Base: https://akapulu.com/api. Bearer AKAPULU_API_KEY. Every path ends in `/`.
Run the helper from the project directory so it reads that project's `.env`.
Python 3.10+ is required. Keep keys off camera and out of frontend code.

After source and scenario validation, use `scripts/akapulu_api.py`:

1. `kb-create "Distinct FAQ name"` → save returned KB ID immediately.
2. `doc-upload REAL_KB_ID akapulu/knowledge.txt --name "Website FAQ"` → save document ID.
3. `doc-wait REAL_KB_ID` → require completed, stop on failure or timeout.
4. Replace the scenario placeholder with the real ID. Run validate_scenario.py and verify_sources.py PROJECT --ready.
5. `scenario-create akapulu/scenario.json --name "Distinct FAQ name" --avatar CHOSEN_AVATAR_UUID --keyword Mara --model gpt-4.1-mini` → save scenario ID and hosted URL.
6. `scenario-get REAL_SCENARIO_ID` → verify persisted wiring, not just a successful POST.

Keep returned IDs and URL in local `akapulu/deployment.json`. Check state on resume. Never automatically repeat a create after an uncertain response; inspect the account first. The helper validates scenario shape and rejects placeholder RAG IDs before creation; source review and completed-document checks remain required too.

Core endpoints:
- POST /knowledge-bases/create/ with JSON name and optional description.
- POST /knowledge-bases/<id>/documents/create/ with multipart name, optional description, and file. UTF-8 text, 130 KiB max, not PDF.
- GET /knowledge-bases/<id>/documents/ for processing statuses.
- POST /scenarios/create/ with name, llm_model, nodes_json, hosted_links:[{avatar_id,label,stt_keywords}]. At most five keywords per link.
- GET /scenarios/<id>/ for persisted scenario.

Use the user's verified avatar selection; there is no documented catalog-list endpoint in this workflow. Pick an account-supported conversation model. A coding agent's model is not automatically the avatar's model.

The initial integration is an ordinary link. It needs no frontend API key, Node server, tunnel, or SDK. Do not imply an in-page embedded experience or assume iframe support.

Before calls, check and disclose current plan limits. Product code reviewed September 30, 2026 has Free: 10 total minutes, 3 minutes per call, 2 concurrent calls. Free presentation includes a watermark. Actual account limits may differ; verify when filming.
