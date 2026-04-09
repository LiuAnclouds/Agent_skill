#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
OPENCLAW_HOME_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}"
TARGET="codex"
selected=()

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install_unix.sh [--target codex|openclaw|all] [--codex-home PATH] [--openclaw-home PATH] [skill-name ...]

Examples:
  bash scripts/install_unix.sh
  bash scripts/install_unix.sh moonrabbit moonrabbit-memory
  bash scripts/install_unix.sh --target openclaw moonrabbit moonrabbit-memory
  bash scripts/install_unix.sh --target all moonrabbit moonrabbit-memory
EOF
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --codex-home)
      CODEX_HOME_DIR="${2:-}"
      shift 2
      ;;
    --openclaw-home)
      OPENCLAW_HOME_DIR="${2:-}"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ "$#" -gt 0 ]]; do
        selected+=("$1")
        shift
      done
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      selected+=("$1")
      shift
      ;;
  esac
done

case "$TARGET" in
  codex|openclaw|all)
    ;;
  *)
    echo "Invalid target: $TARGET" >&2
    usage >&2
    exit 1
    ;;
esac

SKILLS_ROOT="$REPO_ROOT/skills"

if [[ ! -d "$SKILLS_ROOT" ]]; then
  echo "Skills directory not found: $SKILLS_ROOT" >&2
  exit 1
fi

selection_mode="explicit"
if [[ "${#selected[@]}" -eq 0 ]]; then
  selection_mode="auto"
  mapfile -t selected < <(find "$SKILLS_ROOT" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | sort)
fi

target_root_for() {
  local kind="$1"
  case "$kind" in
    codex)
      printf '%s/skills\n' "$CODEX_HOME_DIR"
      ;;
    openclaw)
      printf '%s/skills\n' "$OPENCLAW_HOME_DIR"
      ;;
  esac
}

should_sync_to_target() {
  local skill="$1"
  local kind="$2"

  if [[ "$kind" == "openclaw" && "$skill" == ".system" && "$selection_mode" == "auto" ]]; then
    return 1
  fi

  return 0
}

if [[ "$TARGET" == "all" ]]; then
  targets=(codex openclaw)
else
  targets=("$TARGET")
fi

sync_entry() {
  local src="$1"
  local dst="$2"

  mkdir -p "$dst"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --delete \
      --exclude "__pycache__" \
      --exclude "backups" \
      --exclude "*.pyc" \
      "$src"/ "$dst"/
  else
    find "$dst" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
    cp -R "$src"/. "$dst"/
    find "$dst" -name "__pycache__" -type d -prune -exec rm -rf {} +
    find "$dst" -name "*.pyc" -type f -delete
    find "$dst" -name "backups" -type d -prune -exec rm -rf {} +
  fi
}

for kind in "${targets[@]}"; do
  mkdir -p "$(target_root_for "$kind")"
done

for skill in "${selected[@]}"; do
  src="$SKILLS_ROOT/$skill"

  if [[ ! -d "$src" ]]; then
    echo "Skill or bundle not found in repository: $skill" >&2
    exit 1
  fi

  for kind in "${targets[@]}"; do
    if ! should_sync_to_target "$skill" "$kind"; then
      echo "Skipped [$kind]: $skill (hidden system bundle is skipped for OpenClaw by default)"
      continue
    fi

    dst="$(target_root_for "$kind")/$skill"
    sync_entry "$src" "$dst"
    echo "Synced [$kind]: $skill -> $dst"
  done
done

echo
echo "Done. Restart Codex/OpenClaw or start a new session to load the updated skills."
