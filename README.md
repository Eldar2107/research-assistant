# Async research assistant

Ask a question, we pull Wikipedia, arXiv and web search at the same time, then write one short answer with [N] citations.

Team: Eldar ([Eldar2107](https://github.com/Eldar2107)) and teammates. AI Engineering course, Topic 4.

## Quick start

```bash
git clone https://github.com/Eldar2107/research-assistant.git
cd research-assistant
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# open .env and add your keys

# Offline demo üçün:
docker compose --profile demo up demo

# Bütün testləri coverage və PYTHONPATH ilə işlətmək üçün:
docker compose run --rm -e PYTHONPATH=/app app pytest --cov=src --cov-report=term-missing

# Smoke testləri üçün:
docker compose run --rm -e PYTHONPATH=/app app pytest tests/test_ai_smoke.py -v

# CLI sorğusu üçün:
docker compose run --rm -e PYTHONPATH=/app app python -m src.cli "photosynthesis"
```

On Windows use `venv\Scripts\activate` instead of `source`.

Running outside Docker needs `DATABASE_URL=sqlite:///./research_assistant.db` in your `.env`. The default points to the Postgres container, which only exists inside Docker.

## Docker

```bash
docker compose up --build
```

This starts PostgreSQL and the app (API + web page). Open http://localhost:8000. Put your keys in `.env` first.

Offline demo, no keys and no network:

```bash
docker compose --profile demo up demo
```

## Env vars

| Variable | Needed? | Default | What it does |
|---|---|---|---|
| `LLM_PROVIDER` | yes | `gemini` | `anthropic`, `openai` or `gemini` |
| `LLM_MODEL` | yes | `gemini-2.5-flash` | model name |
| `GOOGLE_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | one of them for live runs | - | key for the LLM you picked. Not needed for `demo_ai.py --offline` |
| `WEB_SEARCH_PROVIDER` | yes | `tavily` | `tavily`, `serper` or `duckduckgo` |
| `TAVILY_API_KEY` / `SERPER_API_KEY` | only if you use that search | - | DuckDuckGo needs no key |
| `LOG_LEVEL` | no | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CACHE_DIR` | no | `./.cache` | where the file cache lives |
| `CACHE_TTL_SECONDS` | no | `86400` | how long a cached answer lasts |
| `PER_SOURCE_TIMEOUT_SECONDS` | no | `10` | timeout per source |
| `DATABASE_URL` | no | `postgresql://user:password@research-postgres:5432/research_assistant` | history db. Use SQLite locally |

Same list is in `.env.example`. Keep your real `.env` local, it is gitignored.

## Running it

```bash
# one question
python -m src.cli "What is photosynthesis and what are its main stages?"

# only two sources, skip cache
python -m src.cli "How does CRISPR-Cas9 work?" --sources wiki,arxiv --no-cache

# offline demo of the AI module, no keys needed
python demo_ai.py --offline --limit 5
```

Source names: `wiki`, `arxiv`, `web`. A repeated question comes back from the database with a `[CACHE]` prefix.

### API and web page

```bash
cd frontend && npm install && npm run build && cd ..
uvicorn src.api:app --reload --port 8000
```

Open http://localhost:8000. Swagger docs are at http://localhost:8000/docs.

| Method | Path | What it does |
|---|---|---|
| `GET` | `/health` | health check |
| `POST` | `/api/search` | search, used by the web page |
| `POST` | `/ask` | search with a `sources` choice |

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer models", "sources": "wikipedia,arxiv"}'
```

## Timings

The comparison is sequential (`fetch_sources_sequential`, about the sum of the three sources) against concurrent (`gather_sources`, about the slowest one). Both live in `src/concurrency/orchestrator.py`. Questions come from `data/research_questions.json`. Reports go to `artefacts/`.

TODO: add the measured table and the exact command here once `scripts/bench.py` is run with a working internet connection.

## Tests

```bash
docker compose run --rm -e PYTHONPATH=/app app pytest --cov=src --cov-report=term-missing
docker compose run --rm -e PYTHONPATH=/app app pytest tests/test_ai_smoke.py -v
```
The ai smoke tests use a fake LLM and a fake web search, so they run offline. Storage tests use an in-memory SQLite db. Make sure `DATABASE_URL` is set to SQLite in `.env` before running the CLI tests.

## Layout

```
.
├── ai/
│   ├── providers/
│   ├── sources.py
│   ├── synthesizer.py
│   └── schemas.py
├── src/
│   ├── config.py
│   ├── cli.py
│   ├── api.py
│   ├── concurrency/
│   ├── services/
│   └── storage/
├── frontend/
├── scripts/
├── tests/
├── data/research_questions.json
├── artefacts/
├── docker/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## How it fits together

```
CLI / API -> concurrency/gather_sources -+-> Wikipedia
                                          +-> arXiv
                                          +-> Web search
          -> services/AIService -+-> services/CacheManager (JSON files, TTL)
                                  +-> ai/synthesize (LLM, retry + timeout)
CLI -> storage/repository (PostgreSQL or SQLite history)
```

Only `AIService` talks to `synthesize`. If a source fails or times out it is skipped and the answer is built from the rest. If the LLM fails and an older cached answer exists, that one is returned with an offline note. `ai/` comes from the course and we use it as is.

## Limits

- The answer has [N] markers, but the reference list (title and link) is not returned by the API or CLI yet.
- No auth or rate limit on the API, and every request costs an LLM call.
- CORS is open to all origins, fine for a demo, not for production.
- There are two caches, the JSON file cache and the database table. They do not share keys.
- Tables are created with `create_all`, so there is no migration tool like Alembic.

Built for the AI Engineering course, Topic 4.
