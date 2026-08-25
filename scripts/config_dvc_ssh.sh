#!/usr/bin/env bash
set -euo pipefail

# Configure a DVC SSH remote.
# Usage: scripts/config_dvc_ssh.sh <remote-name> <user@host:/absolute/path> [--identity-file /path/to/key]
# Example: ./scripts/config_dvc_ssh.sh storage-ssh deploy@10.0.0.5:/srv/dvc-storage --identity-file ~/.ssh/id_rsa

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <remote-name> <user@host:/absolute/path> [--identity-file /path/to/key]" >&2
  exit 2
fi

REMOTE_NAME=$1
REMOTE_URL=$2
IDENTITY=""

shift 2
while [ "$#" -gt 0 ]; do
  case "$1" in
    --identity-file)
      IDPATH="$2"
      IDPATH=$(realpath "$IDPATH")
      IDPATH_ESCAPED="$IDPATH"
      IDENTITY="$IDPATH_ESCAPED"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if ! command -v dvc >/dev/null 2>&1; then
  echo "dvc not found. Install with: python -m pip install --user dvc" >&2
  exit 2
fi

echo "Configuring DVC SSH remote '$REMOTE_NAME' -> ssh://$REMOTE_URL"
dvc remote add -f "$REMOTE_NAME" "ssh://$REMOTE_URL"

if [ -n "$IDENTITY" ]; then
  echo "Setting identity file for remote"
  dvc remote modify "$REMOTE_NAME" --local ssh_keyfile "$IDENTITY"
  echo "(Note: using --local so the key path is stored only in local config)"
fi

echo "Set default remote to '$REMOTE_NAME'"
dvc remote default "$REMOTE_NAME"

echo "Remote configured. To push data run: dvc push -r $REMOTE_NAME"
echo "To pull on another machine: dvc pull -r $REMOTE_NAME"
