# Author: Bradley R. Kinnard
# shadowecology/ecology/tension.py
# Pain calculation - drives genome mutation

from shadowecology.ecology.lattice import Lattice


# calculate tension for a single node
def node_tension(node: dict, lattice: Lattice, current_step: int) -> float:
    confidence = node["confidence"]

    # count negative edges (contradictions)
    contradiction_count = sum(
        1 for strength in lattice.edges.get(node["id"], {}).values() if strength < 0
    )

    # inactive beliefs hurt more over time
    steps_inactive = current_step - node["last_active_step"]
    age_factor = 1.0 + (steps_inactive * 0.02)

    return confidence * contradiction_count * age_factor


# aggregate tension by tag - this drives mutation
def tension_by_tag(lattice: Lattice, current_step: int) -> dict[str, float]:
    # init all 8 tags to zero
    tension = {
        "identity": 0.0,
        "empathy": 0.0,
        "risk": 0.0,
        "caution": 0.0,
        "curiosity": 0.0,
        "humor": 0.0,
        "depth": 0.0,
        "verbosity": 0.0,
    }

    # sum tension from all nodes
    for node in lattice.nodes.values():
        node_pain = node_tension(node, lattice, current_step)

        for tag in node["tags"]:
            if tag in tension:
                tension[tag] += node_pain

    return tension
