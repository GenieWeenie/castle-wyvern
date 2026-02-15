#!/usr/bin/env bash
# Ralph Loop - Castle Wyvern Verification
# Uses Claude Code to verify project is production-ready

set -euo pipefail

PROMISE="all tests pass"
MAX_ITERS=10
PLAN_SENTINEL="STATUS: COMPLETE"
TEST_CMD="cd ~/castle-wyvern && python3 -m pytest tests/ -v --tb=short 2>&1 | tail -20"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Run this inside a git repo."
  exit 1
fi

cd ~/castle-wyvern

# Ensure required files exist
touch PROMPT.md AGENTS.md IMPLEMENTATION_PLAN.md

LOG_FILE=".ralph/ralph.log"
mkdir -p .ralph

# Kimi CLI command with auto-approval (-y flag)
CLI_CMD="kimi -y"

echo "🚀 Starting Ralph Loop for Castle Wyvern verification"
echo "Max iterations: $MAX_ITERS"
echo ""

for i in $(seq 1 "$MAX_ITERS"); do
  echo -e "\n=== Ralph iteration $i/$MAX_ITERS ===" | tee -a "$LOG_FILE"
  echo "$(date): Starting iteration $i" >> "$LOG_FILE"

  # Run Kimi with the prompt
  echo "Running Kimi verification..." | tee -a "$LOG_FILE"
  $CLI_CMD -p "$(cat PROMPT.md)" 2>&1 | tee -a "$LOG_FILE" || true

  # Run tests (backpressure)
  echo -e "\n--- Running tests (backpressure) ---" | tee -a "$LOG_FILE"
  bash -lc "$TEST_CMD" | tee -a "$LOG_FILE" || true

  # Check completion conditions
  if grep -Fq "$PLAN_SENTINEL" IMPLEMENTATION_PLAN.md 2>/dev/null; then
    echo "✅ Completion detected (STATUS: COMPLETE). Stopping." | tee -a "$LOG_FILE"
    exit 0
  fi

  if grep -Fq "97 passed" "$LOG_FILE" 2>/dev/null; then
    echo "✅ All 97 tests passing. Stopping." | tee -a "$LOG_FILE"
    exit 0
  fi

  echo "⏳ Iteration $i complete. Continuing..." | tee -a "$LOG_FILE"
  sleep 2
done

echo "❌ Max iterations reached without completion." | tee -a "$LOG_FILE"
exit 1
