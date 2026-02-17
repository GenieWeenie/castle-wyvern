# Castle Wyvern - AGENTS.md

## Project
Castle Wyvern - Comprehensive personal AI infrastructure

## Backpressure Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_knowledge_graph.py -v
pytest tests/test_visual_automation.py -v
pytest tests/test_agent_coordination.py -v

# Check test count
pytest tests/ --collect-only | grep "test session" | grep -o "[0-9]\+ items"
```

## Build/Run Instructions
```bash
# Start CLI
python castle_wyvern_cli.py

# Or install and run
pip install -r requirements.txt
python -m castle_wyvern
```

## Project Conventions
- Python 3.9+
- Uses pytest for testing
- Rich library for CLI UI
- All features in eyrie/ directory
- Tests in tests/ directory
- Documentation in .md files at root

## Before pushing (CI)
- **Format:** Run `black --line-length 100 .` (or on changed files only) so the format check stays green.
- Run tests: `pytest tests/ -v`

## Operational Notes
- 63 commits on main branch
- 117 tests expected
- 39+ features implemented
- GitHub: GenieWeenie/castle-wyvern
