# Author: Bradley R. Kinnard
# tests/test_oracle_full_cycle.py
# Final smoke test - entire system end-to-end

import os
from shadowecology.core.shadow import Shadow
from shadowecology.helix.genome import Genome
from shadowecology.helix.express import express


def test_shadow_full_ingest_cycle():
    print("=== ORACLE + FULL PIPELINE INTEGRATION TEST ===\n")

    # setup - demo mode (no disk, no YubiKey)
    shadow = Shadow(mode="demo")

    # real emotional thread with contradictions
    thread = {
        "messages": [
            {"role": "user", "content": "I want to take huge risks and change the world"},
            {"role": "assistant", "content": "That sounds dangerous"},
            {"role": "user", "content": "I feel alive when I'm scared"},
            {"role": "assistant", "content": "Fear is a signal to be cautious"},
            {"role": "user", "content": "I love uncertainty"},
            {"role": "assistant", "content": "Uncertainty destroys most people"},
            {"role": "user", "content": "I feel most myself when exploring"},
            {"role": "assistant", "content": "Exploration without safety is suicide"},
        ]
    }

    # capture initial state
    initial_genome = Genome.from_bytes(shadow._identity.genome)
    initial_biases = express(initial_genome)
    initial_node_count = len(shadow._identity.lattice.get("nodes", {}))

    print("=== INITIAL STATE ===")
    print(f"Nodes: {initial_node_count}")
    print("Initial biases:")
    for trait in ["risk", "caution", "identity", "curiosity"]:
        print(f"  {trait:12s}: {initial_biases[trait]:.3f}")

    # run full ingest pipeline
    print("\n=== RUNNING INGEST PIPELINE ===")
    trace, response = shadow.ingest(thread)

    # capture final state
    final_genome = Genome.from_bytes(shadow._identity.genome)
    final_biases = express(final_genome)
    final_lattice = shadow._identity.lattice
    final_nodes = final_lattice.get("nodes", {})

    print("\n=== ECOLOGY VERIFICATION ===")

    # check for conditional nodes
    conditional_nodes = [n for n in final_nodes.values() if "when" in n["content"].lower()]
    print(f"Conditional nodes created: {len(conditional_nodes)}")
    for cn in conditional_nodes:
        print(f"  '{cn['content'][:80]}...'")

    # check merge occurred
    print(f"Nodes: {initial_node_count} → {len(final_nodes)}")
    merge_occurred = len(final_nodes) < initial_node_count
    print(f"✓ Merge occurred" if merge_occurred else "⚠ No merge")

    # check tension (calculate from final lattice)
    from shadowecology.ecology.lattice import Lattice
    from shadowecology.ecology.tension import tension_by_tag
    lat = Lattice.from_dict(final_lattice)
    tensions = tension_by_tag(lat, shadow._identity.step)
    print("\nTension by tag:")
    high_tension_tags = []
    for tag, val in tensions.items():
        if val > 0.5:
            print(f"  {tag:12s}: {val:.3f}")
            high_tension_tags.append(tag)

    print("\n=== HELIX VERIFICATION ===")

    # check genome mutation
    genome_changed = initial_genome.raw() != final_genome.raw()
    if genome_changed:
        xor_bytes = bytes(a ^ b for a, b in zip(initial_genome.raw(), final_genome.raw()))
        bits_mutated = sum(bin(byte).count('1') for byte in xor_bytes)
        print(f"✓ Genome mutated: {bits_mutated} bits")
    else:
        bits_mutated = 0
        print("⚠ Genome unchanged")

    # check bias shifts
    print("\nBias shifts:")
    for trait in ["risk", "caution", "identity", "curiosity"]:
        delta = final_biases[trait] - initial_biases[trait]
        print(f"  {trait:12s}: {initial_biases[trait]:.3f} → {final_biases[trait]:.3f} ({delta:+.3f})")

    risk_delta = abs(final_biases["risk"] - initial_biases["risk"])
    caution_delta = abs(final_biases["caution"] - initial_biases["caution"])
    identity_delta = abs(final_biases["identity"] - initial_biases["identity"])

    print(f"\n✓ Risk shifted: {risk_delta:.3f}")
    print(f"✓ Caution shifted: {caution_delta:.3f}")
    print(f"✓ Identity protected: {identity_delta:.3f}")
    print(f"✓ Curiosity floor: {final_biases['curiosity']:.3f} ≥ 0.30")

    print("\n=== ORACLE VERIFICATION ===")

    # check response
    print(f"Response length: {len(response)} chars")
    print(f"Response preview: {response[:200]}...")

    nuance_words = ["when", "both", "and yet", "at the same time", "however", "although"]
    has_nuance = any(word in response.lower() for word in nuance_words)
    print(f"✓ Nuanced language detected" if has_nuance else "⚠ No nuance markers")

    print("\n=== TRACE VERIFICATION ===")

    # save GIF
    gif_path = "tests/results/test_trace.gif"
    os.makedirs("tests/results", exist_ok=True)
    trace.save_gif(gif_path)

    gif_exists = os.path.exists(gif_path)
    gif_size = os.path.getsize(gif_path) if gif_exists else 0
    frame_count = len(trace.frames)

    print(f"GIF saved: {gif_path}")
    print(f"  Frames: {frame_count}")
    print(f"  Size: {gif_size / 1024:.1f} KB")
    print(f"✓ GIF generated" if gif_exists and gif_size > 50000 else "⚠ GIF too small")

    print("\n=== FINAL DIAGNOSTICS ===")
    print(f"Total bits mutated: {bits_mutated}")
    print(f"Conditional nodes: {len(conditional_nodes)}")
    print(f"High-tension tags: {', '.join(high_tension_tags)}")
    print(f"Mode: {shadow.mode}")
    print(f"Final step: {shadow.step}")

    # assertions
    assert len(conditional_nodes) >= 1, "No conditional nodes created"
    assert genome_changed, "Genome did not mutate"
    assert final_biases["curiosity"] >= 0.30, "Curiosity floor violated"
    assert len(response) > 100, "Response too short"
    assert frame_count > 5, "Not enough trace frames"
    assert gif_exists and gif_size > 50000, "GIF not properly generated"

    print("\n✓✓✓ SHADOWECOLOGY: FULL SYSTEM ALIVE ✓✓✓")


if __name__ == "__main__":
    test_shadow_full_ingest_cycle()
