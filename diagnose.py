#!/usr/bin/env python3
# diagnose.py - Find where evolve.py is hanging

import sys
import time
sys.path.insert(0, "/home/brad/shadowecology")

print("1. Importing modules...", flush=True)
from shadowecology.helix.genome_v2 import GenomeV2
print("2. GenomeV2 imported", flush=True)

from shadowecology.ecology.v2.contradiction import add_belief, find_contradictions
print("3. Contradiction module imported", flush=True)

from shadowecology.oracle.lora_manager import LoRAManager
print("4. LoRAManager imported", flush=True)

print("5. Creating GenomeV2...", flush=True)
genome = GenomeV2()
print("6. GenomeV2 created", flush=True)

print("7. Creating LoRAManager (this loads the GGUF model)...", flush=True)
start = time.time()
lora = LoRAManager()
print(f"8. LoRAManager created in {time.time()-start:.1f}s", flush=True)

print("9. Applying genome to LoRA manager...", flush=True)
start = time.time()
lora.apply_genome(genome)
print(f"10. Genome applied in {time.time()-start:.1f}s", flush=True)

print("11. Testing generation...", flush=True)
start = time.time()
response = lora.generate("Say hello", max_new_tokens=10)
print(f"12. Generated in {time.time()-start:.1f}s: {response}", flush=True)

print("\n✓ All steps completed successfully!")
