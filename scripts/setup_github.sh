#!/usr/bin/env bash
# Create github.com/Akshatha-Mohan/FOMO300K and push (run after: gh auth login)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install gh first: see README.md (GitHub section)"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Not logged in. Run:"
  echo "  gh auth login -h github.com -p https -w"
  exit 1
fi

cd "$REPO_ROOT"

if git remote get-url origin >/dev/null 2>&1; then
  echo "Remote 'origin' already exists:"
  git remote -v
  git push -u origin main
else
  gh repo create FOMO300K \
    --public \
    --source=. \
    --remote=origin \
    --push \
    --description "FOMO300K local workspace: modality docs and minimal preprocessing pipeline"
fi

echo ""
echo "Done: https://github.com/Akshatha-Mohan/FOMO300K"
