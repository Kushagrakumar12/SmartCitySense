"""
Alert Service
Business logic for predictive alerts and anomaly detection
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog

from app.utils.firebase_client import firebase_client
from app.models.alert import Alert, AlertFilter, AlertType, AlertPriority
from app.services.ai_client import ai_ml_client
from app.services.event_service import event_service
from app.services.notification_service import notification_service

logger = structlog.get_logger()


class AlertService:
    """Service for alert-related operations"""
    
    def __init__(self):
        self.collection = "alerts"
        self.db = firebase_client.get_db()
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """
        Create a new alert
        
        Args:
            alert_data: Alert data
            
        Returns:
            Created alert
        """
        try:
            alert_data['created_at'] = datetime.utcnow()
            alert_data['is_active'] = True
            alert_data['notification_sent'] = False
            
            # Add to Firestore
            alert_id = firebase_client.add_document(self.collection, alert_data)
            
            # Retrieve created alert
            alert_doc = firebase_client.get_document(self.collection, alert_id)
            logger.info(f"Created alert {alert_id}")
            
            # Send notification to subscribed users
            await notification_service.send_alert_notification(alert_doc)
            
            # Mark notification as sent
            firebase_client.update_document(
                self.collection,
                alert_id,
                {'notification_sent': True}
            )
            
            return Alert(**alert_doc)
            
        except Exception as e:
            logger.error(f"Failed to create alert: {str(e)}")
            raise
    
    async def detect_anomalies(self, time_window: str = "1h") -> List[Alert]:
        """
        Detect anomalies in recent events and create alerts
        
        Args:
            time_window: Time window for analysis
            
        Returns:
            List of created alerts
        """
        try:
            # Get recent events
            hours = int(time_window.rstrip('h'))
            recent_events = await event_service.get_recent_events(hours=hours, limit=100)
            
            if len(recent_events) < 5:
                logger.info("Not enough events for anomaly detection")
                return []
            
            # Convert events to dictionaries
            events_data = [event.model_dump() for event in recent_events]
            
            # Call AI/ML anomaly detection service
            anomaly_result = await ai_ml_client.detect_anomalies(events_data, time_window)
            
            if not anomaly_result.get('success'):
                logger.warning("Anomaly detection failed")
                return []
            
            # Create alerts for detected anomalies
            alerts = []
            anomalies = anomaly_result.get('anomalies', [])
            
            for anomaly in anomalies:
                alert_data = {
                    'title': anomaly.get('title', 'Anomaly Detected'),
                    'message': anomaly.get('description', 'Unusual pattern detected in event data'),
                    'alert_type': AlertType.ANOMALY.value,
                    'priority': self._determine_priority(anomaly),
                    'category': anomaly.get('category', 'Other'),
                    'affected_areas': anomaly.get('areas', []),
                    'related_events': anomaly.get('event_ids', []),
                    'confidence_score': anomaly.get('confidence', 0.0),
                    'recommendations': anomaly.get('recommendations', []),
                    'metadata': anomaly.get('metadata', {})
                }
                
                alert = await self.create_alert(alert_data)
                alerts.append(alert)
            
            logger.info(f"Created {len(alerts)} anomaly alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {str(e)}")
            return []
    
    def _determine_priority(self, anomaly: Dict[str, Any]) -> str:
        """Determine alert priority based on anomaly data"""
        confidence = anomaly.get('confidence', 0.0)
        severity = anomaly.get('severity', 'medium')
        
        if confidence > 0.8 and severity in ['high', 'critical']:
            return AlertPriority.URGENT.value
        elif confidence > 0.6 and severity == 'high':
            return AlertPriority.HIGH.value
        elif confidence > 0.5:
            return AlertPriority.MEDIUM.value
        else:
            return AlertPriority.LOW.value
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        try:
            alert_data = firebase_client.get_document(self.collection, alert_id)
            if alert_data:
                return Alert(**alert_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get alert {alert_id}: {str(e)}")
            raise
    
    async def list_alerts(self, filters: AlertFilter) -> Dict[str, Any]:
        """
        List alerts with filtering
        
        Args:
            filters: Alert filters
            
        Returns:
            Dictionary with alerts and pagination info
        """
        try:
            query_filters = []
            
            if filters.alert_type:
                query_filters.append(('alert_type', '==', filters.alert_type.value))
            
            if filters.priority:
                query_filters.append(('priority', '==', filters.priority.value))
            
            if filters.category:
                query_filters.append(('category', '==', filters.category.value))
            
            if filters.is_active is not None:
                query_filters.append(('is_active', '==', filters.is_active))
            
            offset = (filters.page - 1) * filters.page_size
            
            alerts = firebase_client.query_documents(
                collection=self.collection,
                filters=query_filters if query_filters else None,
                order_by='created_at',
                limit=filters.page_size + 1,
                offset=offset
            )
            
            has_more = len(alerts) > filters.page_size
            if has_more:
                alerts = alerts[:-1]
            
            total = firebase_client.get_collection_count(
                self.collection,
                query_filters if query_filters else None
            )
            
            alert_models = [Alert(**alert) for alert in alerts]
            
            return {
                "alerts": alert_models,
                "total": total,
                "has_more": has_more
            }
            
        except Exception as e:
            logger.error(f"Failed to list alerts: {str(e)}")
            raise
    
    async def deactivate_alert(self, alert_id: str) -> Alert:
        """Deactivate an alert"""
        try:
            firebase_client.update_document(
                self.collection,
                alert_id,
                {'is_active': False, 'updated_at': datetime.utcnow()}
            )
            
            alert_data = firebase_client.get_document(self.collection, alert_id)
            logger.info(f"Deactivated alert {alert_id}")
            
            return Alert(**alert_data)
            
        except Exception as e:
            logger.error(f"Failed to deactivate alert: {str(e)}")
            raise
    
    async def get_active_alerts_for_area(self, area: str) -> List[Alert]:
        """Get active alerts for a specific area"""
        try:
            alerts = firebase_client.query_documents(
                collection=self.collection,
                filters=[
                    ('is_active', '==', True),
                    ('affected_areas', 'array_contains', area)
                ],
                order_by='created_at',
                limit=20
            )
            
            return [Alert(**alert) for alert in alerts]
            
        except Exception as e:
            logger.error(f"Failed to get alerts for area: {str(e)}")
            raise


# Singleton instance
alert_service = AlertService()


def get_alert_service() -> AlertService:
    """Get alert service instance"""
    return alert_service
