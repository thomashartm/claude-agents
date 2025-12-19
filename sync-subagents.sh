#!/usr/bin/env bash
set -euo pipefail

# sync-sibling-agents.sh
# - Lets you choose a source directory from siblings next to this script
# - Syncs its contents into either:
#     1) <git-root>/.claude/agents  (project)
#     2) ~/.claude/agents          (home)

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  sync-subagents.sh [--delete] [--dry-run] [--yes] [--home|--project]

Options:
  --delete     Delete files in target that are not in source (mirror mode)
  --dry-run    Show what would be synced, without changing anything
  --yes        Skip confirmation prompt (still asks you to pick sibling source unless only one exists)
  --home       Force home target (~/.claude/agents)
  --project    Force project target (<git-root>/.claude/agents)
  -h, --help   Show help
USAGE
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Error: Required command not found: $1" >&2
    exit 1
  }
}

is_git_repo() {
  git rev-parse --show-toplevel >/dev/null 2>&1
}

git_root() {
  git rev-parse --show-toplevel 2>/dev/null || true
}

# List sibling directories next to the script
list_sibling_dirs() {
  # Exclude hidden dirs and common noise; keep it simple and predictable.
  # Only top-level dirs directly under SCRIPT_DIR.
  find "${SCRIPT_DIR}" -mindepth 1 -maxdepth 1 -type d \
    ! -name ".*" \
    ! -name "__pycache__" \
    -print | sort
}

choose_source_dir() {
  local dirs=()
  local line
  while IFS= read -r line; do
    [[ -n "$line" ]] && dirs+=("$line")
  done <<< "$(list_sibling_dirs)"

  if [[ ${#dirs[@]} -eq 0 ]]; then
    echo "Error: No sibling directories found next to the script at: ${SCRIPT_DIR}" >&2
    exit 1
  fi

  if [[ ${#dirs[@]} -eq 1 ]]; then
    echo "${dirs[0]}"
    return 0
  fi

  echo >&2
  echo "Choose the local source directory (sibling of this script):" >&2
  local i=1
  for d in "${dirs[@]}"; do
    echo "  ${i}) $(basename "$d")" >&2
    ((i++))
  done
  echo >&2

  local choice=""
  while [[ -z "${choice}" ]]; do
    read -r -p "Choose [1-${#dirs[@]}]: " choice
    if [[ "${choice}" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#dirs[@]} )); then
      echo "${dirs[choice-1]}"
      return 0
    fi
    echo "Please enter a number between 1 and ${#dirs[@]}." >&2
    choice=""
  done
}

choose_target_scope() {
  local choice=""
  echo >&2
  echo "Where do you want to sync agents to?" >&2
  echo "  1) Project: ./.claude/agents (git root)" >&2
  echo "  2) Home:    ~/.claude/agents" >&2
  echo >&2
  while [[ -z "${choice}" ]]; do
    read -r -p "Choose [1-2]: " choice
    case "${choice}" in
      1) echo "project"; return 0 ;;
      2) echo "home"; return 0 ;;
      *) echo "Please enter 1 or 2." >&2; choice="" ;;
    esac
  done
}

# ---- Parse args ----
DO_DELETE="false"
DRY_RUN="false"
AUTO_YES="false"
FORCE_SCOPE="" # "home" or "project"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --delete) DO_DELETE="true"; shift ;;
    --dry-run) DRY_RUN="true"; shift ;;
    --yes) AUTO_YES="true"; shift ;;
    --home) FORCE_SCOPE="home"; shift ;;
    --project) FORCE_SCOPE="project"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

# Pick source sibling dir
SOURCE_DIR="$(choose_source_dir)"

# Decide target scope
SCOPE=""
if [[ -n "${FORCE_SCOPE}" ]]; then
  SCOPE="${FORCE_SCOPE}"
else
  SCOPE="$(choose_target_scope)"
fi

# Resolve destination
DEST=""
if [[ "${SCOPE}" == "project" ]]; then
  if ! is_git_repo; then
    echo "Error: 'project' selected but current directory is not inside a git repository." >&2
    echo "Run this script from inside your project (git repo), or choose 'home'." >&2
    exit 1
  fi
  ROOT="$(git_root)"
  DEST="${ROOT}/.claude/agents"
else
  DEST="${HOME}/.claude/agents"
fi

mkdir -p "${DEST}"

SRC_PATH="${SOURCE_DIR%/}"
DEST_PATH="${DEST%/}"

echo
echo "Syncing:"
echo "  Source: ${SRC_PATH}/  (picked: $(basename "${SOURCE_DIR}"))"
echo "  Target: ${DEST_PATH}/  (${SCOPE})"
echo "  Mode:   $( [[ "${DO_DELETE}" == "true" ]] && echo "mirror (delete extra files)" || echo "merge (keep extra files)" )"
echo "  Dry:    ${DRY_RUN}"
echo

# Safety prompt unless --yes
if [[ "${AUTO_YES}" != "true" ]]; then
  read -r -p "Proceed? [y/N]: " yn
  case "${yn}" in
    y|Y|yes|YES) ;;
    *) echo "Aborted."; exit 0 ;;
  esac
fi

# Perform the copy
if [[ "${DRY_RUN}" == "true" ]]; then
  echo "[DRY RUN] Would copy files from ${SRC_PATH}/ to ${DEST_PATH}/"
  echo
  echo "Files that would be copied:"
  find "${SRC_PATH}" -type f -print | sed "s|^${SRC_PATH}/|  |"

  if [[ "${DO_DELETE}" == "true" ]]; then
    echo
    echo "Files that would be deleted (exist in target but not in source):"
    if [[ -d "${DEST_PATH}" ]]; then
      # Find files in dest that don't exist in source
      while IFS= read -r dest_file; do
        rel_path="${dest_file#${DEST_PATH}/}"
        if [[ ! -e "${SRC_PATH}/${rel_path}" ]]; then
          echo "  ${rel_path}"
        fi
      done < <(find "${DEST_PATH}" -type f -print)
    fi
  fi
else
  # Delete mode: remove everything first, then copy
  if [[ "${DO_DELETE}" == "true" ]] && [[ -d "${DEST_PATH}" ]]; then
    echo "Removing existing files in ${DEST_PATH}/"
    rm -rf "${DEST_PATH:?}"/*
  fi

  # Copy all files
  echo "Copying files..."
  cp -R "${SRC_PATH}/"* "${DEST_PATH}/"
  echo "Copied $(find "${SRC_PATH}" -type f | wc -l | tr -d ' ') files"
fi

echo
echo "Done."
