# MLOps Assignment M1-M5 Scoring Matrix & Pending Tasks

## M1 - Model Development, DVC, and MLflow

### M1.1 Data Preprocessing
- [ ] Run preprocessing with 80/10/10 train/val/test split
- [ ] Verify 224x224 RGB image format
- [ ] Check data split counts:
  - [ ] Train: ~160 cats, ~160 dogs (demo)
  - [ ] Validation: ~20 cats, ~20 dogs (demo)
  - [ ] Test: ~20 cats, ~20 dogs (demo)

### M1.2 Baseline Model Training
- [ ] Train baseline CNN model
- [ ] Save model to `models/model.pt`
- [ ] Log to MLflow with:
  - [ ] Parameters (epochs, batch_size, lr, img_size, model_name)
  - [ ] Metrics (loss, validation accuracy)
  - [ ] Artifacts (model.pt, loss curve, confusion matrix, classification report)
  - [ ] Experiment name: `catsdogs`

### M1.3 DVC Pipeline & Reproducibility
- [ ] `dvc.yaml` committed with pipeline definition
- [ ] `dvc.lock` committed with locked state
- [ ] DVC remote configured (currently: `../.dvc_storage`)
- [ ] `dvc status` shows pipeline up-to-date
- [ ] `dvc dag` shows DAG
- [ ] `dvc doctor` runs successfully
- [ ] Full `dvc repro` produces consistent results

---

## M2 - Packaging and Containerization

### M2.1 FastAPI Inference Service
- [ ] `src/inference/app.py` implements:
  - [ ] `/health` endpoint returns `{"status":"ok"}`
  - [ ] `/predict` endpoint accepts image upload
  - [ ] Response includes `probs`, `label`, `latency`
  - [ ] `/metrics` endpoint (request/error counts)
  - [ ] `/metrics_prometheus` endpoint for Prometheus

### M2.2 Service Requirements
- [ ] `requirements.txt` with pinned versions
- [ ] `src/inference/utils.py` with model utilities
- [ ] Model loading from `MODEL_PATH` environment variable
- [ ] Local API test successful on port 8000

### M2.3 Docker Image
- [ ] `Dockerfile` present and builds successfully
- [ ] Image runs locally
- [ ] Image can load model from `/app/models/model.pt`
- [ ] Health check passes in container
- [ ] Prediction works in container

---

## M3 - CI, Tests, and Image Creation

### M3.1 Unit Tests
- [ ] `tests/test_preprocess.py` exists and passes
- [ ] `tests/test_inference_utils.py` exists and passes
- [ ] `tests/test_dataset_download.py` exists and passes
- [ ] `pytest -q` runs all tests successfully

### M3.2 GitHub Actions CI Workflow
- [ ] `.github/workflows/ci.yml` exists
- [ ] Workflow triggers on push/PR
- [ ] Workflow steps:
  - [ ] Checkout code
  - [ ] Install dependencies
  - [ ] Run pytest
  - [ ] Build Docker image
- [ ] At least one successful CI run on GitHub
- [ ] CI badges/checks visible in repo

### M3.3 Docker Image Registry (Optional)
- [ ] Registry credentials configured in GitHub Secrets
- [ ] Image name configured in GitHub Secrets
- [ ] Image published to registry on CI success

---

## M4 - CD and Deployment

### M4.1 Docker Compose Deployment
- [ ] `docker-compose.yml` defines services (app, prometheus, grafana)
- [ ] App service mounts `models/model.pt`
- [ ] Compose configuration valid: `docker compose config` passes

### M4.2 CD Workflow
- [ ] `.github/workflows/cd.yml` exists
- [ ] Workflow triggers on pushes to `main`
- [ ] Deploys Docker Compose or equivalent
- [ ] At least one successful CD deployment logged

### M4.3 Deployment Verification
- [ ] `docker compose up --build -d` runs successfully
- [ ] Health check passes: `curl http://127.0.0.1:8000/health`
- [ ] Prediction endpoint responds: `curl -X POST http://127.0.0.1:8000/predict`
- [ ] `docker compose ps` shows running services
- [ ] `docker compose down` cleans up

---

## M5 - Monitoring, Logs, and Final Submission

### M5.1 Metrics & Monitoring
- [ ] API exposes metrics endpoints:
  - [ ] `/metrics` (custom JSON format)
  - [ ] `/metrics_prometheus` (Prometheus format)
- [ ] Metrics track:
  - [ ] Request count
  - [ ] Error count
  - [ ] Response latency

### M5.2 Prometheus & Grafana
- [ ] `monitoring/prometheus.yml` configured
- [ ] `monitoring/grafana/dashboards/pet-classifier.json` exists
- [ ] Prometheus accessible at `http://127.0.0.1:9090`
- [ ] Grafana accessible at `http://127.0.0.1:3000`
- [ ] Dashboard displays metrics after prediction requests

### M5.3 Post-Deployment Evaluation
- [ ] `scripts/evaluate_deployed.py` exists and runs
- [ ] Evaluates test set against deployed API
- [ ] Logs accuracy/classification metrics

### M5.4 Final Submission Package
- [ ] Run `bash scripts/package_artifacts.sh` or PowerShell Compress-Archive
- [ ] `mlops_package.zip` contains:
  - [ ] README.md
  - [ ] `docs/` (all documentation)
  - [ ] `dvc.yaml`, `dvc.lock`, `params.yaml`
  - [ ] `.github/` (CI/CD workflows)
  - [ ] `Dockerfile`, `docker-compose.yml`
  - [ ] `monitoring/` (Prometheus & Grafana config)
  - [ ] `scripts/` (evaluation and utility scripts)
  - [ ] `src/` (model, training, inference code)
  - [ ] `tests/` (unit tests)
  - [ ] `requirements.txt`
  - [ ] `models/model.pt` (trained model)
  - [ ] ❌ NOT: `data/raw/` (large dataset)

### M5.5 Screen Recording
- [ ] Record demo under 5 minutes showing:
  - [ ] Code change to main branch
  - [ ] CI workflow trigger and success
  - [ ] Deployment via CD
  - [ ] Health check response
  - [ ] Prediction response

---

## Rubric Evidence Checklist

- [ ] **M1**: Git repo with DVC files, 224×224 RGB data split (80/10/10), baseline model, MLflow run & artifacts
- [ ] **M2**: FastAPI `/health` & `/predict` endpoints, pinned requirements, working Dockerfile, local image prediction
- [ ] **M3**: pytest output passing, GitHub Actions CI success, Docker image build, registry configured (if applicable)
- [ ] **M4**: Docker Compose deployment, CD workflow, health check, prediction smoke test all working
- [ ] **M5**: API metrics & logs, Prometheus/Grafana operational, post-deployment evaluation, final submission zip

---

## Quick Demo Commands (Windows PowerShell)

```powershell
# Setup
cd E:\BITS\Sem3\MLOps\pet-image-classifier-mlops
py -3.14 -m pip install -r requirements.txt

# M1: Train & MLflow
py -3.14 -m src.train --data_dir data/processed --save_dir models --epochs 1 --batch_size 8 --img_size 224
mlflow ui --backend-store-uri "sqlite:///E:/BITS/Sem3/MLOps/pet-image-classifier-mlops/mlflow.db" --host 127.0.0.1 --port 5000

# M1: DVC
dvc status
dvc dag

# M3: Tests
py -3.14 -m pytest -q

# M2: Local API
$env:MODEL_PATH = "$PWD\models\model.pt"
py -3.14 -m uvicorn src.inference.app:app --host 127.0.0.1 --port 8000

# M2/M4: Docker
docker compose build app
docker compose up -d
curl http://127.0.0.1:8000/health
docker compose down

# M5: Evaluation
py -3.14 scripts/evaluate_deployed.py --base-url http://127.0.0.1:8000 --data-dir data/processed/test

# M5: Package
Compress-Archive -Path README.md,docs,dvc.yaml,dvc.lock,params.yaml,.github,Dockerfile,docker-compose.yml,monitoring,scripts,src,tests,requirements.txt,models -DestinationPath mlops_package.zip -Force
```

---

## Status Summary

- **Total Tasks**: ~80+ checkboxes across M1-M5
- **Legend**:
  - ✅ = Complete
  - 🔄 = In Progress
  - ⏳ = Pending (not started)

Update each checkbox as you complete tasks.
