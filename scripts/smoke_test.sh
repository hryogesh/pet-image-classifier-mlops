#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for the inference service.
# Usage: scripts/smoke_test.sh [BASE_URL]
# Defaults to http://localhost:8000

BASE=${1:-http://localhost:8000}
RETRIES=10
SLEEP=3

echo "Smoke test: checking $BASE/health"
for i in $(seq 1 $RETRIES); do
  if curl -fsS "$BASE/health" >/dev/null 2>&1; then
    echo "health ok"
    break
  else
    echo "waiting for service... ($i/$RETRIES)"
    sleep $SLEEP
  fi
  if [ "$i" -eq "$RETRIES" ]; then
    echo "service did not become healthy" >&2
    exit 1
  fi
done

echo "Checking metrics endpoint"
if curl -fsS "$BASE/metrics" >/dev/null 2>&1; then
  echo "metrics ok"
else
  echo "metrics endpoint failed" >&2
  exit 1
fi

echo "Smoke test passed"
