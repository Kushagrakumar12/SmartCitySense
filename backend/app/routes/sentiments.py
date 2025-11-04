"""
Sentiment Routes
Endpoints for sentiment analysis data
"""

from fastapi import APIRouter, Query
from typing import Optional, List, Dict
from datetime import datetime
import structlog

from app.services.event_service import event_service
from app.models.event import EventFilter

router = APIRouter(prefix="/sentiments", tags=["Sentiments"])
logger = structlog.get_logger()


@router.get("")
async def get_sentiments(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results")
):
    """
    Get sentiment data from events
    
    Returns sentiment scores over time for mood mapping and analysis
    If events don't have sentiment_score, generates approximate scores based on category and severity
    """
    try:
        # Fetch events
        all_events = []
        page = 1
        
        while len(all_events) < limit:
            result = await event_service.list_events(
                EventFilter(
                    page=page,
                    page_size=min(100, limit - len(all_events)),
                    start_time=start_time,
                    end_time=end_time
                )
            )
            
            events_list = result.get('events', [])
            if not events_list:
                break
            
            # Convert Event objects to dicts
            for event in events_list:
                if hasattr(event, 'model_dump'):
                    event_dict = event.model_dump()
                else:
                    event_dict = event
                
                all_events.append(event_dict)
            
            # Check if there are more pages
            if len(events_list) < 100:
                break
            page += 1
        
        # Format sentiment data with fallback sentiment calculation
        sentiments = []
        for event in all_events[:limit]:
            # Get or generate sentiment score
            sentiment_score = event.get('sentiment_score')
            
            if sentiment_score is None:
                # Generate approximate sentiment based on category and severity
                category = event.get('category', 'Other')
                severity = event.get('severity', 'medium')
                
                # Base sentiment by category
                category_sentiments = {
                    'Emergency': 0.2,
                    'Traffic': 0.35,
                    'Civic Issue': 0.4,
                    'Weather': 0.45,
                    'Power Outage': 0.3,
                    'Water Supply': 0.3,
                    'Protest': 0.35,
                    'Construction': 0.45,
                    'Cultural': 0.7,
                    'Other': 0.5
                }
                
                base_sentiment = category_sentiments.get(category, 0.5)
                
                # Adjust by severity
                severity_adjustments = {
                    'critical': -0.2,
                    'high': -0.1,
                    'medium': 0.0,
                    'low': 0.1
                }
                
                sentiment_score = max(0.0, min(1.0, base_sentiment + severity_adjustments.get(severity, 0.0)))
            
            # Determine sentiment label
            if sentiment_score > 0.6:
                sentiment_label = 'positive'
            elif sentiment_score < 0.4:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            sentiments.append({
                "id": event.get('id'),
                "timestamp": event.get('timestamp'),
                "location": event.get('location', {}),
                "sentiment_score": round(sentiment_score, 3),
                "sentiment_label": sentiment_label,
                "category": event.get('category', 'Other'),
                "title": event.get('title', ''),
            })
        
        # Calculate aggregate statistics
        if sentiments:
            scores = [s['sentiment_score'] for s in sentiments]
            avg_sentiment = sum(scores) / len(scores)
            positive_count = sum(1 for s in scores if s > 0.6)
            negative_count = sum(1 for s in scores if s < 0.4)
            neutral_count = len(scores) - positive_count - negative_count
        else:
            avg_sentiment = 0.5
            positive_count = 0
            negative_count = 0
            neutral_count = 0
        
        return {
            "sentiments": sentiments,
            "total": len(sentiments),
            "statistics": {
                "average_sentiment": round(avg_sentiment, 3),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count
            }
        }
        
    except Exception as e:
        logger.error("Error fetching sentiments", error=str(e))
        return {
            "sentiments": [],
            "total": 0,
            "statistics": {
                "average_sentiment": 0.5,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            },
            "error": str(e)
        }
