#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== EJECUTANDO HARNESS V2 (10 TAREAS, SALTO DE 10 EN 10) ==="
python3 harness_runner.py
