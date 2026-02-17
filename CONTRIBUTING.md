# Contributing to Castle Wyvern

Thanks for considering contributing. Here’s how to get set up and send changes.

## Setup

```bash
git clone https://github.com/GenieWeenie/castle-wyvern.git
cd castle-wyvern
pip install -r requirements.txt
# Or: pip install -e ".[run]"   # install with runtime extras
cp .env.example .env
# Edit .env with your API keys (see docs/troubleshooting.md)
```

## Before you submit

1. **Run the tests** (from the repo root):
   ```bash
   python -m pytest tests/ -v
   ```
   CI runs the full suite on every push. For backpressure commands and test count, see [AGENTS.md](AGENTS.md).

2. **Format with Black** (line length 100; CI will fail otherwise):
   ```bash
   black --line-length 100 .
   ```

3. **Open a PR against `main`.** Keep the change focused; describe what and why.

## What to contribute

- **Code:** Bug fixes, tests, or small features. If you change the API or architecture, update [docs/architecture.md](docs/architecture.md) or [docs/roadmap.md](docs/roadmap.md) as needed.
- **Docs:** Fixes or additions under `docs/` or README are welcome. See [docs/](docs/) for structure.
- **Issues:** Report bugs or ideas in [GitHub Issues](https://github.com/GenieWeenie/castle-wyvern/issues).

## More

- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **Troubleshooting:** [docs/troubleshooting.md](docs/troubleshooting.md)
- **Roadmap and direction:** [docs/roadmap.md](docs/roadmap.md)
