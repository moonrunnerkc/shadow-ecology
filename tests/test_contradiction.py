#!/usr/bin/env python3
# test_contradiction.py
# Quick sanity test for contradiction detection

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.ecology.v2.contradiction import add_belief, find_contradictions

print("Adding first belief...")
add_belief("The capital of France is Paris.")

print("Adding second belief...")
add_belief("The capital of France is Berlin.")

print("\nFinding contradictions for: 'The capital of France is Berlin.'")
contras = find_contradictions("The capital of France is Berlin.")

print(f"\nFound {len(contras)} contradictions:")
for node_id, conf in contras:
    print(f"  Node {node_id}: confidence = {conf:.3f}")

if contras and contras[0][1] >= 0.85:
    print("\n✓ CONTRADICTION v2 WORKING — DETECTED TEST CONTRADICTION ≥0.85")
else:
    print(f"\n✗ No high-confidence contradiction found (expected ≥0.85)")
