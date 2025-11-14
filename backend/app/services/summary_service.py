"""
Summary Service
Business logic for AI-generated event summaries
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from app.utils.firebase_client import firebase_client
from app.models.summary import Summary, SummaryFilter, SummaryCreate
from app.services.ai_client import ai_ml_client
from app.services.event_service import event_service

logger = structlog.get_logger()


class SummaryService:
    """Service for summary-related operations"""
    
    def __init__(self):
        self.collection = "summaries"
        self.db = firebase_client.get_db()
    
    async def create_summary(self, request: SummaryCreate) -> Summary:
        """
        Create a summary from multiple events
        
        Args:
            request: Summary creation request
            
        Returns:
            Created summary
        """
        try:
            # Get events
            events = []
            for event_id in request.event_ids:
                event = await event_service.get_event(event_id)
                if event:
                    events.append(event.model_dump())
            
            if len(events) < 2:
                raise ValueError("At least 2 events required for summarization")
            
            # Call AI summarization service
            summary_result = await ai_ml_client.summarize_events(events)
            
            if not summary_result.get('success'):
                raise ValueError("Summarization failed")
            
            # Extract summary data
            summary_data = {
                'title': summary_result.get('title', 'Event Summary'),
                'summary_text': summary_result.get('summary', ''),
                'category': request.category.value if request.category else events[0].get('category'),
                'source_event_ids': request.event_ids,
                'event_count': len(events),
                'created_at': datetime.utcnow(),
                'area': request.area or events[0].get('location', {}).get('area'),
                'sentiment_score': summary_result.get('sentiment_score'),
                'key_points': summary_result.get('key_points', []),
                'recommendations': summary_result.get('recommendations', []),
                'timeframe': summary_result.get('timeframe', 'recent')
            }
            
            # Add location if available
            if events[0].get('location'):
                summary_data['location'] = events[0]['location']
            
            # Add to Firestore
            summary_id = firebase_client.add_document(self.collection, summary_data)
            
            # Retrieve created summary
            summary_doc = firebase_client.get_document(self.collection, summary_id)
            logger.info(f"Created summary {summary_id} from {len(events)} events")
            
            return Summary(**summary_doc)
            
        except Exception as e:
            logger.error(f"Failed to create summary: {str(e)}")
            raise
    
    async def auto_summarize_by_category(self, category: str, hours: int = 2) -> Optional[Summary]:
        """
        Automatically create summary for events in a category
        
        Args:
            category: Event category
            hours: Time window in hours
            
        Returns:
            Created summary or None if not enough events
        """
        try:
            # Get recent events in category
            from app.models.event import EventCategory
            events = await event_service.get_events_by_category(
                EventCategory(category),
                limit=20
            )
            
            if len(events) < 2:
                logger.info(f"Not enough events in {category} for summarization")
                return None
            
            # Create summary request
            request = SummaryCreate(
                event_ids=[event.id for event in events if event.id],
                category=EventCategory(category)
            )
            
            summary = await self.create_summary(request)
            return summary
            
        except Exception as e:
            logger.error(f"Failed to auto-summarize by category: {str(e)}")
            return None
    
    async def auto_summarize_by_area(self, area: str, hours: int = 2) -> Optional[Summary]:
        """
        Automatically create summary for events in an area
        
        Args:
            area: Geographic area
            hours: Time window in hours
            
        Returns:
            Created summary or None if not enough events
        """
        try:
            # Get recent events in area
            events = await event_service.get_events_by_area(area, limit=20)
            
            if len(events) < 2:
                logger.info(f"Not enough events in {area} for summarization")
                return None
            
            # Create summary request
            request = SummaryCreate(
                event_ids=[event.id for event in events if event.id],
                area=area
            )
            
            summary = await self.create_summary(request)
            return summary
            
        except Exception as e:
            logger.error(f"Failed to auto-summarize by area: {str(e)}")
            return None
    
    async def get_summary(self, summary_id: str) -> Optional[Summary]:
        """Get summary by ID"""
        try:
            summary_data = firebase_client.get_document(self.collection, summary_id)
            if summary_data:
                return Summary(**summary_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get summary {summary_id}: {str(e)}")
            raise
    
    async def list_summaries(self, filters: SummaryFilter) -> Dict[str, Any]:
        """
        List summaries with filtering
        
        Args:
            filters: Summary filters
            
        Returns:
            Dictionary with summaries and pagination info
        """
        try:
            query_filters = []
            
            if filters.category:
                query_filters.append(('category', '==', filters.category.value))
            
            if filters.area:
                query_filters.append(('area', '==', filters.area))
            
            if filters.start_date:
                query_filters.append(('created_at', '>=', filters.start_date))
            
            if filters.end_date:
                query_filters.append(('created_at', '<=', filters.end_date))
            
            offset = (filters.page - 1) * filters.page_size
            
            summaries = firebase_client.query_documents(
                collection=self.collection,
                filters=query_filters if query_filters else None,
                order_by='created_at',
                limit=filters.page_size,
                offset=offset
            )
            
            total = firebase_client.get_collection_count(
                self.collection,
                query_filters if query_filters else None
            )
            
            summary_models = [Summary(**summary) for summary in summaries]
            
            return {
                "summaries": summary_models,
                "total": total,
                "page": filters.page,
                "page_size": filters.page_size
            }
            
        except Exception as e:
            logger.error(f"Failed to list summaries: {str(e)}")
            raise


# Singleton instance
summary_service = SummaryService()


def get_summary_service() -> SummaryService:
    """Get summary service instance"""
    return summary_service
