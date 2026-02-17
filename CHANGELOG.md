# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **API:** Request body size limit (5MB); 413 with `payload_too_large` when exceeded.
- **API /metrics:** `started_at` (ISO timestamp) and `uptime_seconds`.
- **CONTRIBUTING:** Quick smoke check (start API, curl /health).
- **docs/troubleshooting.md:** FAQ (run API, run CLI, 413 payload too large).
- **CI:** Bandit security job fails on high-severity findings only (`-l 3`).
- **Test:** Request body over 5MB returns 413 and `payload_too_large`.

### Changed
- **docs/api-examples.md:** /metrics example includes `started_at` and `uptime_seconds`.

### Fixed
- (none yet)

## [0.2.1] - 2026-02-17

### Added
- Test coverage for `eyrie.security` (AuditLogger, EncryptionManager, APIKeyManager, SecurityManager).
- Smoke tests for REST API (`/health`, `/clan`).
- Plugin system tests (PluginHook, load example_plugin, trigger hooks).
- Optional features section in README (Ollama, RAG install and usage).
- Pytest marker `integration` for tests that need network or external services.
- Bandit config (`.bandit`) to skip B101/B105 where appropriate.
- **Docs:** `docs/architecture.md` (layers, data flow, component map), `docs/api-examples.md` (curl for all main endpoints), `docs/roadmap.md` (direction and how to contribute), `docs/troubleshooting.md` (env vars, common errors and fixes).
- **README:** "What's unique" section (KAG vs RAG, coordination loop, MCP+A2A); API section with examples and link to full API docs; Contributing link.
- **REST API:** GET `/kg/status`, POST `/kg/reason`, GET `/coord/status`, POST `/coord/team` (knowledge graph and agent coordination); GET `/metrics` (request count).
- **API tests** for `/kg/status`, `/kg/reason` (400/200), `/coord/status`, `/coord/team` (400/200), `/metrics`.
- **Dependencies:** `requests>=2.32.0`, `rich>=13.0.0` in requirements; `pyproject.toml` optional-dependencies `[run]` for `pip install -e ".[run]"`.
- **CONTRIBUTING.md:** Setup, run tests, Black, open a PR; linked from README.
- **CLI:** `version` command and startup hint when no API key is set; `--version` / `-v` already supported.
- **API observability:** GET `/metrics` (request count, no auth); request logging (`METHOD path status_code`) via `castle_wyvern.api` logger.

### Changed
- CI: Black format check now fails the build (repo formatted with black).
- CI: Bandit runs with `.bandit` config and fails on findings (TruffleHog remains best-effort).
- README: Project status section consolidated to a single table.
- README: Docs and roadmap section (architecture, api-examples, troubleshooting, roadmap, CHANGELOG, Contributing).
- Phoenix Gate: added `circuit_breakers` dict for API/dashboard compatibility.
- API server and web dashboard: use `.state` instead of `.state.value` for circuit breaker (string).
- **API:** All error responses use consistent shape `{"error": "...", "code": "..."}`; codes: `missing_field` (400), `invalid_api_key` (401), `server_error` (500).
- Security: `log_auth` call from `validate_api_key` fixed to use keyword args.
- AGENTS.md: test count updated (124 tests after API tests added).
- **docs/api-examples.md:** Documents GET `/metrics`.

### Fixed
- `eyrie.security`: `SecurityManager.log_auth` signature compatibility with `validate_api_key` call.

## [0.2.0] - (prior releases)

- 39+ features: Phoenix Gate, intent routing, REST API, web dashboard, MCP, A2A, plugins, security, knowledge graph, agent coordination, visual automation, and more.
- See README and GitHub releases for full history.
