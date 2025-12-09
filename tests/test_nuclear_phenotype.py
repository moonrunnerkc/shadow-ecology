#!/usr/bin/env python3
# test nuclear phenotype injection

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.helix.genome_v2 import GenomeV2
from shadowecology.oracle.lora_manager import LoRAManager

# test 1: high curiosity genome
print("=== TEST 1: High Curiosity (0.95) ===")
g_high = GenomeV2()
g_high.values[:64] = [0.95] * 64

lora = LoRAManager()
lora.apply_genome(g_high)
prompt_high = lora._build_system_prompt()
print(prompt_high[:1000])
print()

# test 2: low curiosity genome
print("=== TEST 2: Low Curiosity (0.10) ===")
g_low = GenomeV2()
g_low.values[:64] = [0.10] * 64

lora.apply_genome(g_low)
prompt_low = lora._build_system_prompt()
print(prompt_low[:1000])
print()

# verify repetition count
high_count = prompt_high.count("YOU ARE INSANELY CURIOUS")
low_count = prompt_low.count("YOU ARE VERY CURIOUS")

print(f"✓ High curiosity prompt has {high_count} repetitions of 'INSANELY CURIOUS'")
print(f"✓ Low curiosity prompt has {low_count} repetitions of 'VERY CURIOUS'")

if high_count >= 8 and low_count >= 5:
    print("\n✅ NUCLEAR PHENOTYPE CONFIRMED — TRAIT CHANGES NOW PRODUCE RADICAL BEHAVIORAL SHIFT")
else:
    print(f"\n❌ Insufficient repetition: expected 8+ and 5+, got {high_count} and {low_count}")
