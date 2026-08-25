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
bash scripts/init_dvc.sh
```

This will initialize DVC in the repo and create a local remote at `./.dvc/remotes/local` (a placeholder).

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

SSH remote example

To configure an SSH-backed remote use the helper script:

```bash
# configure remote named 'storage-ssh' that points to /srv/dvc-storage on host 10.0.0.5
bash scripts/config_dvc_ssh.sh storage-ssh deploy@10.0.0.5:/srv/dvc-storage --identity-file ~/.ssh/id_rsa

# push data to the new remote
dvc push -r storage-ssh
```

Notes about SSH remote
- The helper stores the SSH key location in your local DVC config (not committed) using `--local`.
- Ensure the remote path is writable by the SSH user and that the server has `dvc` prerequisites (a plain filesystem remote works without server-side DVC).

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
