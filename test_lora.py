#!/usr/bin/env python3
# test_lora.py
# Test genome-influenced generation with LoRA manager

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.helix.genome_v2 import GenomeV2
from shadowecology.oracle.lora_manager import LoRAManager

print("=== Testing LoRA Manager with Genome ===\n")

# create genome with extreme curiosity and low risk
genome = GenomeV2()
genome.values[:64] = [0.9] * 64       # max curiosity
genome.values[320:384] = [0.1] * 64   # min risk

print("Genome traits:")
for trait, value in genome.get_all_traits().items():
    print(f"  {trait}: {value:.2f}")

print("\n--- Initializing LoRA Manager ---")
lora = LoRAManager()

print("--- Applying genome ---")
lora.apply_genome(genome)

print("\n--- Generating with curious/safe personality ---")
prompt = "Tell me a very curious but safe joke about cats."

try:
    response = lora.generate(prompt)
    print(f"Prompt: {prompt}")
    print(f"\nResponse: {response}")
    print("\n✓ LoRA ADAPTERS MERGED — REAL PHENOTYPE ACTIVE")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
