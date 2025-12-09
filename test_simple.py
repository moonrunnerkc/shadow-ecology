#!/usr/bin/env python3
# test_simple.py

import sys
sys.path.insert(0, "/home/brad/shadowecology")

print("Test 1: Add first belief")
from shadowecology.ecology.v2 import contradiction
idx1 = contradiction.add_belief("Paris is the capital of France")
print(f"  Added with index: {idx1}")
print(f"  Total texts: {len(contradiction._texts)}")

print("\nTest 2: Add second belief")
idx2 = contradiction.add_belief("Berlin is the capital of France")
print(f"  Added with index: {idx2}")
print(f"  Total texts: {len(contradiction._texts)}")

print("\nTest 3: Find contradictions")
contras = contradiction.find_contradictions("Berlin is the capital of France")
print(f"  Found: {contras}")

if contras:
    print(f"\n✓ SUCCESS: Found contradiction with confidence {contras[0][1]:.3f}")
    if contras[0][1] >= 0.85:
        print("CONTRADICTION v2 WORKING — DETECTED TEST CONTRADICTION ≥0.85")
else:
    print("\n✗ FAILED: No contradiction detected")
