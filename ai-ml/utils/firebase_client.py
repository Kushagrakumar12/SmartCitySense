"""
Firebase Client for AI/ML Module
Handles Firestore operations for storing events, predictions, and alerts
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from pathlib import Path

from utils.logger import get_logger
from config.config import config

logger = get_logger("firebase")


class FirebaseClient:
    """Firebase/Firestore client for data operations"""
    
    def __init__(self):
        """Initialize Firebase connection"""
        self.db = None
        self.initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.db = firestore.client()
                self.initialized = True
                return
            
            # Get credentials path
            cred_path = Path(config.firebase.credentials_path)
            
            if not cred_path.exists():
                logger.warning(f"Firebase credentials not found at {cred_path}")
                logger.warning("Running in mock mode - no Firebase connection")
                return
            
            # Initialize Firebase
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred, {
                'projectId': config.firebase.project_id,
            })
            
            self.db = firestore.client()
            self.initialized = True
            logger.success(f"Firebase initialized - Project: {config.firebase.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.initialized = False
    
    def save_vision_result(self, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Save vision analysis result to Firestore
        
        Args:
            event_data: Vision analysis result data
        
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - skipping save")
            return None
        
        try:
            # Add metadata
            event_data['created_at'] = datetime.now(timezone.utc)
            event_data['source'] = 'vision_analysis'
            event_data['processed'] = True
            
            # Save to events collection
            doc_ref = self.db.collection(config.firebase.events_collection).add(event_data)
            doc_id = doc_ref[1].id
            
            logger.info(f"Saved vision result to Firestore: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save vision result: {e}")
            return None
    
    def save_prediction_result(self, prediction_data: Dict[str, Any]) -> Optional[str]:
        """
        Save prediction result to Firestore
        
        Args:
            prediction_data: Prediction analysis result
        
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - skipping save")
            return None
        
        try:
            # Add metadata
            prediction_data['created_at'] = datetime.now(timezone.utc)
            prediction_data['source'] = 'predictive_analysis'
            
            # Save to predictions collection
            doc_ref = self.db.collection(config.firebase.predictions_collection).add(prediction_data)
            doc_id = doc_ref[1].id
            
            logger.info(f"Saved prediction result to Firestore: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save prediction result: {e}")
            return None
    
    def save_alert(self, alert_data: Dict[str, Any]) -> Optional[str]:
        """
        Save alert to Firestore
        
        Args:
            alert_data: Alert information
        
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - skipping alert save")
            return None
        
        try:
            # Add metadata
            alert_data['created_at'] = datetime.now(timezone.utc)
            alert_data['acknowledged'] = False
            
            # Save to alerts collection
            doc_ref = self.db.collection(config.firebase.alerts_collection).add(alert_data)
            doc_id = doc_ref[1].id
            
            logger.warning(f"🚨 Alert saved to Firestore: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
            return None
    
    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        location: Optional[str] = None,
        minutes: int = 60,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent events from Firestore
        
        Args:
            event_type: Filter by event type
            location: Filter by location
            minutes: Time window in minutes
            limit: Maximum number of events
        
        Returns:
            List of event documents
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - returning empty list")
            return []
        
        try:
            from datetime import timedelta
            from dateutil import parser as date_parser
            
            # Calculate time threshold
            time_threshold = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            # Build query - get recent events without timestamp filter first
            # because timestamps might be strings in different formats
            query = self.db.collection(config.firebase.events_collection)
            
            # Apply filters if provided
            if event_type:
                query = query.where(filter=FieldFilter("type", "==", event_type))
            
            if location:
                query = query.where(filter=FieldFilter("location", "==", location))
            
            # Get more events than needed to filter by time in memory
            query = query.limit(limit * 3)
            
            # Execute query
            docs = query.stream()
            all_events = [doc.to_dict() for doc in docs]
            
            # Filter by timestamp in memory (handles string timestamps)
            events = []
            for event in all_events:
                try:
                    # Parse timestamp (could be string or datetime)
                    event_time_str = event.get('timestamp')
                    if event_time_str:
                        if isinstance(event_time_str, str):
                            event_time = date_parser.parse(event_time_str).replace(tzinfo=None)
                        else:
                            event_time = event_time_str
                        
                        # Check if within time window
                        if event_time >= time_threshold:
                            events.append(event)
                    else:
                        # No timestamp, include it anyway
                        events.append(event)
                except Exception as e:
                    logger.warning(f"Could not parse timestamp for event: {e}")
                    # Include event anyway if timestamp parsing fails
                    events.append(event)
            
            # Sort by timestamp (most recent first) and limit
            events = sorted(events, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
            
            logger.info(f"Retrieved {len(events)} events from last {minutes} minutes")
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            logger.exception(e)  # Log full traceback
            return []
    
    def get_historical_data(
        self,
        event_type: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical events for training/analysis
        
        Args:
            event_type: Filter by event type
            days: Number of days to look back
        
        Returns:
            List of historical events
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - returning empty list")
            return []
        
        try:
            from datetime import timedelta
            time_threshold = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = self.db.collection(config.firebase.events_collection)
            query = query.where(filter=FieldFilter("timestamp", ">=", time_threshold))
            
            if event_type:
                query = query.where(filter=FieldFilter("event_type", "==", event_type))
            
            docs = query.stream()
            events = [doc.to_dict() for doc in docs]
            
            logger.info(f"Retrieved {len(events)} historical events from last {days} days")
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve historical data: {e}")
            return []
    
    def save_summarized_event(self, summary_data: Dict[str, Any]) -> Optional[str]:
        """
        Save summarized event to Firestore (Member B1)
        
        Args:
            summary_data: Dictionary with summary information
            
        Returns:
            Document ID or None if failed
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - skipping save")
            return None
        
        try:
            collection = config.text.summarized_events_collection
            doc_ref = self.db.collection(collection).add(summary_data)
            doc_id = doc_ref[1].id
            
            logger.info(f"Saved summarized event {doc_id} to {collection}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save summarized event: {e}")
            return None
    
    def save_mood_map(self, mood_map_data: Dict[str, Any]) -> Optional[str]:
        """
        Save mood map to Firestore (Member B1)
        
        Args:
            mood_map_data: Dictionary with mood map information
            
        Returns:
            Document ID or None if failed
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - skipping save")
            return None
        
        try:
            collection = config.text.mood_map_collection
            doc_ref = self.db.collection(collection).add(mood_map_data)
            doc_id = doc_ref[1].id
            
            logger.info(f"Saved mood map {doc_id} to {collection}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save mood map: {e}")
            return None
    
    def get_grouped_reports(
        self,
        event_type: Optional[str] = None,
        location: Optional[str] = None,
        minutes: int = 60
    ) -> Dict[str, List[str]]:
        """
        Get text reports grouped by location and event type for summarization
        
        Args:
            event_type: Filter by event type
            location: Filter by location
            minutes: Time window in minutes
            
        Returns:
            Dictionary mapping group_id to list of text reports
        """
        if not self.initialized:
            logger.warning("Firebase not initialized - returning empty dict")
            return {}
        
        try:
            events = self.get_recent_events(event_type, location, minutes, limit=500)
            
            # Group by location and event type
            from collections import defaultdict
            grouped = defaultdict(list)
            
            for event in events:
                if "description" in event:
                    evt_type = event.get("event_type", "unknown")
                    evt_location = event.get("location", "unknown")
                    group_key = f"{evt_type}_{evt_location}"
                    grouped[group_key].append(event["description"])
            
            logger.info(f"Grouped {len(events)} events into {len(grouped)} groups")
            return dict(grouped)
            
        except Exception as e:
            logger.error(f"Failed to group reports: {e}")
            return {}


# Global Firebase client instance
firebase_client = FirebaseClient()


if __name__ == "__main__":
    # Test Firebase connection
    client = FirebaseClient()
    
    if client.initialized:
        print("✅ Firebase connection successful")
        
        # Test save
        test_event = {
            "event_type": "test",
            "description": "Test event from firebase_client.py",
            "timestamp": datetime.now(timezone.utc),
            "location": "Test Location"
        }
        doc_id = client.save_vision_result(test_event)
        print(f"Test document ID: {doc_id}")
    else:
        print("❌ Firebase connection failed - check credentials")
