# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Test coverage for `eyrie.security` (AuditLogger, EncryptionManager, APIKeyManager, SecurityManager).
- Smoke tests for REST API (`/health`, `/clan`).
- Plugin system tests (PluginHook, load example_plugin, trigger hooks).
- Optional features section in README (Ollama, RAG install and usage).
- Pytest marker `integration` for tests that need network or external services.
- Bandit config (`.bandit`) to skip B101/B105 where appropriate.

### Changed
- CI: Black format check now fails the build (repo formatted with black).
- CI: Bandit runs with `.bandit` config and fails on findings (TruffleHog remains best-effort).
- README: Project status section consolidated to a single table.
- Phoenix Gate: added `circuit_breakers` dict for API/dashboard compatibility.
- API server and web dashboard: use `.state` instead of `.state.value` for circuit breaker (string).
- Security: `log_auth` call from `validate_api_key` fixed to use keyword args.
- AGENTS.md: test count updated to 117.

### Fixed
- `eyrie.security`: `SecurityManager.log_auth` signature compatibility with `validate_api_key` call.

## [0.2.0] - (prior releases)

- 39+ features: Phoenix Gate, intent routing, REST API, web dashboard, MCP, A2A, plugins, security, knowledge graph, agent coordination, visual automation, and more.
- See README and GitHub releases for full history.
