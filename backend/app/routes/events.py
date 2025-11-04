"""
Event Routes
Endpoints for event management and querying
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from typing import Optional, Dict, Any

from app.models.event import (
    Event, EventCreate, EventUpdate, EventFilter,
    EventListResponse, EventResponse, EventCategory,
    EventSeverity, EventStatus
)
from app.models.common import SuccessResponse
from app.utils.auth_middleware import get_optional_user, get_current_user
from app.services.event_service import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=EventListResponse)
async def list_events(
    category: Optional[EventCategory] = None,
    severity: Optional[EventSeverity] = None,
    status: Optional[EventStatus] = None,
    area: Optional[str] = None,
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, ge=0, le=50),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    List events with optional filtering
    
    Supports filtering by:
    - Category (Traffic, Emergency, Civic Issue, etc.)
    - Severity (low, medium, high, critical)
    - Status (active, resolved, monitoring)
    - Area name
    - Geographic location (latitude, longitude, radius)
    - Pagination (page, page_size)
    """
    try:
        filters = EventFilter(
            category=category,
            severity=severity,
            status=status,
            area=area,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            page=page,
            page_size=page_size
        )
        
        result = await event_service.list_events(filters)
        
        return EventListResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get a specific event by ID
    
    Returns detailed information about a single event.
    """
    try:
        event = await event_service.get_event(event_id)
        
        if not event:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return EventResponse(event=event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event: {str(e)}"
        )


@router.post("", response_model=EventResponse, status_code=http_status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new event (authenticated users only)
    
    This endpoint is typically used by admin users or internal services
    to create events from data ingestion pipelines.
    """
    try:
        event = await event_service.create_event(
            event_data.model_dump(),
            user_id=current_user['uid']
        )
        
        return EventResponse(
            event=event,
            message="Event created successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    update_data: EventUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing event
    
    Allows updating event title, description, status, and severity.
    """
    try:
        event = await event_service.get_event(event_id)
        
        if not event:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        updated_event = await event_service.update_event(
            event_id,
            update_data.model_dump(exclude_unset=True)
        )
        
        return EventResponse(
            event=updated_event,
            message="Event updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )


@router.delete("/{event_id}", response_model=SuccessResponse)
async def delete_event(
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete an event
    
    Permanently removes an event from the system.
    """
    try:
        event = await event_service.get_event(event_id)
        
        if not event:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        await event_service.delete_event(event_id)
        
        return SuccessResponse(message="Event deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )


@router.post("/{event_id}/upvote", response_model=EventResponse)
async def upvote_event(
    event_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Upvote an event
    
    Increments the upvote counter for an event. This helps identify
    which events are most significant to users.
    """
    try:
        event = await event_service.upvote_event(event_id)
        
        return EventResponse(
            event=event,
            message="Event upvoted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upvote event: {str(e)}"
        )


@router.get("/category/{category}", response_model=EventListResponse)
async def get_events_by_category(
    category: EventCategory,
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get recent events by category
    
    Returns the most recent events in a specific category.
    """
    try:
        events = await event_service.get_events_by_category(category, limit)
        
        return EventListResponse(
            events=events,
            total=len(events),
            page=1,
            page_size=limit,
            has_more=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events by category: {str(e)}"
        )


@router.get("/area/{area}", response_model=EventListResponse)
async def get_events_by_area(
    area: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get recent events by area
    
    Returns the most recent events in a specific geographic area.
    """
    try:
        events = await event_service.get_events_by_area(area, limit)
        
        return EventListResponse(
            events=events,
            total=len(events),
            page=1,
            page_size=limit,
            has_more=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events by area: {str(e)}"
        )
