import os
import streamlit as st
import requests
import re

API_BASE_URL = "https://finance-dis-521270728838.europe-west1.run.app"

st.title("UK Finance Domain Intelligence")
st.write("Ask questions about UK finance data and get answers with cited evidence.")

with st.form("query_form"):

    st.subheader("Question")
    query = st.text_area("Ask a question")

    with st.expander("Filters (optional)"):
        enable_filters = st.checkbox("Enable filters", value=False)

        if enable_filters:
            companies = [
                "Barclays",
                "BP",
                "HSBC",
                "Lloyds Banking Group",
                "NatWest Group",
                "Shell",
                "Tesco",
                "Vodafone",
            ]

            company = st.selectbox(
                "Company",
                options=["Any"] + companies,
                index=0,
            )

            fiscal_year = st.number_input(
                "Fiscal Year",
                min_value=1900,
                max_value=2100,
                value=2024,
                step=1,
                help="Used only to filter documents, not to influence reasoning.",
            )

            top_k = st.slider(
                "Number of evidence chunks (top_k)",
                min_value=1,
                max_value=10,
                value=3,
            )

    submitted = st.form_submit_button("Submit")

if submitted:
    if not query:
        st.error("Please enter a query.")
    else:
        payload = {
            "query": query
        }

        if enable_filters:
            filters = {}
            if company != "Any":
                filters["company"] = company

            filters["fiscal_year"] = fiscal_year
            filters["top_k"] = top_k

            payload.update(filters)

        try:
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            response.raise_for_status()
            data = response.json()
            answer = data.get("answer", "")
            citations = data.get("evidence", [])

            st.subheader("Answer")
            st.write(answer)

            if citations:
                st.subheader("Sources")
                for i, c in enumerate(citations, start=1):
                    company = c.get("company", "Unknown company")
                    document = c.get("document", "Unknown document")
                    pages = c.get("pages", "N/A")
                    st.markdown(f"**[{i}] {company} — {document} (pp. {pages})**")

            if citations:
                st.subheader("Cited Evidence")
                query_terms = [term.lower() for term in query.split() if len(term) >= 3]
                for i, citation in enumerate(citations, 1):
                    with st.expander(f"Evidence {i}"):
                        st.write(f"**Company:** {citation.get('company', 'N/A')}")
                        st.write(f"**Document:** {citation.get('document', 'N/A')}")
                        pages = citation.get("pages")
                        if pages:
                            st.write(f"**Pages:** {pages}")
                        else:
                            st.write("**Pages:** N/A")
                        st.markdown(
                            f"<div style='white-space: pre-wrap; font-size: 0.9em'>{citation.get('text', '')}</div>",
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No cited evidence returned.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with API: {e}")
        except ValueError:
            st.error("Invalid response from API.")
