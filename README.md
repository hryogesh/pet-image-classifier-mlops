# pet-image-classifier-mlops

End-to-end MLOps project for Cats vs Dogs binary image classification (pet adoption
platform). This repository contains an example pipeline for data preprocessing,
model training (PyTorch), MLflow experiment tracking, containerized inference
service (FastAPI), automated tests, and CI/CD workflows using GitHub Actions.

This README documents how to set up and run the complete end-to-end flow
locally and how to produce the submission package.

## Quick Start (local end-to-end)

Prerequisites
- Git
- Python 3.10
- Docker & Docker Compose (for containerized inference)
- DVC (optional, if you want to pull dataset from DVC remote)

Recommended: create and activate a virtual environment before installing dependencies.

Minimal (only MLflow + DVC, faster):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install mlflow dvc
```

Full (all project dependencies — includes PyTorch and may take longer):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you prefer system/user installs, deactivate the venv and use `python -m pip install --user ...` instead, but avoid `--user` inside an active virtualenv.

1) Prepare data

- If you are using DVC remote (configured), fetch data with:

```bash
dvc pull
```

- Or manually place the raw dataset under `data/raw/` so the directory contains
  images organised into `cats` and `dogs` subfolders (or files with `cat`/`dog`
  in the filename).

2) Preprocess images (224x224 and split into train/val/test):

```bash
python -m src.data.preprocess --input_dir data/raw --output_dir data/processed --img_size 224
```

Download dataset (helper script)

You can use the bundled helper script to download the Kaggle Cats & Dogs dataset into `data/raw`.

```bash
# make script executable first (only required once)
chmod +x scripts/download_dataset.sh

# default dataset and target dir
./scripts/download_dataset.sh

# or specify dataset slug and target dir
./scripts/download_dataset.sh bhavikjikadara/dog-and-cat-classification-dataset data/raw
```

Notes:
- The script installs `kagglehub` into user scope if it's missing.
- Ensure your Kaggle credentials are available if `kagglehub` requires them (see `kagglehub` docs).

3) Train a model (saves best model to `models/model.pt` and logs runs to MLflow):

```bash
python -m src.train --data_dir data/processed --save_dir models --epochs 3
# optional: increase --epochs and set --batch_size
```

To view MLflow UI locally:

```bash
mlflow ui --backend-store-uri mlruns --port 5000
# then open http://localhost:5000
```

4) Run the inference API locally (without Docker):

```bash
uvicorn src.inference.app:app --host 0.0.0.0 --port 8000
```

5) Run with Docker Compose (recommended for the assignment):

```bash
docker compose build
docker compose up -d

# Smoke test
curl -f http://localhost:8000/health
```

If the model file is missing, the service will fail to load the model — ensure
`models/model.pt` exists (created by training) or update `MODEL_PATH` env var.

## Tests

Run unit tests with:

```bash
python -m pytest -q
```

Two unit tests are provided:
- `tests/test_preprocess.py` — verifies preprocessing creates expected folders
- `tests/test_inference_utils.py` — verifies inference preprocessing (requires torch)

## Packaging & Submission

The repository includes a packaging helper that zips the project files required
for submission (does not include large model files by default):

```bash
./scripts/package_artifacts.sh
# Produces mlops_package.zip
```

If you need to include `models/model.pt` in the submission, run training first
or copy the trained model into `models/` prior to packaging.

## CI / CD

This repo contains two GitHub Actions workflows:
- `.github/workflows/ci.yml` — runs on push/PR: installs deps, runs tests, builds Docker image and optionally pushes the image if registry secrets are provided.
- `.github/workflows/cd.yml` — runs on push to `main`: builds and runs `docker compose` on the runner and performs a smoke test (`/health`).

Notes on registry publishing: set `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, and `IMAGE_NAME` secrets in your GitHub repository to enable image push from the CI workflow.

## Monitoring & Logging

The inference service emits basic logs (request count and latency). For a full
monitoring stack, integrate Prometheus/Grafana or send logs to your preferred
aggregator.

## Useful scripts

- `scripts/build_and_run.sh` — builds an image and runs it with `docker run`.
- `scripts/checkin_remote.sh` — helper to initialize git and push to remote.
- `scripts/package_artifacts.sh` — packages source/config files into a zip.

## Troubleshooting

- If `pytest` is not found, ensure you installed `requirements.txt` inside the
  active virtualenv.
- If Docker Compose fails, ensure Docker daemon is running and you have
  permission to run Docker commands.
- If inference service fails to start, check logs and ensure `models/model.pt`
  exists.

---

If you'd like, I can also:
- add a small `scripts/run_end_to_end.sh` wrapper that runs preprocess → train → package → docker-compose up
- implement simple post-deployment performance collection (M5.2)
Please tell me which next step you'd like.

## Data Versioning & Experiment Tracking

- Data versioning: this repo includes a `dvc.yaml` pipeline with `preprocess` and `train` stages. Use `dvc repro` to run the pipeline and `dvc pull` to fetch data from a configured remote.
- The `preprocess` stage writes processed images to `data/processed` (this is a DVC tracked output).
- The `train` stage writes the best model to `models/model.pt` and is configured as a DVC output in `dvc.yaml`.

- Experiment tracking: training runs are logged to MLflow in the local `mlruns/` folder by default. Launch the UI with:

```bash
mlflow ui --backend-store-uri mlruns --port 5000
# open http://localhost:5000
```

The training script now also logs loss curves, a confusion matrix image, and a classification report as MLflow artifacts.
