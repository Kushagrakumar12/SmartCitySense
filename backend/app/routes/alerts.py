"""
Alert Routes
Endpoints for predictive alerts and anomaly detection
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any

from app.models.alert import (
    Alert, AlertCreate, AlertFilter, AlertResponse, AlertListResponse,
    AlertType, AlertPriority
)
from app.models.common import SuccessResponse
from app.models.event import EventCategory
from app.utils.auth_middleware import get_optional_user, get_current_user
from app.services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    alert_type: Optional[AlertType] = None,
    priority: Optional[AlertPriority] = None,
    category: Optional[EventCategory] = None,
    area: Optional[str] = None,
    is_active: Optional[bool] = None,  # Changed from True to None to avoid index requirement
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    List alerts with filtering
    
    Returns predictive alerts and anomaly detections.
    
    Filter options:
    - alert_type: predictive, anomaly, emergency, trend
    - priority: low, medium, high, urgent
    - category: Event category
    - area: Geographic area
    - is_active: Only active alerts (default: None for no filtering)
    """
    try:
        filters = AlertFilter(
            alert_type=alert_type,
            priority=priority,
            category=category,
            area=area,
            is_active=is_active if is_active is not None else None,  # Don't filter if not specified
            page=page,
            page_size=page_size
        )
        
        result = await alert_service.list_alerts(filters)
        
        return AlertListResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list alerts: {str(e)}"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get a specific alert by ID
    
    Returns detailed information about a single alert.
    """
    try:
        alert = await alert_service.get_alert(alert_id)
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return AlertResponse(alert=alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alert: {str(e)}"
        )


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new alert (admin/system only)
    
    This endpoint is typically used by the predictive system or admin users
    to create alerts based on anomaly detection or trend analysis.
    """
    try:
        alert = await alert_service.create_alert(alert_data.model_dump())
        
        return AlertResponse(
            alert=alert,
            message="Alert created and notifications sent"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )


@router.post("/detect-anomalies", response_model=AlertListResponse)
async def detect_anomalies(
    time_window: str = Query("1h", description="Time window for analysis (e.g., 1h, 6h, 24h)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Trigger anomaly detection
    
    Analyzes recent events to detect unusual patterns and creates alerts.
    This endpoint can be called manually or scheduled to run periodically.
    
    Example patterns detected:
    - Multiple outage reports in same area → likely grid issue
    - Sudden spike in traffic reports → major accident or event
    - Unusual cluster of civic complaints → infrastructure problem
    """
    try:
        alerts = await alert_service.detect_anomalies(time_window)
        
        return AlertListResponse(
            alerts=alerts,
            total=len(alerts),
            has_more=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect anomalies: {str(e)}"
        )


@router.put("/{alert_id}/deactivate", response_model=AlertResponse)
async def deactivate_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Deactivate an alert
    
    Marks an alert as inactive. It will no longer appear in active alert lists.
    """
    try:
        alert = await alert_service.deactivate_alert(alert_id)
        
        return AlertResponse(
            alert=alert,
            message="Alert deactivated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate alert: {str(e)}"
        )


@router.get("/area/{area}", response_model=AlertListResponse)
async def get_alerts_for_area(
    area: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Get active alerts for a specific area
    
    Returns all active alerts affecting a particular geographic area.
    """
    try:
        alerts = await alert_service.get_active_alerts_for_area(area)
        
        return AlertListResponse(
            alerts=alerts,
            total=len(alerts),
            has_more=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts for area: {str(e)}"
        )
