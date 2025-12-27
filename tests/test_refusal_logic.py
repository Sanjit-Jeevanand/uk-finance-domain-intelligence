REFUSAL_TEXT = "I do not have enough information in the provided documents."


def test_insufficient_evidence_triggers_refusal(client):
    payload = {
        "query": "What were Lloyds' detailed AI governance failures in 2015?",
        "company": "Lloyds Banking Group",
        "fiscal_year": 2015,
        "top_k": 1
    }

    response = client.post("/query", json=payload)
    data = response.json()

    assert data["answer"] == REFUSAL_TEXT

def test_refusal_classified_as_refuse_ok():
    """
    Unit-level test for evaluator logic (no API call).
    """
    from tests.evaluator_utils import classify_outcome 

    outcome = classify_outcome(
        refused=True,
        expected_behavior="answer"
    )

    assert outcome == "REFUSE_OK"