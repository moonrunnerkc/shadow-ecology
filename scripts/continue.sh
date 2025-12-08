#!/usr/bin/env bash
# Author: Bradley R. Kinnard
# Load shadow_main and drop into live REPL

set -e

IDENTITY="shadow_main"

# find project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# load identity and drop into REPL with it available
.venv/bin/python3 -i -c "
from shadowecology.vault.vault import load
identity = load('$IDENTITY')
print(f'Loaded identity: {identity[\"identity_id\"]} (step {identity[\"step\"]})')
print('Variable \"identity\" is available in this REPL')
"
