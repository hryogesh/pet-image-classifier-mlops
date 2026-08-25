#!/usr/bin/env bash
set -euo pipefail

# POST a sample image to /predict and validate response
# Usage: scripts/smoke_test_predict.sh [BASE_URL] [SAMPLE_PATH]

BASE=${1:-http://localhost:8000}
SAMPLE=${2:-}

if [ -z "$SAMPLE" ]; then
  # try to find a sample image in processed data
  for d in data/processed/val/cats data/processed/val/dogs data/processed/train/cats data/processed/train/dogs; do
    if [ -d "$d" ]; then
      f=$(ls -A "$d" | head -n1 || true)
      if [ -n "$f" ]; then
        SAMPLE="$d/$f"
        break
      fi
    fi
  done
fi

if [ -z "$SAMPLE" ] || [ ! -f "$SAMPLE" ]; then
  echo "No sample image found; provide path as second arg" >&2
  exit 2
fi

echo "Using sample: $SAMPLE"

RETRIES=8
SLEEP=3
for i in $(seq 1 $RETRIES); do
  if curl -fsS "$BASE/health" >/dev/null 2>&1; then
    break
  fi
  echo "Waiting for service... ($i/$RETRIES)"
  sleep $SLEEP
  if [ "$i" -eq "$RETRIES" ]; then
    echo "service unreachable" >&2
    exit 1
  fi
done

echo "Posting sample to $BASE/predict"
resp=$(curl -sS -F "file=@$SAMPLE" "$BASE/predict") || true
echo "Response: $resp"

if echo "$resp" | grep -q 'error'; then
  echo "Prediction failed" >&2
  exit 1
fi

echo "Smoke predict passed"
