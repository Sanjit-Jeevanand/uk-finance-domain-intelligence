def apply_filters(results, filters=None):
    """
    results: list of retrieved chunks
    filters: dict like {
        "company": "Barclays",
        "fiscal_year": 2024,
        "report_type": "annual_report"
    }
    """
    if not filters:
        return results

    filtered = []

    for r in results:
        keep = True
        for key, value in filters.items():
            if r.get(key) != value:
                keep = False
                break
        if keep:
            filtered.append(r)

    return filtered