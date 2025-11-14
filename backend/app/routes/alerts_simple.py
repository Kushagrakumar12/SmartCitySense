"""
Simple Alerts Endpoint
Returns high-severity events as alerts without requiring Firebase indexes
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Any
import structlog

from app.services.event_service import event_service
from app.models.event import EventFilter, EventSeverity

router = APIRouter(prefix="/alerts", tags=["Alerts"])  # Use /alerts prefix
logger = structlog.get_logger()


@router.get("")
async def get_alerts_from_events(
    active: bool = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Get alerts from high and critical severity events
    
    This avoids Firebase index requirements by fetching all events
    and filtering in memory.
    """
    try:
        # Get all events
        all_events = []
        fetch_page = 1
        while True:
            filters = EventFilter(
                page=fetch_page,
                page_size=100
            )
            response = await event_service.list_events(filters)
            events_page = response.get("events", [])
            if not events_page:
                break
            all_events.extend(events_page)
            if not response.get("has_more", False) or len(all_events) >= 500:  # Limit to 500
                break
            fetch_page += 1
        
        # Convert Event objects to dicts and filter for alerts
        alerts = []
        for event in all_events:
            event_dict = event if isinstance(event, dict) else event.model_dump() if hasattr(event, 'model_dump') else dict(event)
            
            # Only include high and critical severity as alerts
            severity = event_dict.get("severity", "").lower()
            status = event_dict.get("status", "active")
            
            if severity in ["high", "critical"]:
                if not active or status == "active":
                    # Transform to alert format
                    alert = {
                        "id": event_dict.get("id"),
                        "title": event_dict.get("title", event_dict.get("description", ""))[:100],
                        "description": event_dict.get("description", ""),
                        "severity": severity,
                        "category": event_dict.get("category", "Other"),
                        "location": event_dict.get("location", {}),
                        "timestamp": event_dict.get("timestamp"),
                        "status": status,
                        "source": event_dict.get("source", "system"),
                        "alert_type": "event_based"
                    }
                    alerts.append(alert)
        
        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_alerts = alerts[start_idx:end_idx]
        
        return {
            "success": True,
            "alerts": paginated_alerts,
            "total": len(alerts),
            "page": page,
            "page_size": page_size,
            "has_more": end_idx < len(alerts)
        }
        
    except Exception as e:
        logger.error("Error fetching alerts from events", error=str(e))
        return {
            "success": False,
            "alerts": [],
            "total": 0,
            "error": str(e)
        }
