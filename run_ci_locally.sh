#!/bin/bash
# Run CI checks locally before pushing
# Usage: ./run_ci_locally.sh

set -e

echo "🏰 Castle Wyvern - Local CI Check"
echo "================================"

# Flake8
echo ""
echo "→ Running flake8..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

# Black
echo ""
echo "→ Running black check..."
black --check --line-length=100 .

# Mypy
echo ""
echo "→ Running mypy..."
mypy --config-file pyproject.toml eyrie/

# Pytest
echo ""
echo "→ Running pytest..."
pytest tests/ -v --cov=eyrie --cov=bmad --cov=grimoorum --cov-report=term-missing

echo ""
echo "✅ All CI checks passed!"
