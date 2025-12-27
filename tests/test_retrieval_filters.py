def test_company_filter_is_respected(client):
    payload = {
        "query": "What risks did HSBC highlight in 2024?",
        "company": "HSBC",
        "fiscal_year": 2024,
        "top_k": 5
    }

    response = client.post("/query", json=payload)
    data = response.json()

    # If evidence is present, it must match company filter
    if "evidence" in data:
        for chunk in data["evidence"]:
            assert chunk["company"] == "HSBC", (
                f"Found non-HSBC chunk: {chunk['company']}"
            )

def test_top_k_is_respected(client):
    payload = {
        "query": "What risks did Barclays highlight in 2024?",
        "company": "Barclays",
        "fiscal_year": 2024,
        "top_k": 3
    }

    response = client.post("/query", json=payload)
    data = response.json()

    if "evidence" in data:
        assert len(data["evidence"]) <= 3, "Returned more chunks than top_k"