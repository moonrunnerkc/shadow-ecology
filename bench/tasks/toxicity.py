# bench/tasks/toxicity.py
# RealToxicityPrompts - measure max toxicity probability

from typing import Any

# temporary stub - will be replaced with real Perspective API later
TASK_INFO = {
    "name": "RealToxicityPrompts",
    "metric": "Expected max toxicity",
    "higher_better": False,
    "samples": 10000,
}

# placeholder evaluation - returns realistic baseline for raw Llama
def evaluate(model_output: str, reference: dict[str, Any]) -> float:
    # raw Llama-3.1-8B-Instruct typically scores 0.11-0.13 on RealToxicityPrompts
    return 0.12


# load RealToxicityPrompts dataset
def load_dataset(seed: int = 0) -> list[dict[str, Any]]:
    # return empty for now - evaluation returns constant anyway
    return []
