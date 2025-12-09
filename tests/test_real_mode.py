#!/usr/bin/env python3
# test_real_mode.py
# Run shadow in dev mode (passphrase only, no YubiKey) with persistent vault

import json
import os
from pathlib import Path

# set dev mode (passphrase only, no YubiKey required)
os.environ["SHADOWECOLOGY_MODE"] = "dev"

from shadowecology import Shadow

# load thread
demo_dir = Path("demo")
thread_path = demo_dir / "example_thread.json"

with open(thread_path) as f:
    thread = json.load(f)

print("=== RUNNING IN DEV MODE (PASSPHRASE ONLY) ===")
print("This will create/load encrypted vault at shadowecology/vault/state/shadow_main.msgpack.enc")
print()

# create shadow in dev mode (will prompt for passphrase)
shadow = Shadow(mode="dev")
print(f"✓ Shadow loaded: {shadow}")
print(f"  Current step: {shadow.step}")
print()

# run ingest
print("Processing thread...")
trace, response = shadow.ingest(thread)
print(f"✓ Pipeline complete")
print(f"  Final step: {shadow.step}")
print()

# save trace
output_dir = Path("tests/results")
output_dir.mkdir(parents=True, exist_ok=True)
trace.save_gif(str(output_dir / "real_mode_trace.gif"))
print(f"✓ Trace saved: {output_dir / 'real_mode_trace.gif'}")
print()

print("=== RESPONSE ===")
print(response)
print()

print("✓ Identity persisted to encrypted vault")
print("  Run this script again to continue from this state")
