#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/download_dataset.sh [dataset_slug] [target_dir]
# Defaults: dataset_slug=bhavikjikadara/dog-and-cat-classification-dataset
#           target_dir=data/raw

DATASET=${1:-bhavikjikadara/dog-and-cat-classification-dataset}
TARGET_DIR=${2:-data/raw}

echo "Using dataset: ${DATASET} -> ${TARGET_DIR}"

if ! python -c "import kagglehub" 2>/dev/null; then
  echo "kagglehub not found. Installing (user scope)..."
  pip install --user kagglehub
fi

echo "Downloading dataset via src.data.download_dataset..."
python -m src.data.download_dataset --dataset_name "${DATASET}" --target_dir "${TARGET_DIR}"

echo "Dataset downloaded to: ${TARGET_DIR}"
