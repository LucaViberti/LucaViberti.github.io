#!/usr/bin/env bash
# Existing translations are never overwritten; new files are English drafts.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$script_dir/copy_to_ja.py"
