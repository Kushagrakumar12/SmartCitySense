"""
Firebase Event Reader
Reads events from Person 1's Firebase collection

EXPLANATION:
Alternative to Kafka - reads from Firebase Firestore.
Person 1 may write events to Firebase instead of (or in addition to) Kafka.

WHY FIREBASE?
- Simpler setup than Kafka
- Good for moderate volume
- Built-in querying
- Real-time listeners available

WORKFLOW:
1. Connect to Firestore
2. Query Person 1's collection
3. Filter by timestamp (only new events)
4. Return batch of events

NOTE: We track last processed timestamp to avoid reprocessing.

"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  firebase-admin not installed. Run: pip install firebase-admin")

from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


class FirebaseEventReader:
    """
    Reads events from Firebase Firestore
    
    Features:
    - Query by timestamp
    - Track last processed event
    - Batch reading
    - Real-time listener (optional)
    """
    
    def __init__(self):
        """Initialize Firebase connection"""
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin library not installed")
        
        self.project_id = Config.FIREBASE_PROJECT_ID
        self.key_path = Config.FIREBASE_PRIVATE_KEY_PATH
        self.collection_name = Config.FIREBASE_INPUT_COLLECTION
        
        self.db = None
        self.last_timestamp = None
        
        self._initialize_firebase()
        
        logger.info(f"Firebase reader initialized for collection '{self.collection_name}'")
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if not firebase_admin._apps:
                # Initialize with credentials
                if self.key_path:
                    cred = credentials.Certificate(self.key_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials (works in Google Cloud)
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("✓ Connected to Firebase Firestore")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def read_new_events(self, max_events: int = None) -> List[Dict[str, Any]]:
        """
        Read new events since last check
        
        Args:
            max_events: Maximum number of events to read
        
        Returns:
            List of event dictionaries
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return []
        
        batch_size = max_events or Config.BATCH_SIZE
        events = []
        
        try:
            # Get collection reference
            collection = self.db.collection(self.collection_name)
            
            # Build query
            query = collection.order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            # Filter by last timestamp if available
            if self.last_timestamp:
                query = query.where('timestamp', '>', self.last_timestamp)
            
            # Limit results
            query = query.limit(batch_size)
            
            # Execute query
            docs = query.stream()
            
            for doc in docs:
                event = doc.to_dict()
                event['id'] = doc.id  # Add document ID
                
                # Add metadata
                event['_firebase_metadata'] = {
                    'document_id': doc.id,
                    'read_at': datetime.utcnow().isoformat()
                }
                
                events.append(event)
            
            # Update last timestamp
            if events:
                # Events are ordered by timestamp descending, so first is newest
                latest_timestamp = events[0].get('timestamp')
                if latest_timestamp:
                    self.last_timestamp = latest_timestamp
                
                logger.info(f"Read {len(events)} new events from Firebase")
            
        except Exception as e:
            logger.error(f"Error reading from Firebase: {e}")
        
        return events
    
    def read_events_in_range(self, start_time: datetime, 
                            end_time: datetime = None,
                            max_events: int = None) -> List[Dict[str, Any]]:
        """
        Read events within a time range
        
        Args:
            start_time: Start of time range
            end_time: End of time range (default: now)
            max_events: Maximum events to return
        
        Returns:
            List of events
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return []
        
        if end_time is None:
            end_time = datetime.utcnow()
        
        batch_size = max_events or Config.BATCH_SIZE
        events = []
        
        try:
            collection = self.db.collection(self.collection_name)
            
            # Build range query
            query = (collection
                    .where('timestamp', '>=', start_time.isoformat())
                    .where('timestamp', '<=', end_time.isoformat())
                    .order_by('timestamp')
                    .limit(batch_size))
            
            docs = query.stream()
            
            for doc in docs:
                event = doc.to_dict()
                event['id'] = doc.id
                events.append(event)
            
            logger.info(f"Read {len(events)} events from {start_time} to {end_time}")
            
        except Exception as e:
            logger.error(f"Error reading range from Firebase: {e}")
        
        return events
    
    def read_by_type(self, event_type: str, max_events: int = None) -> List[Dict[str, Any]]:
        """
        Read events of a specific type
        
        Args:
            event_type: Type of events to read
            max_events: Maximum events to return
        
        Returns:
            List of events
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return []
        
        batch_size = max_events or Config.BATCH_SIZE
        events = []
        
        try:
            collection = self.db.collection(self.collection_name)
            
            query = (collection
                    .where('type', '==', event_type)
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(batch_size))
            
            docs = query.stream()
            
            for doc in docs:
                event = doc.to_dict()
                event['id'] = doc.id
                events.append(event)
            
            logger.info(f"Read {len(events)} events of type '{event_type}'")
            
        except Exception as e:
            logger.error(f"Error reading by type from Firebase: {e}")
        
        return events
    
    def poll_continuously(self, callback: callable, interval_seconds: int = None):
        """
        Continuously poll for new events
        
        Args:
            callback: Function to call with new events
            interval_seconds: Polling interval
        """
        import time
        
        interval = interval_seconds or Config.PROCESSING_INTERVAL_SECONDS
        logger.info(f"Starting continuous polling (interval={interval}s)")
        
        try:
            while True:
                events = self.read_new_events()
                
                if events:
                    try:
                        callback(events)
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Polling stopped by user")
        except Exception as e:
            logger.error(f"Error in polling: {e}")
    
    def reset_timestamp(self):
        """Reset last timestamp (will read from beginning)"""
        self.last_timestamp = None
        logger.info("Reset last timestamp")


def main():
    """Test Firebase reader"""
    print("\n" + "="*60)
    print("🔥 Firebase Event Reader Test")
    print("="*60 + "\n")
    
    if not FIREBASE_AVAILABLE:
        print("❌ firebase-admin not installed")
        print("   Install: pip install firebase-admin")
        return
    
    if not Config.FIREBASE_PROJECT_ID:
        print("❌ Firebase not configured")
        print("   Set FIREBASE_PROJECT_ID in .env")
        return
    
    try:
        reader = FirebaseEventReader()
        
        print(f"Project: {reader.project_id}")
        print(f"Collection: {reader.collection_name}")
        print()
        
        # Read recent events
        print("Reading recent events...")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)  # Last hour
        
        events = reader.read_events_in_range(start_time, end_time, max_events=5)
        
        if events:
            print(f"\n✓ Found {len(events)} events")
            print("\nFirst event:")
            print(json.dumps(events[0], indent=2, default=str))
        else:
            print("\n⚠️  No events found")
            print("   Make sure Person 1 has written events to Firebase")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
