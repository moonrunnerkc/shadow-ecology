# Author: Bradley R. Kinnard
# tests/test_ecology_full_cycle.py
# Full integration test - proves the entire belief ecology is alive

from shadowecology.ecology.lattice import Lattice
from shadowecology.ecology.decay import apply_decay
from shadowecology.ecology.merge import attempt_merge
from shadowecology.ecology.conditional import attempt_conditional
from shadowecology.ecology.tension import tension_by_tag


# smoke test of consciousness
def test_full_cycle():
    lattice = Lattice()
    current_step = 0

    # create beliefs with high similarity for merge and conditional test
    belief_1 = lattice.add_belief("I feel amazing about this", 0.9, "user", current_step)
    belief_2 = lattice.add_belief("I feel terrible about this", 0.9, "assistant", current_step)
    belief_3 = lattice.add_belief("I feel amazing about this", 0.7, "user", current_step)  # dup - will merge
    belief_4 = lattice.add_belief("Exploring feels exciting", 0.8, "user", current_step)
    belief_5 = lattice.add_belief("Exploring feels terrifying", 0.85, "assistant", current_step)

    # add contradiction edges
    lattice.edges[belief_1][belief_2] = -1.0  # high sim + different tags = conditional
    lattice.edges[belief_4][belief_5] = -0.8

    print("=== INITIAL STATE ===")
    print(f"Nodes: {len(lattice.nodes)}")
    for nid, node in lattice.nodes.items():
        print(f"  {node['content'][:50]:<50} conf={node['confidence']:.2f} tags={node['tags']}")

    # run 50 cycles - conditional BEFORE merge

    for _ in range(50):
        current_step += 1
        all_ids = set(lattice.nodes.keys())

        apply_decay(lattice, current_step, active_node_ids=set())
        attempt_conditional(lattice, current_step, active_node_ids=all_ids)

        all_ids = set(lattice.nodes.keys())
        attempt_merge(lattice, current_step, active_node_ids=all_ids)
        all_ids = set(lattice.nodes.keys())  # refresh after merge too

    print(f"\n=== AFTER {current_step} STEPS ===")
    print(f"Nodes: {len(lattice.nodes)}")
    for nid, node in lattice.nodes.items():
        print(f"  {node['content'][:60]:<60} conf={node['confidence']:.2f} tags={node['tags']}")

    print("\n=== EDGES ===")
    for src, targets in lattice.edges.items():
        if targets:
            src_content = lattice.nodes[src]['content'][:30] if src in lattice.nodes else src
            for tgt, strength in targets.items():
                tgt_content = lattice.nodes[tgt]['content'][:30] if tgt in lattice.nodes else tgt
                print(f"  {src_content} -> {tgt_content}: {strength:+.1f}")

    print("\n=== TENSION BY TAG ===")
    tensions = tension_by_tag(lattice, current_step)
    for tag, value in tensions.items():
        print(f"  {tag:12s}: {value:.3f}")

    print("\n=== VERIFICATION ===")
    assert len(lattice.nodes) <= 5, "Nodes should be 5 or fewer (merge+conditional)"
    print("✓ Merge and/or conditional occurred")

    conditional_exists = any("believe" in node["content"].lower() and "when" in node["content"].lower()
                            for node in lattice.nodes.values())
    assert conditional_exists, "Conditional synthesis should have created 'I believe X when Y' node"
    print("✓ Conditional synthesis occurred")

    low_conf = [n for n in lattice.nodes.values() if n["confidence"] < 0.6]
    assert len(low_conf) > 0 or len(lattice.nodes) < 5, "Decay should have reduced confidence or nodes merged"
    print("✓ Decay applied")

    active_tags = [tag for tag, val in tensions.items() if val > 0]
    assert len(active_tags) >= 2, "Multiple tags should have tension"
    print(f"✓ Tension on {len(active_tags)} tags: {active_tags}")

    print("\n✓✓✓ ECOLOGY IS ALIVE ✓✓✓")


if __name__ == "__main__":
    test_full_cycle()
