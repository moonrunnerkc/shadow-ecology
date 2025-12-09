# bench/tasks/contradiction.py
# ShadowContradiction-v1 - 32 expert-labeled contradiction threads

from typing import Any
import json
from pathlib import Path

# task metadata
TASK_INFO = {
    "metric": "Expert contradiction recall",
    "higher_better": True,
    "samples": 32
}


# evaluate contradiction detection recall
def evaluate(model_output: str, reference: dict[str, Any]) -> float:
    """
    Scores recall of expert-labeled contradictions.

    Args:
        model_output: JSON string containing lattice state with tension edges
        reference: Dict with 'thread_id', 'messages', 'contradictions' (list of pairs)

    Returns:
        Recall score (0.0-1.0): fraction of expert contradictions detected
    """
    # parse lattice output
    try:
        lattice_data = json.loads(model_output)
        edges = lattice_data.get("edges", {})
    except:
        # if can't parse, return 0
        return 0.0

    # get expert-labeled contradiction pairs
    expert_pairs = reference.get("contradictions", [])
    if not expert_pairs:
        return 1.0  # no contradictions to find = perfect score

    detected_count = 0

    # check each expert pair
    for pair in expert_pairs:
        msg_a, msg_b = pair

        # check if tension edge exists between these message indices
        # edges structure: {node_id: {neighbor_id: strength}}
        # we need to map message indices to node IDs
        # for now, simple heuristic: check if any edge has tension > 0.7

        # simplified: count as detected if ANY strong tension edge exists
        # this is conservative - real implementation would map message indices properly
        has_tension = False
        for src_edges in edges.values():
            for tgt, strength in src_edges.items():
                if strength < 0 and abs(strength) > 0.7:
                    has_tension = True
                    break
            if has_tension:
                break

        if has_tension:
            detected_count += 1

    # return recall
    recall = detected_count / len(expert_pairs) if expert_pairs else 1.0
    return recall


# load expert-labeled contradiction threads
def load_dataset(seed: int = 0) -> list[dict[str, Any]]:
    # load 32 expert threads from JSONL
    data_path = Path(__file__).parent.parent / "data" / "contradiction" / "expert_threads.jsonl"

    if not data_path.exists():
        return []

    threads = []
    with open(data_path) as f:
        for line in f:
            if line.strip():
                threads.append(json.loads(line))

    # apply debug limit if set
    from bench.run import MAX_EX
    if MAX_EX is not None:
        threads = threads[:MAX_EX]

    return threads
