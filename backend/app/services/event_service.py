"""
Event Service
Business logic for event management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from app.utils.firebase_client import firebase_client
from app.utils.geo_utils import filter_by_location
from app.models.event import Event, EventFilter, EventStatus, EventCategory
from app.services.ai_client import ai_ml_client

logger = structlog.get_logger()


class EventService:
    """Service for event-related operations"""
    
    def __init__(self):
        # Use processed_events collection (data comes from data-processing pipeline)
        self.collection = "processed_events"
        self.db = firebase_client.get_db()
    
    def _transform_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform processed event data to backend Event schema
        
        Maps from data-processing schema to backend API schema
        """
        try:
            # Map the schema
            transformed = {
                'id': event_data.get('id') or event_data.get('event_id'),
                'title': event_data.get('description', '')[:200],  # Use description as title
                'description': event_data.get('description', ''),
                'source': event_data.get('source', 'unknown'),
                'timestamp': event_data.get('timestamp'),
                'status': 'active',  # Default status
                'tags': event_data.get('tags', []),
                'upvotes': 0,
                'report_count': 1,
                'media_urls': []
            }
            
            # Map category (type -> category)
            type_to_category_map = {
                'traffic': 'Traffic',
                'civic': 'Civic Issue',
                'emergency': 'Emergency',
                'weather': 'Weather',
                'cultural': 'Cultural',
                'other': 'Other'
            }
            event_type = event_data.get('type', 'other').lower()
            transformed['category'] = type_to_category_map.get(event_type, 'Other')
            
            # Map severity
            severity = event_data.get('severity', 'medium').lower()
            transformed['severity'] = severity if severity in ['low', 'medium', 'high', 'critical'] else 'medium'
            
            # Map location
            coordinates = event_data.get('coordinates', {})
            location_str = event_data.get('location', '')
            
            transformed['location'] = {
                'latitude': coordinates.get('lat', coordinates.get('latitude', 12.9716)),
                'longitude': coordinates.get('lon', coordinates.get('longitude', 77.5946)),
                'address': location_str,
                'area': event_data.get('zone', ''),
                'city': 'Bengaluru'
            }
            
            # Include sentiment data if available
            if 'sentiment_score' in event_data:
                transformed['sentiment_score'] = event_data['sentiment_score']
            if 'sentiment' in event_data:
                transformed['sentiment'] = event_data['sentiment']
            
            return transformed
        except Exception as e:
            logger.error(f"Failed to transform event data: {str(e)}")
            raise
    
    async def create_event(self, event_data: Dict[str, Any], user_id: Optional[str] = None) -> Event:
        """
        Create a new event
        
        Args:
            event_data: Event data dictionary
            user_id: Optional user ID if user-submitted
            
        Returns:
            Created event
        """
        try:
            # Add metadata
            event_data['reported_by'] = user_id
            event_data['timestamp'] = datetime.utcnow()
            event_data['status'] = EventStatus.ACTIVE.value
            
            # Analyze sentiment if description provided
            if 'description' in event_data:
                sentiment_result = await ai_ml_client.analyze_sentiment(event_data['description'])
                if sentiment_result.get('success'):
                    event_data['sentiment_score'] = sentiment_result.get('score', 0)
            
            # Add to Firestore
            event_id = firebase_client.add_document(self.collection, event_data)
            
            # Retrieve created event
            event = firebase_client.get_document(self.collection, event_id)
            logger.info(f"Created event {event_id}")
            
            return Event(**event)
            
        except Exception as e:
            logger.error(f"Failed to create event: {str(e)}")
            raise
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        try:
            event_data = firebase_client.get_document(self.collection, event_id)
            if event_data:
                transformed = self._transform_event_data(event_data)
                return Event(**transformed)
            return None
        except Exception as e:
            logger.error(f"Failed to get event {event_id}: {str(e)}")
            raise
    
    async def list_events(self, filters: EventFilter) -> Dict[str, Any]:
        """
        List events with filtering and pagination
        
        Args:
            filters: Event filters
            
        Returns:
            Dictionary with events, total count, and pagination info
        """
        try:
            # Build Firestore query filters
            query_filters = []
            
            if filters.category:
                # Note: Firestore documents use 'type' field with lowercase values
                # Map API category names to Firestore type values
                category_map = {
                    "Traffic": "traffic",
                    "Emergency": "emergency",
                    "Civic Issue": "civic",
                    "Cultural": "cultural",
                    "Weather": "weather",
                    "Power Outage": "power_outage",
                    "Water Supply": "water",
                    "Protest": "protest",
                    "Construction": "construction",
                    "Other": "other"
                }
                firestore_type = category_map.get(filters.category.value, filters.category.value.lower())
                query_filters.append(('type', '==', firestore_type))
            
            if filters.severity:
                query_filters.append(('severity', '==', filters.severity.value))
            
            if filters.status:
                query_filters.append(('status', '==', filters.status.value))
            
            if filters.area:
                query_filters.append(('location.area', '==', filters.area))
            
            # Date filtering
            if filters.start_date:
                query_filters.append(('timestamp', '>=', filters.start_date))
            
            if filters.end_date:
                query_filters.append(('timestamp', '<=', filters.end_date))
            
            # Calculate offset
            offset = (filters.page - 1) * filters.page_size
            
            # Firebase composite index limitation workaround:
            # Fetch ALL events and filter/sort in Python
            if len(query_filters) > 0:
                # Fetch all events without filters (to avoid index issues)
                all_events = firebase_client.query_documents(
                    collection=self.collection,
                    filters=None,
                    order_by=None,
                    limit=1000,
                    offset=None
                )
                
                # Debug: inspect first event structure (can be removed in production)
                # if all_events:
                #     sample_event = all_events[0]
                #     logger.info(f"Sample event keys: {list(sample_event.keys())}")
                
                # Apply filters in Python
                events = all_events
                for field, operator, value in query_filters:
                    if operator == '==':
                        if '.' in field:  # Nested field like 'location.area'
                            parts = field.split('.')
                            events = [e for e in events if e.get(parts[0], {}).get(parts[1]) == value]
                        else:
                            events = [e for e in events if e.get(field) == value]
                    elif operator == '>=':
                        events = [e for e in events if e.get(field, '') >= value]
                    elif operator == '<=':
                        events = [e for e in events if e.get(field, '') <= value]
                
                logger.info(f"Filtered to {len(events)} events matching criteria")
                
                # Sort by timestamp (descending)
                events = sorted(events, key=lambda e: e.get('timestamp', ''), reverse=True)
                
                # Apply pagination
                start_idx = offset
                end_idx = offset + filters.page_size + 1
                events = events[start_idx:end_idx]
            else:
                # No filters - use Firestore ordering and pagination
                events = firebase_client.query_documents(
                    collection=self.collection,
                    filters=None,
                    order_by='timestamp',
                    limit=filters.page_size + 1,
                    offset=offset
                )
            
            # Check if there are more pages
            has_more = len(events) > filters.page_size
            if has_more:
                events = events[:-1]  # Remove the extra event
            
            # Apply geospatial filtering if coordinates provided
            if filters.latitude and filters.longitude and filters.radius_km:
                events = filter_by_location(
                    events,
                    filters.latitude,
                    filters.longitude,
                    filters.radius_km
                )
            
            # Get total count (approximate)
            total = firebase_client.get_collection_count(
                self.collection,
                query_filters if query_filters else None
            )
            
            # Convert to Event models with transformation
            event_models = []
            for event_data in events:
                try:
                    transformed = self._transform_event_data(event_data)
                    event_models.append(Event(**transformed))
                except Exception as e:
                    logger.warning(f"Skipping event due to transformation error: {str(e)}")
                    continue
            
            return {
                "events": event_models,
                "total": total,
                "page": filters.page,
                "page_size": filters.page_size,
                "has_more": has_more
            }
            
        except Exception as e:
            logger.error(f"Failed to list events: {str(e)}")
            raise
    
    async def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Event:
        """Update event"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            firebase_client.update_document(self.collection, event_id, update_data)
            
            # Get updated event
            event_data = firebase_client.get_document(self.collection, event_id)
            logger.info(f"Updated event {event_id}")
            
            return Event(**event_data)
            
        except Exception as e:
            logger.error(f"Failed to update event {event_id}: {str(e)}")
            raise
    
    async def delete_event(self, event_id: str) -> None:
        """Delete event"""
        try:
            firebase_client.delete_document(self.collection, event_id)
            logger.info(f"Deleted event {event_id}")
        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {str(e)}")
            raise
    
    async def upvote_event(self, event_id: str) -> Event:
        """Increment upvote count for event"""
        try:
            event_data = firebase_client.get_document(self.collection, event_id)
            if not event_data:
                raise ValueError(f"Event {event_id} not found")
            
            current_upvotes = event_data.get('upvotes', 0)
            firebase_client.update_document(
                self.collection,
                event_id,
                {'upvotes': current_upvotes + 1}
            )
            
            # Get updated event
            event_data = firebase_client.get_document(self.collection, event_id)
            logger.info(f"Upvoted event {event_id}")
            
            return Event(**event_data)
            
        except Exception as e:
            logger.error(f"Failed to upvote event {event_id}: {str(e)}")
            raise
    
    async def get_events_by_category(self, category: EventCategory, limit: int = 10) -> List[Event]:
        """Get recent events by category"""
        try:
            events = firebase_client.query_documents(
                collection=self.collection,
                filters=[('category', '==', category.value)],
                order_by='timestamp',
                limit=limit
            )
            
            return [Event(**event) for event in events]
            
        except Exception as e:
            logger.error(f"Failed to get events by category: {str(e)}")
            raise
    
    async def get_events_by_area(self, area: str, limit: int = 10) -> List[Event]:
        """Get recent events by area"""
        try:
            events = firebase_client.query_documents(
                collection=self.collection,
                filters=[('location.area', '==', area)],
                order_by='timestamp',
                limit=limit
            )
            
            return [Event(**event) for event in events]
            
        except Exception as e:
            logger.error(f"Failed to get events by area: {str(e)}")
            raise
    
    async def get_recent_events(self, hours: int = 24, limit: int = 50) -> List[Event]:
        """Get events from the last N hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            events = firebase_client.query_documents(
                collection=self.collection,
                filters=[('timestamp', '>=', cutoff_time)],
                order_by='timestamp',
                limit=limit
            )
            
            return [Event(**event) for event in events]
            
        except Exception as e:
            logger.error(f"Failed to get recent events: {str(e)}")
            raise


# Singleton instance
event_service = EventService()


def get_event_service() -> EventService:
    """Get event service instance"""
    return event_service
