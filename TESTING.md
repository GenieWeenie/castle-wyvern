# Testing Guide

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Files

```bash
pytest tests/test_phoenix_gate.py -v
pytest tests/test_intent_router.py -v
pytest tests/test_knowledge_graph.py -v
pytest tests/test_visual_automation.py -v
pytest tests/test_agent_coordination.py -v
pytest tests/test_error_handler.py -v
```

### Run a Single Test

```bash
pytest tests/test_phoenix_gate.py::test_function_name -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

## Test Coverage Summary

| Test File | Tests | Description |
|---|---|---|
| `test_phoenix_gate.py` | 8 | Core Phoenix Gate functionality |
| `test_intent_router.py` | 9 | Intent routing and classification |
| `test_knowledge_graph.py` | 30 | Knowledge graph operations (Claude created) |
| `test_visual_automation.py` | 19 | Visual automation workflows (Claude created) |
| `test_agent_coordination.py` | 18 | Agent coordination and orchestration (Claude created) |
| `test_error_handler.py` | 13 | Error handling and recovery |
| **Total** | **97** | |

## Best Practices for Writing Tests

### Structure

- **One test file per module** — name it `test_<module>.py`
- **One assertion per test** when possible for clear failure messages
- **Use descriptive test names** — `test_router_handles_empty_input` over `test_router_1`

### Patterns

```python
import pytest

class TestFeatureName:
    """Group related tests in a class."""

    def test_expected_behavior(self):
        """Test the happy path."""
        result = feature_function(valid_input)
        assert result == expected_output

    def test_edge_case(self):
        """Test boundary conditions."""
        result = feature_function(edge_input)
        assert result is not None

    def test_error_handling(self):
        """Test that errors are raised appropriately."""
        with pytest.raises(ValueError):
            feature_function(invalid_input)
```

### Guidelines

- Use `@pytest.fixture` for shared setup instead of duplicating code
- Use `@pytest.mark.parametrize` for testing multiple inputs against the same logic
- Mock external dependencies (APIs, file I/O, network calls) with `unittest.mock`
- Keep tests fast — avoid sleep calls and real network requests
- Tests should be independent and not rely on execution order

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ -v --tb=short

      - name: Run tests with coverage
        run: pytest tests/ -v --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
pytest tests/ -q --tb=line
```

## Troubleshooting

### `ModuleNotFoundError`

Ensure you're running from the project root and dependencies are installed:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Tests pass individually but fail together

Tests may have shared state. Check for:
- Global variables being mutated
- Files written to disk without cleanup
- Missing `teardown` or fixture `yield` cleanup

### Slow tests

Run with timing to identify bottlenecks:

```bash
pytest tests/ -v --durations=10
```

### Fixture not found

Make sure fixtures are defined in `conftest.py` or in the same file where they're used. Fixtures in `conftest.py` are auto-discovered by pytest.

### Mocking not working

Patch where the object is **used**, not where it's **defined**:

```python
# If module_a imports func from module_b:
# Patch "module_a.func", not "module_b.func"
with patch("module_a.func") as mock_func:
    mock_func.return_value = "mocked"
```
