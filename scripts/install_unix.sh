#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET_ROOT="$CODEX_HOME_DIR/skills"

if [[ ! -d "$SKILLS_ROOT" ]]; then
  echo "Skills directory not found: $SKILLS_ROOT" >&2
  exit 1
fi

mkdir -p "$TARGET_ROOT"

if [[ "$#" -gt 0 ]]; then
  selected=("$@")
else
  mapfile -t selected < <(find "$SKILLS_ROOT" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | sort)
fi

copy_skill() {
  local src="$1"
  local dst="$2"

  mkdir -p "$dst"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude "__pycache__" \
      --exclude "backups" \
      --exclude "*.pyc" \
      "$src"/ "$dst"/
  else
    cp -R "$src"/. "$dst"/
    find "$dst" -name "__pycache__" -type d -prune -exec rm -rf {} +
    find "$dst" -name "*.pyc" -type f -delete
    find "$dst" -name "backups" -type d -prune -exec rm -rf {} +
  fi
}

for skill in "${selected[@]}"; do
  src="$SKILLS_ROOT/$skill"
  dst="$TARGET_ROOT/$skill"

  if [[ ! -d "$src" ]]; then
    echo "Skill not found in repository: $skill" >&2
    exit 1
  fi

  copy_skill "$src" "$dst"
  echo "Installed: $skill -> $dst"
done

echo
echo "Done. Restart Codex or start a new session to load the updated skills."
