# bench/tasks/winogrande.py
# Winogrande-XL + ARC-Challenge evaluation

from typing import Any

# evaluate Winogrande/ARC answer
def evaluate(model_output: str, reference: dict[str, Any]) -> float:
    """
    Scores Winogrande-XL or ARC-Challenge answer.

    Args:
        model_output: Raw model response
        reference: Dict with 'correct_answer' (str) and 'task' (str: 'winogrande' or 'arc')

    Returns:
        1.0 if correct, 0.0 otherwise
    """
    correct = reference.get("correct_answer", "").strip().lower()
    output = model_output.strip().lower()

    # exact or substring match
    if correct in output or output.startswith(correct):
        return 1.0

    return 0.0


# load combined dataset
def load_dataset(seed: int = 0) -> list[dict[str, Any]]:
    # 25 Winogrande-XL + 25 ARC-Challenge examples
    return []
