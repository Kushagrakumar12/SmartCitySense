"""
Statistics Routes
Endpoints for city-wide statistics and analytics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import structlog

from app.services.event_service import event_service
from app.models.event import EventFilter, EventStatus

router = APIRouter(prefix="/stats", tags=["Statistics"])
logger = structlog.get_logger()


@router.get("")
async def get_city_stats() -> Dict[str, Any]:
    """
    Get city-wide statistics
    
    Returns:
    - total_events: Total number of active events
    - active_alerts: Number of active alerts (high and critical severity)
    - average_sentiment: Average sentiment score across all events
    - resolved_issues: Number of resolved events
    - events_by_category: Breakdown by category
    - events_by_severity: Breakdown by severity
    """
    try:
        # Get ALL events without filtering (Firebase index not available for status filter)
        all_events = []
        page = 1
        while True:
            filters = EventFilter(
                page=page,
                page_size=100
            )
            response = await event_service.list_events(filters)
            events_page = response.get("events", [])
            if not events_page:
                break
            all_events.extend(events_page)
            if not response.get("has_more", False):
                break
            page += 1
        
        # Filter active events in memory
        # Convert Event objects to dicts
        active_events = []
        resolved_events = []
        for event in all_events:
            event_dict = event if isinstance(event, dict) else event.model_dump() if hasattr(event, 'model_dump') else dict(event)
            status = event_dict.get("status", "active")
            if status == "active":
                active_events.append(event_dict)
            elif status == "resolved":
                resolved_events.append(event_dict)
        
        total_events = len(active_events)
        
        # Count active alerts (high and critical severity)
        active_alerts = len([
            e for e in active_events 
            if e.get("severity") in ["high", "critical"]
        ])
        
        # Calculate average sentiment
        sentiments = [
            e.get("sentiment_score", 0) 
            for e in active_events 
            if e.get("sentiment_score") is not None
        ]
        average_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        resolved_issues = len(resolved_events)
        
        # Breakdown by category
        events_by_category = {}
        for event in active_events:
            category = event.get("category", "Other")
            events_by_category[category] = events_by_category.get(category, 0) + 1
        
        # Breakdown by severity
        events_by_severity = {}
        for event in active_events:
            severity = event.get("severity", "low")
            events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
        
        return {
            "total_events": total_events,
            "active_alerts": active_alerts,
            "average_sentiment": round(average_sentiment, 2),
            "resolved_issues": resolved_issues,
            "events_by_category": events_by_category,
            "events_by_severity": events_by_severity,
            "events_today": total_events,  # Simplified for now
            "trend_direction": "stable"
        }
        
    except Exception as e:
        logger.error("Error fetching city stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@router.get("/analytics")
async def get_analytics(
    metric: str = "events",
    period: str = "day"
) -> Dict[str, Any]:
    """
    Get analytics data for charts and visualizations
    
    Parameters:
    - metric: Type of metric (events, sentiment, alerts)
    - period: Time period (hour, day, week, month)
    """
    try:
        # Get all events (paginated)
        all_events = []
        page = 1
        while True:
            filters = EventFilter(
                page=page,
                page_size=100
            )
            response = await event_service.list_events(filters)
            events = response.get("events", [])
            if not events:
                break
            all_events.extend(events)
            if not response.get("has_more", False):
                break
            page += 1
        
        
        # Simple time series data (placeholder)
        # In production, this would query Firebase with time-based filtering
        time_series = []
        categories = {}
        
        for event in all_events:
            category = event.get("category", "Other")
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "metric": metric,
            "period": period,
            "total_count": len(all_events),
            "time_series": time_series,
            "categories": categories,
            "top_areas": []  # Placeholder
        }
        
    except Exception as e:
        logger.error("Error fetching analytics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics: {str(e)}"
        )
