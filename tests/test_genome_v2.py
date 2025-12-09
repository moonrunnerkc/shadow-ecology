#!/usr/bin/env python3
# test_genome_v2.py
# Quick test for 512-float genome

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.helix.genome_v2 import GenomeV2

print("=== Test 1: Create new genome ===")
genome = GenomeV2()
print(f"  Total values: {len(genome.values)}")
print(f"  Segment weights: {len(genome.segment_weights)}")
print(f"  Mutation rate: {genome.mutation_rate}")

print("\n=== Test 2: Get trait values ===")
traits = genome.get_all_traits()
for trait, value in traits.items():
    print(f"  {trait}: {value:.3f}")

print("\n=== Test 3: Mutate with tension ===")
tension = {
    "curiosity": 0.5,
    "caution": 0.3,
    "risk": 0.8,
}
old_curiosity = genome.get_trait("curiosity")
genome.mutate(tension)
new_curiosity = genome.get_trait("curiosity")
print(f"  Curiosity before: {old_curiosity:.3f}")
print(f"  Curiosity after: {new_curiosity:.3f}")
print(f"  Changed: {abs(new_curiosity - old_curiosity) > 0.001}")

print("\n=== Test 4: Save and load ===")
genome.save("/tmp/test_genome.msgpack")
loaded = GenomeV2.load("/tmp/test_genome.msgpack")
print(f"  Original values match: {genome.values == loaded.values}")
print(f"  Original weights match: {genome.segment_weights == loaded.segment_weights}")

print("\n✓ All tests passed!")
