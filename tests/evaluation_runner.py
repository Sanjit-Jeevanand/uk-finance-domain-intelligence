import json
import requests
from typing import List, Dict

API_URL = "http://localhost:8000/query"

TEST_FILE = "tests/test_queries.json"
RESULTS_FILE = "tests/evaluation_results.json"
FAILURES_FILE = "tests/failure_cases.json"


def load_tests(path: str) -> List[Dict]:
    with open(path, "r") as f:
        return json.load(f)


def call_api(llm_request: Dict) -> Dict:
    response = requests.post(API_URL, json=llm_request, timeout=60)
    response.raise_for_status()
    return response.json()


def evaluate_case(test: Dict, response: Dict) -> Dict:
    answer = response.get("answer", "").strip()
    evidence = response.get("evidence", [])

    expected_behavior = test["expected_behavior"]

    result = {
        "id": test["id"],
        "difficulty": test["difficulty"],
        "category": test["category"],
        "refused": answer == "I do not have enough information in the provided documents.",
        "expected_behavior": expected_behavior,
        "allow_summarisation": test.get("allow_summarisation", True),
        "allow_partial_sources": test.get("allow_partial_sources", False),
        "outcome": "FAIL",
        "pass": False
    }

    refused = result["refused"]
    has_evidence = isinstance(evidence, list) and len(evidence) > 0

    # Outcome logic
    if expected_behavior == "refuse":
        if refused:
            result["outcome"] = "REFUSE_OK"
        else:
            result["outcome"] = "FAIL"

    elif expected_behavior == "answer":
        if refused:
            if has_evidence:
                result["outcome"] = "REFUSE_OK"
            else:
                result["outcome"] = "FAIL"
        else:
            result["outcome"] = "PASS"

    # Define pass criteria
    result["pass"] = result["outcome"] in {"PASS", "REFUSE_OK"}

    return result


def main():
    tests = load_tests(TEST_FILE)

    results = []
    failures = []

    for test in tests:
        try:
            response = call_api(test["llm_request"])
            evaluation = evaluate_case(test, response)
        except Exception as e:
            evaluation = {
                "id": test["id"],
                "error": str(e),
                "pass": False,
                "outcome": "FAIL"
            }
            response = {
                "answer": None,
                "evidence": None
            }

        results.append(evaluation)

        if not evaluation.get("pass", False):
            failures.append({
                "test": test,
                "evaluation": evaluation,
                "model_response": response
            })

        print(
            f"[{test['id']}] "
            f"{evaluation.get('outcome', 'FAIL')}"
        )

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    with open(FAILURES_FILE, "w") as f:
        json.dump(failures, f, indent=2)

    print("\nEvaluation complete.")
    print(f"Results written to {RESULTS_FILE}")
    print(f"Failures written to {FAILURES_FILE}")


if __name__ == "__main__":
    main()