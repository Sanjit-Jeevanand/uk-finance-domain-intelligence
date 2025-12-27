def test_query_api_contract(client):
    payload = {
        "query": "What funding and liquidity risks did Barclays highlight in 2024?",
        "company": "Barclays",
        "fiscal_year": 2024,
        "top_k": 4
    }

    response = client.post("/query", json=payload)

    assert response.status_code == 200

    data = response.json()

    # --- Contract checks ---
    assert isinstance(data, dict), "Response must be JSON object"
    assert "answer" in data, "`answer` key must always be present"
    assert isinstance(data["answer"], str), "`answer` must be a string"