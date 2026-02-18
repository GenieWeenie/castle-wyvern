# Troubleshooting & Configuration

## Environment variables

Copy `.env.example` to `.env` and fill in at least one AI provider key.

| Variable | Required | Purpose |
|----------|----------|---------|
| `AI_API_KEY` | Yes (or ZAI/OpenAI) | Primary key for Phoenix Gate (Z.ai or OpenAI) |
| `ZAI_API_KEY` | Optional | Z.ai provider |
| `OPENAI_API_KEY` | Optional | OpenAI fallback |
| `OLLAMA_HOST` | Optional | Local LLM (e.g. `http://localhost:11434`) |
| `CASTLE_WYVERN_API_KEY` | Optional | REST API key; if set, requests must send `X-API-Key` or `?api_key=` |
| `CASTLE_WYVERN_ENCRYPTION_KEY` | Optional | Memory encryption; auto-generated if not set |
| `SLACK_WEBHOOK_URL` | Optional | Slack integration |
| `DISCORD_WEBHOOK_URL` | Optional | Discord integration |
| SMTP_* | Optional | Email notifications |

**At least one of** `AI_API_KEY`, `ZAI_API_KEY`, or `OPENAI_API_KEY` should be set for LLM features. For local-only use, set `OLLAMA_HOST` and use a local model in Phoenix Gate.

---

## Common errors

### "Invalid or missing API key" (401)

- **Cause:** The server was started with an API key (e.g. `CASTLE_WYVERN_API_KEY` in `.env` or `--api-key`), but the request didn’t send it or sent the wrong value.
- **Fix:** Send the key in a header: `X-API-Key: your-key`, or as a query param: `?api_key=your-key`. Or start the server without an API key if you don’t need protection.

### "Connection refused" / Cannot reach API

- **Cause:** The API server isn’t running or is on a different host/port.
- **Fix:** Start the API from the CLI (`api-start`) or run `python -m eyrie.api_server`. Default port is **18791**. Check firewall and that nothing else is using that port.

### "Question is required" / "query is required" / "task (or description) is required" (400)

- **Cause:** A required body field is missing or empty for that endpoint.
- **Fix:** Send a JSON body with the right field. Examples: `{"question": "..."}` for `/clan/ask`, `{"query": "..."}` for `/kg/reason` and `/memory/search`, `{"task": "..."}` for `/coord/team`. See [api-examples.md](api-examples.md).
- **Response shape:** All API errors return `{"error": "message", "code": "..."}`. Common codes: `missing_field` (400), `invalid_api_key` (401), `server_error` (500). Clients can branch on `code` if needed.

### AI / Phoenix Gate errors or timeouts

- **Cause:** Provider key missing or invalid, network issue, or circuit breaker open after failures.
- **Fix:** Check `AI_API_KEY` (or ZAI/OpenAI) in `.env`. For local LLM, set `OLLAMA_HOST` and ensure Ollama is running. If the circuit breaker has opened, wait a short time or restart the server.

### Tests fail with import or missing dependencies

- **Cause:** Missing packages or wrong Python path.
- **Fix:** From the repo root run `pip install -r requirements.txt` (or `pip install -e ".[dev]"` for dev deps). Run tests with `python -m pytest tests/ -v` from the repo root.

---

## FAQ

**How do I run the REST API?**  
From the repo root: `python -m eyrie.api_server` (default port 18791). Or from the CLI: type `api-start` in interactive mode.

**Where is the CLI?**  
Run `python castle_wyvern_cli.py` from the repo root. For non-interactive commands: `python castle_wyvern_cli.py ask "your question"` or `python castle_wyvern_cli.py status`.

**Request body too large (413)?**  
The API limits request bodies to 5MB. Split large payloads or use a different upload strategy.

**Rate limit exceeded (429)?**  
The API allows 60 requests per minute per IP (or per API key if sent). Default is configurable when starting the server (`rate_limit_per_minute=`). Slow down or batch requests.

---

## Getting help

- **Docs:** [Architecture](architecture.md), [API examples](api-examples.md), [Features](features/README.md).
- **Issues:** [GitHub Issues](https://github.com/GenieWeenie/castle-wyvern/issues).
