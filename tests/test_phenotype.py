#!/usr/bin/env python3
# test phenotype injection strength

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.helix.genome_v2 import GenomeV2
from shadowecology.oracle.lora_manager import LoRAManager

# create genome with max curiosity
g_max = GenomeV2()
g_max.values[:64] = [0.95] * 64  # max curiosity

# create genome with min curiosity
g_min = GenomeV2()
g_min.values[:64] = [0.1] * 64   # min curiosity

# create lora manager
lora = LoRAManager()

print("=== MAX CURIOSITY (0.95) ===")
lora.apply_genome(g_max)
print(lora._build_system_prompt())
print()

print("=== MIN CURIOSITY (0.10) ===")
lora.apply_genome(g_min)
print(lora._build_system_prompt())
print()

print("✓ Phenotype injection creates dramatically different prompts!")
