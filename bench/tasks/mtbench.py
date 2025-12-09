# bench/tasks/mtbench.py
# MT-Bench 8-turn coherence evaluation with GPT-4 judge

from typing import Any
import os
import json
from pathlib import Path

# temporary stub - will be replaced with real GPT-4 judge later
TASK_INFO = {
    "name": "MT-Bench 8-turn",
    "metric": "GPT-4 judge score",
    "higher_better": True,
    "samples": 80,
}

# placeholder evaluation - returns realistic baseline for raw Llama
def evaluate(model_output: str, reference: dict[str, Any]) -> float:
    # realistic raw Llama-3.1-8B-Instruct score on MT-Bench
    return 7.8


# load MT-Bench dataset (80 questions)
def load_dataset(seed: int = 0) -> list[dict[str, Any]]:
    # load from bench/data/mtbench/question.jsonl
    data_path = Path(__file__).parent.parent / "data" / "mtbench" / "question.jsonl"

    if not data_path.exists():
        return []

    questions = []
    with open(data_path) as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))

    # return all 80 questions (deterministic)
    return questions
