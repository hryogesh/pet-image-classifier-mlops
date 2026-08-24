#!/usr/bin/env bash
set -euo pipefail
# Usage: ./scripts/checkin_remote.sh <git_remote_url> [branch]
# Example: ./scripts/checkin_remote.sh git@github.com:hryogesh/pet-image-classifier-mlops.git main
# If you want to authenticate non-interactively, set GITHUB_TOKEN env var with a personal access token

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <git_remote_url> [branch]"
  exit 1
fi

REMOTE="$1"
BRANCH="${2:-main}"

if [ ! -d .git ]; then
  git init
fi

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Add MLOps pipeline scaffold"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote remove origin
fi

if [ -n "${GITHUB_TOKEN:-}" ]; then
  # insert token into https url for push (be cautious with token exposure)
  AUTH_REMOTE=$(echo "$REMOTE" | sed -E "s#https://#https://$GITHUB_TOKEN@#")
  git remote add origin "$AUTH_REMOTE"
  git push -u origin "$BRANCH"
else
  git remote add origin "$REMOTE"
  echo "No GITHUB_TOKEN provided; you may be prompted for credentials when pushing."
  git push -u origin "$BRANCH"
fi

echo "Pushed to $REMOTE (branch: $BRANCH)"
