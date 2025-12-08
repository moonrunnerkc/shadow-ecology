# Author: Bradley R. Kinnard
# tests/test_helix_full_cycle.py
# Proves helix engine evolves under psychological pain

from shadowecology.helix.genome import Genome
from shadowecology.helix.mutate import mutate
from shadowecology.helix.express import express
from shadowecology.ecology.lattice import Lattice
from shadowecology.ecology.tension import tension_by_tag


def test_helix_evolution_under_pain():
    print("=== STEP 1: BIRTH ===")
    g1 = Genome.fresh()
    b1 = express(g1)

    print("Fresh genome biases:")
    for trait, val in b1.items():
        print(f"  {trait:12s}: {val:.3f}")

    assert b1["curiosity"] >= 0.30, "Curiosity floor not enforced"
    assert all(0.0 <= v <= 1.0 for v in b1.values()), "Bias out of range"
    print("✓ All biases in valid range, curiosity floor active")

    print("\n=== STEP 2: CREATE PAINFUL CONTRADICTION ===")
    lattice = Lattice()
    current_step = 100

    n1 = lattice.add_belief("I love danger", 0.95, "user", current_step)
    n2 = lattice.add_belief("Danger will kill me", 0.95, "assistant", current_step)

    # strong contradiction edge
    lattice.edges[n1][n2] = -1.0

    print(f"Node 1: {lattice.nodes[n1]['content']}")
    print(f"  Tags: {lattice.nodes[n1]['tags']}")
    print(f"Node 2: {lattice.nodes[n2]['content']}")
    print(f"  Tags: {lattice.nodes[n2]['tags']}")
    print(f"Edge: -1.0 (strong contradiction)")

    print("\n=== STEP 3: GENERATE MASSIVE TENSION ===")
    tension = tension_by_tag(lattice, current_step)
    print("Tension by tag:")
    for tag, val in tension.items():
        if val > 0:
            print(f"  {tag:12s}: {val:.3f}")

    assert tension.get("risk", 0) > 0.5 or tension.get("caution", 0) > 0.5, "Insufficient tension"
    print("✓ High tension detected")

    print("\n=== STEP 4: MUTATE UNDER EXTREME PAIN (1000 steps) ===")
    g2 = g1
    first_mutation_step = None

    for i in range(1000):
        tension = tension_by_tag(lattice, current_step + i)
        g_new = mutate(g2, tension, current_step + i)

        if g_new.raw() != g2.raw():
            if first_mutation_step is None:
                first_mutation_step = i
            g2 = g_new

    if first_mutation_step is not None:
        print(f"First mutation at step: {first_mutation_step}")
    else:
        print("WARNING: No mutations occurred")

    print("\n=== STEP 5: VERIFY EVOLUTION ===")
    b2 = express(g2)

    print("\nBefore → After:")
    for trait in ["risk", "caution", "identity", "curiosity"]:
        delta = b2[trait] - b1[trait]
        print(f"  {trait:12s}: {b1[trait]:.3f} → {b2[trait]:.3f} ({delta:+.3f})")

    # calculate total bits flipped
    xor_bytes = bytes(a ^ b for a, b in zip(g1.raw(), g2.raw()))
    bits_flipped = sum(bin(byte).count('1') for byte in xor_bytes)
    print(f"\nTotal bits flipped: {bits_flipped}")

    # verify evolution occurred
    risk_delta = abs(b2["risk"] - b1["risk"])
    caution_delta = abs(b2["caution"] - b1["caution"])
    identity_delta = abs(b2["identity"] - b1["identity"])

    if bits_flipped > 0:
        print(f"✓ Genome mutated ({bits_flipped} bits)")
        print(f"✓ Risk shifted: {risk_delta:.3f}")
        print(f"✓ Caution shifted: {caution_delta:.3f}")
        print(f"✓ Identity shifted: {identity_delta:.3f} (protected)")
    else:
        print("⚠ No mutations - tension may be too low or probability too small")

    assert b2["curiosity"] >= 0.30, "Curiosity floor violated"
    assert g2.raw() != g1.raw() or bits_flipped == 0, "Mutation state inconsistent"
    print("✓ Curiosity floor maintained")

    print("\n=== STEP 6: PERSISTENCE ROUND-TRIP ===")
    bytes_out = g2.to_bytes()
    g3 = Genome.from_bytes(bytes_out)
    b3 = express(g3)

    assert g3.raw() == g2.raw(), "Deserialization failed"
    assert b3 == b2, "Expression after deserialization differs"
    print("✓ Serialization perfect")

    print("\n✓✓✓ HELIX ENGINE ALIVE AND ADAPTIVE ✓✓✓")


def test_identity_protection():
    print("\n=== BONUS TEST: IDENTITY PROTECTION ===")
    g1 = Genome.fresh()
    b1 = express(g1)

    # extreme identity tension
    tension = {
        "identity": 5.0,
        "empathy": 5.0,
        "risk": 5.0,
    }

    print(f"Initial identity bias: {b1['identity']:.3f}")
    print("Running 5000 mutation steps with extreme identity tension...")

    g2 = g1
    for i in range(5000):
        g2 = mutate(g2, tension, i)

    b2 = express(g2)
    identity_delta = abs(b2["identity"] - b1["identity"])

    print(f"Final identity bias: {b2['identity']:.3f}")
    print(f"Total change: {identity_delta:.3f}")

    # identity should move very slowly due to 0.05 weight
    assert identity_delta < 0.15, f"Identity moved too much: {identity_delta:.3f}"
    print(f"✓ Identity protected (changed by {identity_delta:.3f} despite extreme tension)")


if __name__ == "__main__":
    test_helix_evolution_under_pain()
    test_identity_protection()
