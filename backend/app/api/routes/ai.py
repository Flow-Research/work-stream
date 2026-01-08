from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession
from app.core.rate_limit import limiter, RATE_LIMIT_AI
from app.services.ai import AIService
from app.services.papers import PaperService

router = APIRouter()


class DecomposeTaskRequest(BaseModel):
    """Request schema for task decomposition."""
    
    research_question: str = Field(..., min_length=10)
    budget: float = Field(..., gt=0)
    context: Optional[str] = None


class ProposedSubtask(BaseModel):
    """Schema for a proposed subtask."""
    
    title: str
    description: str
    subtask_type: str
    sequence_order: int
    budget_allocation_percent: float


class DecomposeTaskResponse(BaseModel):
    """Response schema for task decomposition."""
    
    subtasks: list[ProposedSubtask]


class DiscoverPapersRequest(BaseModel):
    """Request schema for paper discovery."""
    
    query: str = Field(..., min_length=3)
    limit: int = Field(default=20, ge=1, le=100)


class Paper(BaseModel):
    """Schema for a paper."""
    
    id: str
    title: str
    authors: list[str]
    year: Optional[int]
    abstract: Optional[str]
    venue: Optional[str]
    url: Optional[str]
    source: str


class DiscoverPapersResponse(BaseModel):
    """Response schema for paper discovery."""
    
    papers: list[Paper]


class ExtractClaimsRequest(BaseModel):
    """Request schema for claim extraction."""
    
    paper_id: str
    paper_text: str


class Claim(BaseModel):
    """Schema for an extracted claim."""
    
    id: str
    statement: str
    claim_type: str
    confidence: str
    source_quote: Optional[str]


class ExtractClaimsResponse(BaseModel):
    """Response schema for claim extraction."""
    
    claims: list[Claim]


class SynthesizeRequest(BaseModel):
    """Request schema for synthesis."""
    
    claims: list[Claim]
    format: str = Field(default="summary", pattern=r"^(summary|structured)$")


class SynthesizeResponse(BaseModel):
    """Response schema for synthesis."""
    
    synthesis: str


@router.post("/decompose-task", response_model=DecomposeTaskResponse)
@limiter.limit(RATE_LIMIT_AI)
async def decompose_task(
    request: Request,
    body: DecomposeTaskRequest,
    current_user: CurrentUser,
) -> DecomposeTaskResponse:
    ai_service = AIService()
    
    try:
        subtasks = await ai_service.decompose_task(
            research_question=body.research_question,
            budget=body.budget,
            context=body.context,
        )
        return DecomposeTaskResponse(subtasks=subtasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/discover-papers", response_model=DiscoverPapersResponse)
@limiter.limit(RATE_LIMIT_AI)
async def discover_papers(
    request: Request,
    body: DiscoverPapersRequest,
    current_user: CurrentUser,
) -> DiscoverPapersResponse:
    paper_service = PaperService()
    
    try:
        papers = await paper_service.search_papers(
            query=body.query,
            limit=body.limit,
        )
        return DiscoverPapersResponse(papers=papers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Paper service error: {str(e)}",
        )


@router.post("/extract-claims", response_model=ExtractClaimsResponse)
@limiter.limit(RATE_LIMIT_AI)
async def extract_claims(
    request: Request,
    body: ExtractClaimsRequest,
    current_user: CurrentUser,
) -> ExtractClaimsResponse:
    ai_service = AIService()
    
    try:
        claims = await ai_service.extract_claims(
            paper_id=body.paper_id,
            paper_text=body.paper_text,
        )
        return ExtractClaimsResponse(claims=claims)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/synthesize", response_model=SynthesizeResponse)
@limiter.limit(RATE_LIMIT_AI)
async def synthesize_claims(
    request: Request,
    body: SynthesizeRequest,
    current_user: CurrentUser,
) -> SynthesizeResponse:
    ai_service = AIService()
    
    try:
        synthesis = await ai_service.synthesize(
            claims=body.claims,
            format=body.format,
        )
        return SynthesizeResponse(synthesis=synthesis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )
