# ARCHITECT PRIME AI — ChatGPT Actions plugin starter v1.0
**Status: deployable starter code, NOT installed or approved ChatGPT plugin.**
Includes core GPT package when source ZIP is available, FastAPI service,
OpenAPI schema generated at `/openapi.json`, Dockerfile, API-key authentication,
tests, deployment guide, and privacy policy draft.

## Available operations
- POST /projects — create project with G1 pending
- GET /projects/{project_id} — retrieve project
- POST /concepts/compare — weighted concept scoring
- POST /estimates/calculate — arithmetic cost estimate
- GET /projects/{project_id}/qa — input completeness check
- GET /health — service status

## Local launch
`pip install -r requirements.txt`
Set `ARCHITECT_API_KEY` and `PUBLIC_BASE_URL` environment variables.
`uvicorn app.main:app --reload`
`pytest -q`

## Important limitations
No actual CAD/BIM or photorealistic rendering engine. No official local code database.
No persistent storage, per-user isolation, rate limiting, or full production security.
Do not host confidential customer projects on this demo without hardening.
Read CHATGPT_ACTIONS/SETUP.md.
