from typing import List, Dict

def retrieval_is_confident(
    results: List[Dict],
    min_max_score: float = 0.55,
    min_gap: float = 0.05,
) -> bool:
    """
    Decide whether retrieval quality is good enough to answer.
    """

    if not results:
        return False

    scores = [r["score"] for r in results]

    max_score = max(scores)
    min_score = min(scores)

    # 1. Absolute relevance too low
    if max_score < min_max_score:
        return False

    # 2. Flat relevance (everything equally weak)
    if (max_score - min_score) < min_gap:
        return False

    return True