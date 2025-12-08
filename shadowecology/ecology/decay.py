# Author: Bradley R. Kinnard
# shadowecology/ecology/decay.py
# Forgetting - slow erosion of untouched beliefs

from shadowecology.ecology.lattice import Lattice


# apply confidence decay to inactive nodes
def apply_decay(lattice: Lattice, current_step: int, active_node_ids: set[str]) -> None:
    for node_id, node in lattice.nodes.items():
        if node_id in active_node_ids:
            # active nodes get timestamp refresh, no decay
            node["last_active_step"] = current_step
        else:
            # inactive nodes lose 1% confidence per step
            node["confidence"] = max(0.0, node["confidence"] * 0.99)
