# Castle Wyvern API — Examples

The REST API runs on **port 18791** by default. Start it from the CLI (`api-start`) or:

```bash
python -m eyrie.api_server --port 18791
```

If you set `API_KEY` in `.env` or pass `--api-key`, send it as a header or query param:

- **Header:** `X-API-Key: your-key`
- **Query:** `?api_key=your-key`

`/health` does not require a key; other endpoints do when the server is started with an API key.

**Base URL:** `http://localhost:18791`

---

## Health (no auth)

```bash
curl -s http://localhost:18791/health | jq
```

Example response:

```json
{
  "status": "healthy",
  "timestamp": "2025-02-17T12:00:00",
  "version": "0.2.0",
  "services": {
    "phoenix_gate": "closed",
    "grimoorum": "active",
    "intent_router": "active"
  }
}
```

---

## System status

```bash
curl -s -H "X-API-Key: YOUR_KEY" http://localhost:18791/status | jq
```

Returns version, Phoenix Gate state, node counts, and component status.

---

## Ask the clan (intent routing)

```bash
curl -s -X POST http://localhost:18791/clan/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"question": "What is the best way to structure a Python project?"}' | jq
```

Response includes `routing.intent`, `routing.member`, and `response`.

---

## Code (Lexington)

```bash
curl -s -X POST http://localhost:18791/clan/code \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"description": "Parse a CSV and return rows as dicts", "language": "python"}' | jq
```

---

## Memory — search

```bash
curl -s -X POST http://localhost:18791/memory/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"query": "meeting notes", "limit": 5}' | jq
```

---

## Memory — ingest

```bash
curl -s -X POST http://localhost:18791/memory/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"content": "Project X uses Python 3.9 and Flask.", "type": "note", "metadata": {"source": "readme"}}' | jq
```

---

## Knowledge graph — status

```bash
curl -s -H "X-API-Key: YOUR_KEY" http://localhost:18791/kg/status | jq
```

Returns node/edge counts and graph stats.

---

## Knowledge graph — reason

```bash
curl -s -X POST http://localhost:18791/kg/reason \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"query": "What do we know about authentication?"}' | jq
```

---

## Coordination — status

```bash
curl -s -H "X-API-Key: YOUR_KEY" http://localhost:18791/coord/status | jq
```

Returns registered agents, active/completed/failed tasks, success rate.

---

## Coordination — optimal team

```bash
curl -s -X POST http://localhost:18791/coord/team \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"task": "Design and implement a small REST API", "requirements": ["coding", "architecture", "documentation"]}' | jq
```

Response includes `team` with `id`, `name`, `specialization`, `performance_score` per agent.

---

## BMAD — quick spec

```bash
curl -s -X POST http://localhost:18791/bmad/spec \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"description": "Add rate limiting to the API"}' | jq
```

---

## BMAD — code review

```bash
curl -s -X POST http://localhost:18791/bmad/review \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"code": "def add(a,b): return a+b"}' | jq
```

---

## Endpoint summary

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | no | Liveness |
| GET | `/status` | yes | Full status |
| GET | `/clan` | yes | List clan members |
| POST | `/clan/ask` | yes | Ask (routed by intent) |
| POST | `/clan/code` | yes | Code (Lexington) |
| POST | `/clan/review` | yes | Code review (Xanatos) |
| POST | `/clan/plan` | yes | Plan (Brooklyn) |
| POST | `/clan/summarize` | yes | Summarize (Broadway) |
| GET/POST | `/nodes` | yes | List / register nodes |
| POST | `/nodes/discover` | yes | Trigger discovery |
| POST | `/memory/search` | yes | Search memory |
| POST | `/memory/ingest` | yes | Ingest document |
| GET | `/memory/conversations` | yes | List conversations |
| GET | `/kg/status` | yes | KAG stats |
| POST | `/kg/reason` | yes | Logical reasoning |
| GET | `/coord/status` | yes | Coordination stats |
| POST | `/coord/team` | yes | Optimal team for task |
| POST | `/bmad/spec` | yes | Quick spec |
| POST | `/bmad/review` | yes | Code review |

See [architecture.md](architecture.md) for how these map to Phoenix Gate, Grimoorum, KAG, and coordination.
