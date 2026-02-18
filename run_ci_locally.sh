#!/bin/bash
# Run CI checks locally before pushing. Usage: bash run_ci_locally.sh
set -e
cd "$(dirname "$0")"

echo "=== 1. Flake8 (strict) ==="
python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

echo "=== 2. Black check ==="
python3 -m black --check --line-length=100 .

echo "=== 3. Mypy ==="
python3 -m mypy eyrie/ --config-file pyproject.toml

echo "=== 4. Pytest ==="
python3 -m pytest tests/ -v --cov=eyrie --cov=bmad --cov=grimoorum --cov-report=term-missing --tb=short

echo "=== ALL CI STEPS PASSED ==="
