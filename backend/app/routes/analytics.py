"""
Analytics Routes
Endpoints for city analytics and insights
"""

from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.services.event_service import event_service
from app.models.event import EventFilter

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = structlog.get_logger()


@router.get("")
async def get_analytics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    """
    Get city analytics and insights
    
    Returns:
    - City health score
    - Event volume over time
    - Category distribution
    - Sentiment trends
    - Severity analysis
    """
    try:
        # Fetch all events (with pagination)
        all_events = []
        page = 1
        
        while True:
            result = await event_service.list_events(
                EventFilter(
                    page=page,
                    page_size=100,
                    start_time=start_date,
                    end_time=end_date
                )
            )
            
            events_list = result.get('events', [])
            if not events_list:
                break
                
            # Convert Event objects to dicts
            for event in events_list:
                if hasattr(event, 'model_dump'):
                    all_events.append(event.model_dump())
                else:
                    all_events.append(event)
            
            # Check if there are more pages
            if len(events_list) < 100:
                break
            page += 1
        
        total_events = len(all_events)
        
        # Calculate city health score (higher is better)
        # Based on: low severity events, resolved issues, positive sentiment
        critical_count = sum(1 for e in all_events if e.get('severity') == 'critical')
        high_count = sum(1 for e in all_events if e.get('severity') == 'high')
        resolved_count = sum(1 for e in all_events if e.get('status') == 'resolved')
        
        # Health score: penalize critical/high severity, reward resolutions
        if total_events > 0:
            severity_penalty = (critical_count * 2 + high_count) / total_events
            resolution_bonus = resolved_count / total_events if resolved_count > 0 else 0
            city_health_score = max(0, min(1, 0.8 - severity_penalty + resolution_bonus * 0.3))
        else:
            city_health_score = 1.0
        
        # Event volume over time (group by day)
        event_volume = {}
        for event in all_events:
            timestamp = event.get('timestamp', '')
            if timestamp:
                # Convert timestamp to string if it's not already
                if not isinstance(timestamp, str):
                    timestamp = str(timestamp)
                # Extract date (YYYY-MM-DD)
                date = timestamp.split('T')[0] if 'T' in timestamp else timestamp[:10]
                event_volume[date] = event_volume.get(date, 0) + 1
        
        # Convert to list format for charts
        event_volume_list = [
            {"timestamp": date, "value": count}
            for date, count in sorted(event_volume.items())
        ]
        
        # Category distribution
        category_counts: Dict[str, int] = {}
        for event in all_events:
            category = event.get('category', 'Other')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        category_distribution = [
            {"category": cat, "count": count}
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Sentiment trends (average sentiment over time)
        sentiment_by_date: Dict[str, List[float]] = {}
        for event in all_events:
            if event.get('sentiment_score') is not None:
                timestamp = event.get('timestamp', '')
                if timestamp:
                    # Convert timestamp to string if it's not already
                    if not isinstance(timestamp, str):
                        timestamp = str(timestamp)
                    date = timestamp.split('T')[0] if 'T' in timestamp else timestamp[:10]
                    if date not in sentiment_by_date:
                        sentiment_by_date[date] = []
                    sentiment_by_date[date].append(event['sentiment_score'])
        
        sentiment_trends = [
            {
                "timestamp": date,
                "value": sum(scores) / len(scores) if scores else 0
            }
            for date, scores in sorted(sentiment_by_date.items())
        ]
        
        # Severity analysis
        severity_counts = {
            'low': sum(1 for e in all_events if e.get('severity') == 'low'),
            'medium': sum(1 for e in all_events if e.get('severity') == 'medium'),
            'high': sum(1 for e in all_events if e.get('severity') == 'high'),
            'critical': sum(1 for e in all_events if e.get('severity') == 'critical'),
        }
        
        severity_analysis = [
            {"severity": sev, "count": count}
            for sev, count in severity_counts.items()
        ]
        
        return {
            "city_health_score": round(city_health_score, 2),
            "event_volume": event_volume_list,
            "category_distribution": category_distribution,
            "sentiment_trends": sentiment_trends,
            "severity_analysis": severity_analysis,
            "total_events_analyzed": total_events,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
        
    except Exception as e:
        logger.error("Error fetching analytics", error=str(e))
        return {
            "city_health_score": 0.5,
            "event_volume": [],
            "category_distribution": [],
            "sentiment_trends": [],
            "severity_analysis": [],
            "total_events_analyzed": 0,
            "error": "Unable to fetch analytics data"
        }
