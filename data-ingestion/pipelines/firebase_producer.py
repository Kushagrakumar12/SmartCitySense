"""
Firebase Pub/Sub Producer (Alternative to Kafka)
For teams using Firebase/GCP infrastructure
"""
import json
from typing import List, Optional
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError as e:
    FIREBASE_AVAILABLE = False
    import_error = str(e)

from config import Config
from utils import setup_logger, Event

logger = setup_logger(__name__)


class FirebaseProducer:
    """
    Firebase producer for streaming events
    Uses Firestore for storage and Pub/Sub for streaming
    """
    
    def __init__(self):
        """Initialize Firebase connection"""
        self.db = None
        self.collection_name = Config.FIREBASE_COLLECTION or "citypulse_events"
        
        if not FIREBASE_AVAILABLE:
            logger.warning("⚠️  Firebase SDK not installed")
            return
        
        if not Config.FIREBASE_PROJECT_ID:
            logger.warning("⚠️  Firebase not configured")
            return
        
        try:
            # Initialize Firebase (if not already initialized)
            if not firebase_admin._apps:
                if Config.FIREBASE_PRIVATE_KEY_PATH:
                    cred = credentials.Certificate(Config.FIREBASE_PRIVATE_KEY_PATH)
                    firebase_admin.initialize_app(cred, {
                        'projectId': Config.FIREBASE_PROJECT_ID
                    })
                else:
                    # Use default credentials (for Cloud Run / App Engine)
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("✓ Firebase connected")
        
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
    
    def send_event(self, event: Event) -> bool:
        """
        Send event to Firebase Firestore
        
        Args:
            event: Event object to store
        
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            logger.warning(f"Firebase not available, would send: {event.description[:50]}...")
            return False
        
        try:
            # Convert event to dictionary
            event_data = event.to_dict()
            
            # Add to Firestore
            doc_ref = self.db.collection(self.collection_name).document(event.id)
            doc_ref.set(event_data)
            
            logger.debug(f"Event stored in Firestore: {event.id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending event to Firebase: {e}")
            return False
    
    def send_events_batch(self, events: List[Event]) -> int:
        """
        Send multiple events in batch
        
        Args:
            events: List of Event objects
        
        Returns:
            Number of successfully sent events
        """
        if not events:
            logger.warning("No events to send")
            return 0
        
        if not self.db:
            logger.warning("Firebase not available")
            return 0
        
        success_count = 0
        
        # Use batch writes for efficiency
        batch = self.db.batch()
        
        for event in events:
            try:
                event_data = event.to_dict()
                doc_ref = self.db.collection(self.collection_name).document(event.id)
                batch.set(doc_ref, event_data)
                success_count += 1
            except Exception as e:
                logger.error(f"Error preparing event for batch: {e}")
        
        # Commit batch
        try:
            batch.commit()
            logger.info(f"Sent {success_count} events to Firebase")
        except Exception as e:
            logger.error(f"Error committing batch: {e}")
            success_count = 0
        
        return success_count
    
    def query_events(self, limit: int = 10) -> List[dict]:
        """
        Query recent events from Firestore (for testing)
        
        Args:
            limit: Number of events to retrieve
        
        Returns:
            List of event dictionaries
        """
        if not self.db:
            return []
        
        try:
            docs = (
                self.db.collection(self.collection_name)
                .order_by('timestamp', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            
            events = [doc.to_dict() for doc in docs]
            return events
        
        except Exception as e:
            logger.error(f"Error querying events: {e}")
            return []


def main():
    """Test Firebase producer"""
    print("\n" + "="*60)
    print("🔥 Firebase Producer Test")
    print("="*60 + "\n")
    
    if not FIREBASE_AVAILABLE:
        print("⚠️  Firebase SDK not installed")
        print("Install with: pip install firebase-admin")
        return
    
    # Create sample events
    from utils import Coordinates
    
    sample_events = [
        Event(
            type="traffic",
            source="google_maps",
            description="Test traffic event for Firebase",
            location="Test Location",
            coordinates=Coordinates(lat=12.9716, lon=77.5946),
            severity="medium"
        ),
        Event(
            type="civic",
            source="civic_portal",
            description="Test civic event for Firebase",
            location="Test Location 2",
            severity="low"
        )
    ]
    
    # Test sending
    producer = FirebaseProducer()
    
    if producer.db:
        print(f"✓ Connected to Firebase\n")
        print(f"Sending {len(sample_events)} test events...\n")
        
        success = producer.send_events_batch(sample_events)
        print(f"\n✓ Sent {success}/{len(sample_events)} events")
        
        # Query back
        print("\nQuerying recent events:")
        recent = producer.query_events(limit=5)
        for i, event in enumerate(recent, 1):
            print(f"{i}. {event.get('type')}: {event.get('description')[:50]}...")
    else:
        print("⚠️  Firebase not configured")
        print("Set FIREBASE_PROJECT_ID and credentials in .env")


if __name__ == "__main__":
    main()
