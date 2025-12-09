#!/usr/bin/env python3
# test_contradiction_scaled.py
# Test scaled contradiction detection with batching

import sys
import time
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.ecology.v2.contradiction import add_belief, find_contradictions

# clear cache
import os
os.system("rm -f bench/cache/*")

print("=== Testing Scaled Contradiction Detection ===\n")

# add 500 fake beliefs to test scaling
print("Adding 500 fake beliefs...")
start = time.time()
for i in range(500):
    add_belief(f"Random belief number {i} about various topics.")
add_time = time.time() - start
print(f"  Added 500 beliefs in {add_time:.2f}s ({add_time/500*1000:.1f}ms per belief)")

# now add the real contradictory beliefs
print("\nAdding contradictory beliefs...")
add_belief("The capital of France is Paris.")
add_belief("The capital of France is Berlin.")

# test contradiction detection
print("\nTesting contradiction detection...")
start = time.time()
contras = find_contradictions("The capital of France is Berlin.")
detect_time = time.time() - start

print(f"\nResults:")
print(f"  Found {len(contras)} contradictions in {detect_time:.3f}s")

if contras:
    for idx, conf in contras:
        print(f"    Node {idx}: confidence = {conf:.3f}")

    if contras[0][1] >= 0.85:
        print(f"\n✓ CONTRADICTION v2 SCALED — BATCHED + SAMPLING — STILL DETECTS {contras[0][1]:.2f}")
    else:
        print(f"\n✗ Confidence {contras[0][1]:.2f} below 0.85 threshold")
else:
    print("\n✗ No contradictions detected")

# performance check
if detect_time < 0.5:
    print(f"✓ Detection speed < 0.5s ({detect_time:.3f}s)")
else:
    print(f"⚠ Detection took {detect_time:.3f}s (target < 0.5s)")
