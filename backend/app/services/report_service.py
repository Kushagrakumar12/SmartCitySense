"""
Report Service
Business logic for user-submitted reports
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from app.utils.firebase_client import firebase_client
from app.models.report import Report, ReportCreate
from app.services.ai_client import ai_ml_client
from app.services.event_service import event_service

logger = structlog.get_logger()


class ReportService:
    """Service for report-related operations"""
    
    def __init__(self):
        self.collection = "reports"
        self.db = firebase_client.get_db()
    
    async def create_report(self, report_data: ReportCreate, user_id: str) -> Report:
        """
        Create a new user-submitted report
        
        Args:
            report_data: Report data
            user_id: ID of the user submitting the report
            
        Returns:
            Created report
        """
        try:
            # Convert to dictionary
            data = report_data.model_dump()
            data['reported_by'] = user_id
            data['created_at'] = datetime.utcnow()
            data['status'] = 'pending'
            
            # Analyze media if provided
            ai_analysis = {}
            if data.get('media_urls'):
                for media_url in data['media_urls']:
                    # Analyze image with vision model
                    vision_result = await ai_ml_client.analyze_image(
                        media_url,
                        context=data.get('description')
                    )
                    
                    if vision_result.get('success'):
                        ai_analysis['vision'] = vision_result
                        
                        # Use AI analysis to enrich report
                        if 'detected_objects' in vision_result:
                            data['tags'] = vision_result.get('detected_objects', [])
                        
                        if 'category_suggestion' in vision_result:
                            # Optionally update category based on AI suggestion
                            data['ai_suggested_category'] = vision_result['category_suggestion']
            
            # Analyze sentiment
            sentiment_result = await ai_ml_client.analyze_sentiment(data['description'])
            if sentiment_result.get('success'):
                ai_analysis['sentiment'] = sentiment_result
                data['sentiment_score'] = sentiment_result.get('score', 0)
            
            data['ai_analysis'] = ai_analysis
            
            # Add to Firestore
            report_id = firebase_client.add_document(self.collection, data)
            
            # Retrieve created report
            report_doc = firebase_client.get_document(self.collection, report_id)
            logger.info(f"Created report {report_id} by user {user_id}")
            
            # Auto-convert to event if confidence is high
            if ai_analysis.get('vision', {}).get('confidence', 0) > 0.7:
                await self._convert_report_to_event(report_id, report_doc)
            
            return Report(**report_doc)
            
        except Exception as e:
            logger.error(f"Failed to create report: {str(e)}")
            raise
    
    async def _convert_report_to_event(self, report_id: str, report_data: Dict[str, Any]) -> None:
        """
        Convert a report to an event
        
        Args:
            report_id: Report ID
            report_data: Report data
        """
        try:
            # Create event from report
            event_data = {
                'title': report_data['title'],
                'description': report_data['description'],
                'category': report_data['category'],
                'severity': report_data.get('severity', 'medium'),
                'location': report_data['location'],
                'source': 'user_report',
                'media_urls': report_data.get('media_urls', []),
                'sentiment_score': report_data.get('sentiment_score'),
                'tags': report_data.get('tags', [])
            }
            
            event = await event_service.create_event(
                event_data,
                user_id=report_data['reported_by']
            )
            
            # Update report with event ID
            firebase_client.update_document(
                self.collection,
                report_id,
                {
                    'event_id': event.id,
                    'status': 'converted',
                    'processed_at': datetime.utcnow()
                }
            )
            
            logger.info(f"Converted report {report_id} to event {event.id}")
            
        except Exception as e:
            logger.error(f"Failed to convert report to event: {str(e)}")
    
    async def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        try:
            report_data = firebase_client.get_document(self.collection, report_id)
            if report_data:
                return Report(**report_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get report {report_id}: {str(e)}")
            raise
    
    async def list_reports(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List reports with filtering
        
        Args:
            user_id: Filter by user ID
            status: Filter by status
            page: Page number
            page_size: Items per page
            
        Returns:
            Dictionary with reports and pagination info
        """
        try:
            filters = []
            
            if user_id:
                filters.append(('reported_by', '==', user_id))
            
            if status:
                filters.append(('status', '==', status))
            
            offset = (page - 1) * page_size
            
            reports = firebase_client.query_documents(
                collection=self.collection,
                filters=filters if filters else None,
                order_by='created_at',
                limit=page_size,
                offset=offset
            )
            
            total = firebase_client.get_collection_count(
                self.collection,
                filters if filters else None
            )
            
            report_models = [Report(**report) for report in reports]
            
            return {
                "reports": report_models,
                "total": total,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"Failed to list reports: {str(e)}")
            raise
    
    async def update_report_status(self, report_id: str, status: str) -> Report:
        """Update report status"""
        try:
            update_data = {
                'status': status,
                'processed_at': datetime.utcnow()
            }
            
            firebase_client.update_document(self.collection, report_id, update_data)
            
            # Get updated report
            report_data = firebase_client.get_document(self.collection, report_id)
            logger.info(f"Updated report {report_id} status to {status}")
            
            return Report(**report_data)
            
        except Exception as e:
            logger.error(f"Failed to update report status: {str(e)}")
            raise


# Singleton instance
report_service = ReportService()


def get_report_service() -> ReportService:
    """Get report service instance"""
    return report_service
