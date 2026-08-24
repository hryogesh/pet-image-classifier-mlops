#!/usr/bin/env bash
set -euo pipefail
OUT=mlops_package.zip
rm -f ${OUT}
zip -r ${OUT} README.md docs dvc.yaml params.yaml .github Dockerfile docker-compose.yml scripts src requirements.txt
echo "Created ${OUT}"
