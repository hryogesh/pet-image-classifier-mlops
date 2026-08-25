#!/usr/bin/env bash
set -euo pipefail

# Initialize DVC in the repo and create a local remote placeholder.
# Usage: scripts/init_dvc.sh [--remote-path PATH]

REMOTE_PATH=${1:-.dvc_storage}

if ! command -v dvc >/dev/null 2>&1; then
  echo "DVC not found. Install with: python -m pip install --user dvc" >&2
  exit 2
fi

if [ ! -d .dvc ]; then
  echo "Initializing dvc..."
  dvc init
else
  echo "dvc already initialized"
fi

echo "Creating local remote at: $REMOTE_PATH"
dvc remote add -f storage "local::$REMOTE_PATH"

echo "Local remote configured as 'storage' -> $REMOTE_PATH"
echo "To push data later, run: dvc push"
