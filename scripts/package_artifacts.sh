#!/usr/bin/env bash
set -euo pipefail
OUT=mlops_package.zip
rm -f ${OUT}
FILES="README.md docs dvc.yaml dvc.lock params.yaml .github Dockerfile docker-compose.yml monitoring scripts src tests requirements.txt"
if [ -d models ]; then FILES="$FILES models"; fi
zip -r "${OUT}" $FILES
echo "Created ${OUT}"
