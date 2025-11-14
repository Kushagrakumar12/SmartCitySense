"""
Summary Routes
Endpoints for AI-generated event summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any

from app.models.summary import (
    Summary, SummaryCreate, SummaryFilter,
    SummaryResponse, SummaryListResponse
)
from app.models.event import EventCategory
from app.utils.auth_middleware import get_optional_user, get_current_user
from app.services.summary_service import summary_service

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.get("", response_model=SummaryListResponse)
async def list_summaries(
    category: Optional[EventCategory] = None,
    area: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    List AI-generated summaries
    
    Returns summaries of clustered events. Each summary synthesizes
    multiple related events into a single coherent narrative with
    actionable recommendations.
    
    Filter options:
    - category: Event category
    - area: Geographic area
    """
    try:
        filters = SummaryFilter(
            category=category,
            area=area,
            page=page,
            page_size=page_size
        )
        
        result = await summary_service.list_summaries(filters)
        
        return SummaryListResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list summaries: {str(e)}"
        )


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get a specific summary by ID
    
    Returns detailed information about a single summary including
    key points, recommendations, and source events.
    """
    try:
        summary = await summary_service.get_summary(summary_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        return SummaryResponse(summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.post("", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_summary(
    request: SummaryCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new summary from events
    
    Generates an AI summary from multiple events. This endpoint:
    1. Fetches the specified events
    2. Sends them to the AI/ML summarization service
    3. Creates a structured summary with key points and recommendations
    
    Example use case:
    "15 reports about traffic on Old Airport Road" → "Heavy traffic on Old
    Airport Road due to accident near HAL. Average delay 30 minutes. Use
    Marathahalli route as alternative."
    """
    try:
        if len(request.event_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 events required for summarization"
            )
        
        summary = await summary_service.create_summary(request)
        
        return SummaryResponse(
            summary=summary,
            message="Summary generated successfully"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )


@router.post("/auto/category/{category}", response_model=SummaryResponse)
async def auto_summarize_category(
    category: EventCategory,
    hours: int = Query(2, ge=1, le=24, description="Time window in hours"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Auto-generate summary for a category
    
    Automatically creates a summary from recent events in a specific category.
    This is useful for generating periodic summaries like:
    - "Traffic updates for the last 2 hours"
    - "Emergency alerts today"
    """
    try:
        summary = await summary_service.auto_summarize_by_category(
            category.value,
            hours=hours
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Not enough events in {category.value} for summarization"
            )
        
        return SummaryResponse(
            summary=summary,
            message="Summary generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-summarize category: {str(e)}"
        )


@router.post("/auto/area/{area}", response_model=SummaryResponse)
async def auto_summarize_area(
    area: str,
    hours: int = Query(2, ge=1, le=24, description="Time window in hours"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Auto-generate summary for an area
    
    Automatically creates a summary from recent events in a specific geographic area.
    This is useful for generating location-based summaries like:
    - "What's happening in Koramangala?"
    - "Events in Indiranagar today"
    """
    try:
        summary = await summary_service.auto_summarize_by_area(
            area,
            hours=hours
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Not enough events in {area} for summarization"
            )
        
        return SummaryResponse(
            summary=summary,
            message="Summary generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-summarize area: {str(e)}"
        )
