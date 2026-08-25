#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup_env.sh [minimal|full]
# minimal: installs mlflow and dvc only (fast)
# full: installs everything from requirements.txt (default)

MODE=${1:-full}
VENV_DIR=.venv

echo "Setting up python virtualenv in ${VENV_DIR} (mode=${MODE})"

if [ -d "${VENV_DIR}" ]; then
  echo "Virtualenv ${VENV_DIR} already exists. Activate it with: source ${VENV_DIR}/bin/activate"
  exit 0
fi

python -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip setuptools wheel

if [ "${MODE}" = "minimal" ]; then
  pip install mlflow dvc
  echo "Installed minimal tools: mlflow, dvc"
else
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "Installed full requirements from requirements.txt"
  else
    echo "requirements.txt not found; installing minimal tools instead"
    pip install mlflow dvc
  fi
fi

echo "Virtualenv setup complete. Activate with: source ${VENV_DIR}/bin/activate"
