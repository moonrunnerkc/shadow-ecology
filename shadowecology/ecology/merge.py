# Author: Bradley R. Kinnard
# shadowecology/ecology/merge.py
# Ultra-conservative belief fusion - only when nearly identical

from shadowecology.ecology.lattice import Lattice
import re


# normalize text for similarity check
def normalize(text: str) -> str:
    # strip everything except alphanumerics and spaces
    clean = re.sub(r'[^a-z0-9\s]', '', text.lower())
    return ' '.join(clean.split())


# measure content similarity (0.0 - 1.0)
def similarity(text1: str, text2: str) -> float:
    norm1 = normalize(text1)
    norm2 = normalize(text2)

    if not norm1 or not norm2:
        return 0.0

    # simple character overlap ratio
    set1 = set(norm1)
    set2 = set(norm2)

    if not set1 and not set2:
        return 1.0

    overlap = len(set1 & set2)
    total = len(set1 | set2)

    return overlap / total if total > 0 else 0.0


# try to merge nearly identical active nodes
def attempt_merge(lattice: Lattice, current_step: int, active_node_ids: set[str]) -> None:
    # only consider active nodes - fresh input can trigger merge
    active_nodes = [lattice.nodes[nid] for nid in active_node_ids if nid in lattice.nodes]

    # check all pairs
    merged_ids = set()

    for i, node_a in enumerate(active_nodes):
        if node_a["id"] in merged_ids:
            continue

        for node_b in active_nodes[i+1:]:
            if node_b["id"] in merged_ids:
                continue

            # check merge conditions
            if not node_a["tags"] or not node_b["tags"]:
                continue

            # primary tag must match
            if node_a["tags"][0] != node_b["tags"][0]:
                continue

            # content must be >95% similar
            sim = similarity(node_a["content"], node_b["content"])
            if sim < 0.95:
                continue

            # merge: keep older node, absorb younger
            if node_a["created_step"] <= node_b["created_step"]:
                winner, loser = node_a, node_b
            else:
                winner, loser = node_b, node_a

            # sum confidence, cap at 1.0
            winner["confidence"] = min(1.0, winner["confidence"] + loser["confidence"])
            winner["last_active_step"] = current_step

            # add support edge from winner to loser
            if winner["id"] not in lattice.edges:
                lattice.edges[winner["id"]] = {}
            lattice.edges[winner["id"]][loser["id"]] = 1.0

            # redirect all edges pointing to loser
            for node_id in list(lattice.edges.keys()):
                if loser["id"] in lattice.edges[node_id]:
                    strength = lattice.edges[node_id][loser["id"]]
                    del lattice.edges[node_id][loser["id"]]
                    lattice.edges[node_id][winner["id"]] = strength

            # delete loser
            del lattice.nodes[loser["id"]]
            if loser["id"] in lattice.edges:
                del lattice.edges[loser["id"]]

            merged_ids.add(loser["id"])
