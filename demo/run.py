# demo/run.py
# Viral demo - runs shadow on example thread and generates trace GIF

import json
import os
from pathlib import Path

# set demo mode before importing
os.environ["SHADOWECOLOGY_MODE"] = "demo"

from shadowecology import Shadow

# load thread
demo_dir = Path(__file__).parent
thread_path = demo_dir / "example_thread.json"
output_dir = demo_dir / "output"
output_dir.mkdir(exist_ok=True)

with open(thread_path) as f:
    thread = json.load(f)

# run shadow
shadow = Shadow(mode="demo")
trace, response = shadow.ingest(thread)

# save outputs
trace.save_gif(str(output_dir / "shadow_trace.gif"))

with open(output_dir / "final_response.txt", "w") as f:
    f.write(response)

print(f"✓ Trace: {output_dir / 'shadow_trace.gif'}")
print(f"✓ Response: {output_dir / 'final_response.txt'}")
print(f"\n{response}")
