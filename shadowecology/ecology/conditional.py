# Author: Bradley R. Kinnard
# shadowecology/ecology/conditional.py
# Dialectical synthesis - holding contradiction without breaking

from shadowecology.ecology.lattice import Lattice
from shadowecology.ecology.merge import similarity
from shadowecology.ecology.tension import node_tension


# TENSION_THRESHOLD for conditional creation
TENSION_THRESHOLD = 1.5


# create conditional nodes from high-tension contradictions
def attempt_conditional(lattice: Lattice, current_step: int, active_node_ids: set[str]) -> None:
    # only consider active nodes
    active_nodes = [lattice.nodes[nid] for nid in active_node_ids if nid in lattice.nodes]

    # check all pairs
    for i, node_a in enumerate(active_nodes):
        for node_b in active_nodes[i+1:]:
            # both must have tags
            if not node_a["tags"] or not node_b["tags"]:
                continue

            # primary tags must differ (removed - same-tag contradictions are the most painful)
            # if node_a["tags"][0] == node_b["tags"][0]:
            #     continue

            # must be semantically close but not identical
            sim = similarity(node_a["content"], node_b["content"])
            if sim <= 0.85 or sim >= 0.95:
                continue

            # both must be confident
            if node_a["confidence"] < 0.6 or node_b["confidence"] < 0.6:
                continue

            # at least one must have high tension
            tension_a = node_tension(node_a, lattice, current_step)
            tension_b = node_tension(node_b, lattice, current_step)

            if tension_a < TENSION_THRESHOLD and tension_b < TENSION_THRESHOLD:
                continue

            # create conditional: higher tension becomes the condition
            if tension_a > tension_b:
                belief, condition = node_a, node_b
            else:
                belief, condition = node_b, node_a

            # birth dialectical synthesis
            conditional_content = f"I believe {belief['content']} when {condition['content']}"

            conditional_id = lattice.add_belief(
                content=conditional_content,
                confidence=(node_a["confidence"] + node_b["confidence"]) / 2.0,
                source=f"synthesis:{belief['id']}:{condition['id']}",
                current_step=current_step
            )

            # add support edges from both parents
            if node_a["id"] not in lattice.edges:
                lattice.edges[node_a["id"]] = {}
            lattice.edges[node_a["id"]][conditional_id] = 1.0

            if node_b["id"] not in lattice.edges:
                lattice.edges[node_b["id"]] = {}
            lattice.edges[node_b["id"]][conditional_id] = 1.0

            # keep parents alive - they're still needed
            node_a["last_active_step"] = current_step
            node_b["last_active_step"] = current_step
