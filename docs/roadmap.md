# Castle Wyvern — Roadmap

A minimal view of where the project is headed so contributors can align.

## Short-term (next few releases)

- **API stability** — Keep existing REST endpoints stable; add versioning if we introduce breaking changes.
- **Docs and examples** — Expand [api-examples.md](api-examples.md) and feature docs as new capabilities land.
- **Tests** — Maintain and grow the test suite (see [AGENTS.md](../AGENTS.md) for backpressure commands).

## Medium-term

- **Integrations** — Deeper OpenClaw, Slack, Discord, or other channels using the same API.
- **Observability** — Optional metrics/telemetry for API and coordination (e.g. request counts, task success rates).
- **Scale and resilience** — Tuning for multiple nodes, persistence for coordination/KAG, and clearer failure modes.

## How to contribute

- **Bugs and ideas:** [GitHub Issues](https://github.com/GenieWeenie/castle-wyvern/issues).
- **Code:** Open a PR against `main`; ensure tests pass (`pytest tests/ -v`).
- **Docs:** PRs to `docs/` and README are welcome; keep [architecture.md](architecture.md) and this roadmap in sync when you change design or direction.

For concrete release history and recent changes, see [CHANGELOG.md](../CHANGELOG.md) and [releases](https://github.com/GenieWeenie/castle-wyvern/releases).
