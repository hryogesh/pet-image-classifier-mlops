# Data & Code Versioning

This project uses Git for code versioning and DVC for large-data and model artifact versioning.

Overview
- Code: tracked with `git`.
- Data & Models: tracked with `dvc` (see `dvc.yaml` for pipeline stages).

Quickstart (local remote)

1. Install DVC (locally):

```bash
python -m pip install --user dvc
```

2. Initialize DVC (run once):

```bash
py -3.14 -m dvc init
```

This will initialize DVC in the repo and create a local remote at `./.dvc/remotes/local` (a placeholder).

Windows PowerShell alternative:

```powershell
py -3.14 -m pip install dvc
py -3.14 -m dvc remote add -f storage "local::.dvc_storage"
py -3.14 -m dvc remote default storage
py -3.14 -m dvc remote list
```

The repository defaults to this local remote, so it works without an SSH server.
The remote data is stored in `.dvc_storage` and should not be committed to Git.

3. Track your dataset and model artifacts with DVC:

```bash
# add processed data and model to DVC tracking
dvc add data/processed
dvc add models/model.pt
# this creates .dvc files and updates .gitignore automatically
git add data/processed.dvc models/model.pt.dvc .gitignore dvc.lock dvc.yaml
git commit -m "Track data and model with DVC"
```

4. Configure a remote (recommended)

Replace `s3://my-bucket/path` with your backend (S3, GCS, Azure, SSH, etc.).

```bash
dvc remote add -d storage s3://my-bucket/path
dvc remote modify storage access_key_id <ID>
dvc remote modify storage secret_access_key <KEY>
# push data to remote
dvc push
```

On Windows, use the same commands through the Python launcher when `dvc` is not
on `PATH`:

```powershell
py -3.14 -m dvc push -r storage
py -3.14 -m dvc status
```

Pulling data on another machine

```bash
git clone <repo>
git checkout <commit-with-data>
# fetch DVC-tracked data
dvc pull
```

Notes
- `dvc.yaml` already provides `preprocess` and `train` stages. Use `dvc repro` to run the pipeline reproducibly.
- Keep `mlruns/` and `models/` out of Git — use DVC to track the large artifacts instead.

References
- https://dvc.org/doc
- https://dvc.org/doc/use-cases/versioning-data
