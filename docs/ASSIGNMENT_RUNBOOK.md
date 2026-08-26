# MLOps Assignment 2 Runbook

This runbook maps the project to the M1-M5 rubric and provides a small-batch demonstration that can be completed locally on Windows PowerShell.

## 0. One-time setup

Run from the repository root:

```powershell
cd E:\BITS\Sem3\MLOps\pet-image-classifier-mlops
py -3.14 -m pip install -r requirements.txt
```

Check the tools:

```powershell
py -3.14 --version
py -3.14 -m pytest --version
py -3.14 -m dvc --version
mlflow --version
docker compose version
```

The Docker stages require Docker Desktop to be running. The local Python stages do not.

## Demo dataset

The demo uses 200 images from each class. It does not modify the original dataset.

```powershell
Remove-Item demo -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force demo\raw\Cat, demo\raw\Dog | Out-Null

Get-ChildItem data\raw\PetImages\Cat -File |
  Select-Object -First 200 |
  Copy-Item -Destination demo\raw\Cat
Get-ChildItem data\raw\PetImages\Dog -File |
  Select-Object -First 200 |
  Copy-Item -Destination demo\raw\Dog
```

## M1 - Model development, DVC, and MLflow

### M1.1 Preprocess

```powershell
Remove-Item data\processed -Recurse -Force -ErrorAction SilentlyContinue
py -3.14 -m src.data.preprocess `
  --input_dir demo/raw `
  --output_dir data/processed `
  --img_size 224
```

Verify the 80/10/10 split and both classes:

```powershell
Get-ChildItem data\processed\train\cats -File | Measure-Object | Select-Object Count
Get-ChildItem data\processed\train\dogs -File | Measure-Object | Select-Object Count
Get-ChildItem data\processed\val\cats -File | Measure-Object | Select-Object Count
Get-ChildItem data\processed\test\cats -File | Measure-Object | Select-Object Count
```

Expected demo counts are approximately 160 train, 20 validation, and 20 test images per class.

### M1.2 Train a baseline model

```powershell
py -3.14 -m src.train `
  --data_dir data/processed `
  --save_dir models `
  --epochs 1 `
  --batch_size 8 `
  --lr 0.001 `
  --img_size 224 `
  --model_name baseline_cnn
```

Verify the serialized model and MLflow artifacts:

```powershell
Test-Path models\model.pt
Get-ChildItem models
Test-Path mlruns
```

Training logs parameters, loss, validation accuracy, the model, loss curve, confusion matrix, and classification report to MLflow.

Start the MLflow UI in a separate terminal:

```powershell
cd E:\BITS\Sem3\MLOps\pet-image-classifier-mlops
mlflow ui --backend-store-uri "sqlite:///E:/BITS/Sem3/MLOps/pet-image-classifier-mlops/mlflow.db" --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000` and show the `catsdogs` experiment, parameters, metrics, and artifacts.

### M1.3 DVC verification

The committed DVC pipeline is in `dvc.yaml` and the locked state is in `dvc.lock`.

```powershell
$dvc = "C:\Users\ADMIN\AppData\Local\Python\pythoncore-3.14-64\Scripts\dvc.exe"
& $dvc status
& $dvc dag
& $dvc doctor
```

For the full reproducible pipeline using `data/raw`:

```powershell
& $dvc repro
& $dvc status
```

The final status should say that the data and pipeline are up to date. Full DVC reproduction converts all raw images and can take much longer than the demo.

## M2 - Packaging and containerization

The implementation is in `src/inference/app.py`, `src/inference/utils.py`, `requirements.txt`, and `Dockerfile`.

For a local API demo using the small model:

```powershell
$env:MODEL_PATH = "$PWD\models\model.pt"
$env:MODEL_NAME = "baseline_cnn"
py -3.14 -m uvicorn src.inference.app:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
curl.exe http://127.0.0.1:8000/health
$sample = Get-ChildItem data\processed\test\cats -File | Select-Object -First 1
curl.exe -X POST http://127.0.0.1:8000/predict -F "file=@$($sample.FullName)"
```

Expected responses include `{"status":"ok"}` and prediction JSON containing `probs`, `label`, and `latency`.

If Docker Desktop is running, build and run the container with the full model path expected by Compose:

```powershell
$env:MODEL_NAME = "baseline_cnn"
docker compose build app
docker compose up -d app
curl.exe http://127.0.0.1:8000/health
$sample = Get-ChildItem data\processed\test\cats -File | Select-Object -First 1
curl.exe -X POST http://127.0.0.1:8000/predict -F "file=@$($sample.FullName)"
docker compose down
```

## M3 - CI, tests, and image creation

Run the required unit tests:

```powershell
py -3.14 -m pytest -q
```

The tests cover preprocessing and inference/model utilities in `tests/`.

The GitHub Actions CI workflow is `.github/workflows/ci.yml`. It checks out code, installs dependencies, runs pytest, and builds the Docker image. The container smoke workflow is `.github/workflows/container-smoke.yml`.

Push the repository to GitHub and show a successful Actions run. For registry publishing, configure the registry credentials and image name required by the workflow secrets before pushing.

## M4 - CD and deployment

The deployment target is Docker Compose, defined in `docker-compose.yml`. The CD workflow is `.github/workflows/cd.yml` and runs on pushes to `main`.

Local deployment verification:

```powershell
docker compose config
docker compose up --build -d
docker compose ps
curl.exe http://127.0.0.1:8000/health
$sample = Get-ChildItem data\processed\test\cats -File | Select-Object -First 1
curl.exe -X POST http://127.0.0.1:8000/predict -F "file=@$($sample.FullName)"
docker compose down
```

Capture the Compose services, health response, and prediction response. The Docker daemon must be running. The model must exist at `models/model.pt` before the app starts.

## M5 - Monitoring, logs, and final submission

The API exposes request and latency metrics:

```powershell
curl.exe http://127.0.0.1:8000/metrics
curl.exe http://127.0.0.1:8000/metrics_prometheus
```

Compose also defines Prometheus on `http://127.0.0.1:9090` and Grafana on `http://127.0.0.1:3000`. Show the request count, error count, and latency dashboard after making prediction requests.

Evaluate a small labeled test batch:

```powershell
py -3.14 scripts/evaluate_deployed.py `
  --base-url http://127.0.0.1:8000 `
  --data-dir data/processed/test
```

Create the final package, including the trained model:

```powershell
bash scripts/package_artifacts.sh
Test-Path mlops_package.zip
```

If Bash is unavailable, create the equivalent archive in PowerShell:

```powershell
Compress-Archive `
  -Path README.md,docs,dvc.yaml,dvc.lock,params.yaml,.github,Dockerfile,docker-compose.yml,monitoring,scripts,src,tests,requirements.txt,models `
  -DestinationPath mlops_package.zip `
  -Force
```

The final submission should contain source code, tests, DVC files, CI/CD workflows, Docker files, monitoring configuration, and `models/model.pt`. Do not include the large raw dataset unless specifically required.

## Rubric evidence checklist

- [ ] M1: Git repository, DVC files, 224x224 RGB train/validation/test data, baseline model, MLflow run and artifacts.
- [ ] M2: FastAPI health and prediction endpoints, pinned requirements, Dockerfile, successful local image prediction.
- [ ] M3: pytest output, GitHub Actions CI result, Docker image build, registry configuration or published image.
- [ ] M4: Docker Compose deployment, CD workflow, health check, prediction smoke test.
- [ ] M5: API logs, metrics, Prometheus/Grafana view, labeled post-deployment evaluation, final zip.
- [ ] Screen recording under five minutes showing code change, CI, deployment, health, and prediction.
