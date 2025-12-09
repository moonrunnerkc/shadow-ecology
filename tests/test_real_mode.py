#!/usr/bin/env python3
# tests/test_real_mode.py
# Test full pipeline in dev mode (persistent vault, no YubiKey required)

import json
import os
from pathlib import Path

# ensure vault directory exists
vault_dir = Path(__file__).parent.parent / "shadowecology" / "vault" / "state"
vault_dir.mkdir(parents=True, exist_ok=True)

# set dev mode (passphrase only, no YubiKey)
os.environ["SHADOWECOLOGY_MODE"] = "dev"

from shadowecology import Shadow

# load example thread
demo_dir = Path(__file__).parent.parent / "demo"
with open(demo_dir / "example_thread.json") as f:
    thread = json.load(f)

print("=== REAL MODE TEST (DEV - NO YUBIKEY) ===\n")

# create shadow in dev mode (will prompt for passphrase)
shadow = Shadow()
print(f"Shadow created: {shadow}")
print(f"Initial step: {shadow.step}\n")

# run ingest
print("Running ingest...")
trace, response = shadow.ingest(thread)

print(f"\nFinal step: {shadow.step}")
print(f"Response length: {len(response)} chars")
print(f"\nResponse:\n{response}\n")

# save trace
output_path = Path(__file__).parent / "results" / "real_mode_trace.gif"
output_path.parent.mkdir(exist_ok=True)
trace.save_gif(str(output_path))
print(f"✓ Trace saved: {output_path}")

print("\n=== IDENTITY PERSISTED TO VAULT ===")
print(f"File: shadowecology/vault/state/shadow_main.msgpack.enc")
print("Run this script again to see step counter increase (persistent state)")
