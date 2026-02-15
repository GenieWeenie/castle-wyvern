# Testing & Quality — Castle Wyvern

## Overview

Castle Wyvern includes comprehensive test coverage for all major features. This document describes how to run tests and what's covered.

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_knowledge_graph.py -v
pytest tests/test_visual_automation.py -v
pytest tests/test_agent_coordination.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=eyrie --cov-report=html
```

## Test Coverage

### Core Features (tests/)

| Test File | Features Covered | Test Count |
|-----------|-----------------|------------|
| `test_phoenix_gate.py` | API routing, health checks, error handling | 8 tests |
| `test_intent_router.py` | Intent classification, routing, fallbacks | 9 tests |
| `test_knowledge_graph.py` | Entities, relationships, queries, visualization | 10 tests |
| `test_visual_automation.py` | UI elements, macros, session recording | 9 tests |
| `test_agent_coordination.py` | Agents, tasks, coordination loops, analytics | 15 tests |
| `test_error_handler.py` | Custom exceptions, retry logic, circuit breaker | 13 tests |

**Total: 64 tests**

### Test Categories

#### Unit Tests
Test individual components in isolation:
- Entity creation and manipulation
- Relationship management
- Agent capability matching
- Task assignment algorithms

#### Integration Tests
Test component interactions:
- Intent router → Phoenix Gate
- Knowledge Graph → Visualization
- Agent Coordination → Team formation

#### Error Handling Tests
Test failure scenarios:
- Circuit breaker behavior
- Retry logic with exponential backoff
- Error recovery suggestions

## Writing New Tests

### Test Structure
```python
import pytest
from eyrie.module import Component

class TestComponent:
    def setup_method(self):
        """Set up test fixtures."""
        self.component = Component()
    
    def test_feature(self):
        """Test specific feature."""
        result = self.component.do_something()
        assert result == expected_value
```

### Best Practices
1. Use descriptive test names
2. One assertion per test (when possible)
3. Use fixtures for common setup
4. Mock external dependencies
5. Test both success and failure cases

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --tb=short

# Check coverage
pytest tests/ --cov=eyrie --cov-fail-under=80
```

## Test Data

Tests use:
- **Temporary files** (pytest tmp_path fixture)
- **Mock objects** (unittest.mock)
- **In-memory databases** (where applicable)

No production data is used in tests.

## Known Limitations

Some features require manual testing:
- Visual automation (requires screen capture)
- Browser agent (requires browser control)
- Multi-node distribution (requires network)

These are tested via integration tests and manual QA.

## Quality Metrics

- **Test Coverage Target**: 80%+
- **Test Execution Time**: < 30 seconds
- **Flaky Tests**: 0 tolerance
- **Documentation**: Every test file has module docstring

## Contributing

When adding features:
1. Write tests FIRST (TDD approach)
2. Ensure all tests pass
3. Add to this documentation
4. Update coverage metrics

## Troubleshooting

### Tests Fail on Import
```bash
# Ensure you're in the project root
cd ~/castle-wyvern

# Install test dependencies
pip install pytest pytest-cov

# Run with Python path
PYTHONPATH=. pytest tests/
```

### Permission Errors
Some tests create temporary files. Ensure:
- Write access to `/tmp`
- Write access to `~/.castle_wyvern/logs/`

### Timeout Issues
Tests have default 30s timeout. For slow tests:
```bash
pytest tests/ --timeout=60
```

---

**Last Updated**: 2026-02-14
**Test Count**: 64
**Coverage**: 80%+
