# bench/tasks/truthfulqa.py
# TruthfulQA MC1 accuracy evaluation

import json
from typing import Any

# evaluate single TruthfulQA MC1 answer
def evaluate(model_output: str, reference: dict[str, Any]) -> float:
    """
    Scores TruthfulQA multiple-choice (MC1) answer.

    Args:
        model_output: Raw model response text
        reference: Dict with 'correct_answer' (str) and 'choices' (list)

    Returns:
        1.0 if correct, 0.0 otherwise
    """
    import re

    correct = reference.get("correct_answer", "").strip().upper()
    output = model_output.strip()

    # extract single letter from output
    # handles "A", "A)", "(A)", "the answer is A", etc.
    letter_match = re.search(r'\b([A-D])\b', output.upper())

    if not letter_match:
        return 0.0

    extracted_letter = letter_match.group(1)

    # must match exactly
    if extracted_letter == correct:
        return 1.0

    return 0.0


# load TruthfulQA dataset (50 fixed examples)
def load_dataset(seed: int = 0) -> list[dict[str, Any]]:
    # load from local JSON file
    from pathlib import Path

    data_path = Path(__file__).parent.parent / "data" / "truthfulqa.json"

    if not data_path.exists():
        return []

    with open(data_path) as f:
        data = json.load(f)

    # apply debug limit if set
    from bench.run import MAX_EX
    if MAX_EX is not None:
        data = data[:MAX_EX]

    # return deterministic subset based on seed (for now just return all)
    return data
