#!/usr/bin/env bash
set -euo pipefail
docker build -t catsdogs:latest .
docker run -p 8000:8000 catsdogs:latest
