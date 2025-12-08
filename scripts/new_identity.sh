#!/usr/bin/env bash
# Author: Bradley R. Kinnard
# Create a fresh encrypted shadow identity

set -e

IDENTITY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            IDENTITY="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 --name <identity_id>"
            exit 1
            ;;
    esac
done

if [[ -z "$IDENTITY" ]]; then
    echo "Usage: $0 --name <identity_id>"
    exit 1
fi

# find project root (where shadowecology/ lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# single python invocation - prompts once, creates identity
.venv/bin/python3 -c "
from shadowecology.vault.vault import load_or_create
identity = load_or_create('$IDENTITY')
print(f'Created new identity: {identity[\"identity_id\"]}')
"
