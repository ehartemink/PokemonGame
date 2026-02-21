#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAVE_DIR="${ROOT_DIR}/data/saves"

rm -rf "${SAVE_DIR}"
mkdir -p "${SAVE_DIR}"

echo "Reset complete: ${SAVE_DIR} reinitialized."
