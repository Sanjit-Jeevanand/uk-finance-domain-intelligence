from fastapi import APIRouter
from api.schemas import QueryRequest, QueryResponse, EvidenceBlock
from api.services.rag_service import RAGService
from api.services.llm_service import LLMService

router = APIRouter()
rag_service = RAGService()
llm_service = LLMService()

# in api/main.py

@router.get("/")
def root():
    return {
        "service": "finance-dis",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):

    filters = {}

    if request.company:
        filters["company"] = request.company

    if request.fiscal_year:
        filters["fiscal_year"] = request.fiscal_year

    filters["report_type"] = "annual_report"

    result = rag_service.retrieve(
        query=request.query,
        filters=filters,
        top_k=request.top_k,
    )

    if not result["raw_chunks"] or not result["evidence_context"]:
        answer = "I do not have enough information in the provided documents."
    else:
        # Generate answer
        answer = llm_service.answer(
            question=request.query,
            evidence_context=result["evidence_context"],
        )

    # 🔹 Build evidence blocks
    evidence = []
    for i, c in enumerate(result["raw_chunks"], start=1):
        evidence.append(
            EvidenceBlock(
                source_id=i,
                company=c["company"],
                document=f"{c['report_type']} {c['fiscal_year']}",
                pages=f"{c['page_start']}–{c['page_end']}",
                text=c["text"],
            )
        )

    return QueryResponse(
        answer=answer,
        evidence=evidence,
    )