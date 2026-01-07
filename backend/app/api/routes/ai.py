"""AI assistance endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession
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
async def decompose_task(
    request: DecomposeTaskRequest,
    current_user: CurrentUser,
) -> DecomposeTaskResponse:
    """
    Use AI to decompose a research question into subtasks.
    
    Args:
        request: The decomposition request
        current_user: The authenticated user
        
    Returns:
        List of proposed subtasks
    """
    ai_service = AIService()
    
    try:
        subtasks = await ai_service.decompose_task(
            research_question=request.research_question,
            budget=request.budget,
            context=request.context,
        )
        return DecomposeTaskResponse(subtasks=subtasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/discover-papers", response_model=DiscoverPapersResponse)
async def discover_papers(
    request: DiscoverPapersRequest,
    current_user: CurrentUser,
) -> DiscoverPapersResponse:
    """
    Discover papers relevant to a research query.
    
    Args:
        request: The discovery request
        current_user: The authenticated user
        
    Returns:
        List of discovered papers
    """
    paper_service = PaperService()
    
    try:
        papers = await paper_service.search_papers(
            query=request.query,
            limit=request.limit,
        )
        return DiscoverPapersResponse(papers=papers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Paper service error: {str(e)}",
        )


@router.post("/extract-claims", response_model=ExtractClaimsResponse)
async def extract_claims(
    request: ExtractClaimsRequest,
    current_user: CurrentUser,
) -> ExtractClaimsResponse:
    """
    Extract claims from paper text using AI.
    
    Args:
        request: The extraction request
        current_user: The authenticated user
        
    Returns:
        List of extracted claims
    """
    ai_service = AIService()
    
    try:
        claims = await ai_service.extract_claims(
            paper_id=request.paper_id,
            paper_text=request.paper_text,
        )
        return ExtractClaimsResponse(claims=claims)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_claims(
    request: SynthesizeRequest,
    current_user: CurrentUser,
) -> SynthesizeResponse:
    """
    Synthesize claims into a coherent summary.
    
    Args:
        request: The synthesis request
        current_user: The authenticated user
        
    Returns:
        Synthesized content
    """
    ai_service = AIService()
    
    try:
        synthesis = await ai_service.synthesize(
            claims=request.claims,
            format=request.format,
        )
        return SynthesizeResponse(synthesis=synthesis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )
