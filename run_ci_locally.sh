#!/bin/bash
# Run exact CI steps; exit on first failure. Use: bash run_ci_locally.sh
set -e
cd "$(dirname "$0")"

echo "=== 1. Flake8 (strict) ==="
python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

echo "=== 2. Black check ==="
python3 -m black --check --line-length=100 .

echo "=== 3. Mypy ==="
python3 -m mypy eyrie/

echo "=== 4. Pytest ==="
python3 -m pytest tests/ -v --cov=eyrie --cov=bmad --cov=grimoorum --cov-report=xml --tb=short

echo "=== ALL CI STEPS PASSED ==="
