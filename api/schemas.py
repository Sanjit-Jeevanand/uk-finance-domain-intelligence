from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str = Field(..., description="User question")
    company: Optional[str] = Field(None, description="Company filter")
    fiscal_year: Optional[int] = Field(None, description="Fiscal year filter")
    top_k: int = Field(5, ge=1, le=20)


class EvidenceBlock(BaseModel):
    source_id: int
    company: str
    document: str
    pages: str
    text: str


class QueryResponse(BaseModel):
    answer: str
    evidence: List[EvidenceBlock]