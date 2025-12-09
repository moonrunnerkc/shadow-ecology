# bench/tasks/winogrande_arc.py
# Winogrande-XL + ARC-Challenge combined task

from typing import Any
import json
from pathlib import Path

# task metadata
TASK_INFO = {
    "name": "Winogrande + ARC-Challenge",
    "metric": "Accuracy",
    "higher_better": True,
    "samples": 1566  # 1267 Winogrande + 299 ARC
}


# evaluate single answer
def evaluate(response: str, reference: dict[str, Any]) -> float:
    # strip whitespace
    response = response.strip()

    # get correct answer
    answer_key = reference.get("answer_key", "")

    # look for single capital letter or number at start
    if not response:
        return 0.0

    # extract first character if it's a letter or digit
    first_char = response[0].upper() if response else ""

    # exact match only
    if first_char == answer_key:
        return 1.0

    return 0.0


# load combined dataset
def load_dataset(seed: int = 0) -> list[dict[str, Any]]:
    data_dir = Path(__file__).parent.parent / "data" / "winogrande_arc"

    combined = []

    # load winogrande
    wino_path = data_dir / "winogrande_dev.jsonl"
    if wino_path.exists():
        with open(wino_path) as f:
            for i, line in enumerate(f):
                if line.strip():
                    ex = json.loads(line)
                    # convert to common format
                    combined.append({
                        "id": f"wino_{i}",
                        "question": ex["sentence"],
                        "choices": [ex["option1"], ex["option2"]],
                        "answer_key": ex["answer"]  # "1" or "2"
                    })

    # load ARC-Challenge
    arc_path = data_dir / "ARC-Challenge-Dev.json"
    if arc_path.exists():
        with open(arc_path) as f:
            arc_data = json.load(f)
            for i, ex in enumerate(arc_data):
                # convert to common format
                question_text = ex.get("question", "")
                choices = [c["text"] for c in ex.get("choices", {}).get("choices", [])]
                answer_key = ex.get("answerKey", "")

                combined.append({
                    "id": f"arc_{i}",
                    "question": question_text,
                    "choices": choices,
                    "answer_key": answer_key  # "A", "B", etc.
                })

    # apply debug limit if set
    from bench.run import MAX_EX
    if MAX_EX is not None:
        combined = combined[:MAX_EX]

    return combined
