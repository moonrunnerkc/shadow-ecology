# Author: Bradley R. Kinnard
# Test vault cycle WITHOUT YubiKey (passphrase-only for Day 1 testing)

from shadowecology.vault.vault import load_or_create, save_atomic, load
from shadowecology.vault import keymaster
import os

# Temporarily mock YubiKey challenge for testing
def mock_yubikey():
    return os.urandom(20)  # fake deterministic response for test

# Patch it
keymaster.yubikey_challenge = mock_yubikey

# Step 1: Create fresh identity
print("Step 1: Creating test_cycle identity...")
identity = load_or_create("test_cycle")
print(f"  Created: {identity['identity_id']} at step {identity['step']}")
original_genome = identity['genome']

# Step 2: Modify in memory
print("\nStep 2: Modifying in memory...")
identity['step'] = 42
identity['lattice']['nodes']['test_node'] = {
    'content': 'test belief',
    'confidence': 0.85,
    'tags': ['curiosity']
}
print(f"  Modified step to {identity['step']}")
print(f"  Added test node")

# Step 3: Save atomically
print("\nStep 3: Saving modifications...")
save_atomic("test_cycle", identity)
print("  Saved successfully")

# Step 4: Reload from disk
print("\nStep 4: Reloading from disk...")
reloaded = load("test_cycle")
print(f"  Reloaded: {reloaded['identity_id']} at step {reloaded['step']}")

# Step 5: Verify identical
print("\nStep 5: Verifying integrity...")
assert reloaded['identity_id'] == identity['identity_id'], "ID mismatch"
assert reloaded['step'] == 42, f"Step mismatch: expected 42, got {reloaded['step']}"
assert reloaded['genome'] == original_genome, "Genome corrupted"
assert 'test_node' in reloaded['lattice']['nodes'], "Test node missing"
assert reloaded['lattice']['nodes']['test_node']['confidence'] == 0.85, "Node data corrupted"

print("  ✓ Identity ID matches")
print("  ✓ Step counter persisted")
print("  ✓ Genome intact")
print("  ✓ Lattice modifications saved")
print("\n✅ Full cycle test PASSED")
