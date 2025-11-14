"""
Firebase Storage
Writes processed events to Firestore

EXPLANATION:
After processing (deduplicate, geocode, categorize), we store the enhanced
events in Firebase Firestore for:
- Member B (AI/ML) to analyze
- Member C (Frontend) to display

WHY FIRESTORE?
- NoSQL flexibility: Easy to add fields
- Real-time: Frontend gets updates instantly
- Querying: Can filter by zone, type, urgency, etc.
- Scalable: Handles millions of events
- Indexing: Fast queries

DATABASE STRUCTURE:
Collection: processed_events
Document ID: event_id
Fields:
  - id, type, subtype, description
  - location, coordinates, zone, neighborhood
  - timestamp, urgency, tags
  - quality_score
  - source, duplicate_of, similar_events
  - processed_at

INDEXES NEEDED (create in Firebase Console):
- timestamp (descending)
- zone + timestamp (composite)
- type + timestamp (composite)
- urgency + timestamp (composite)
- tags (array-contains) + timestamp (composite)

"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1 import FieldFilter
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  firebase-admin not installed. Run: pip install firebase-admin")

from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


class FirebaseStorage:
    """
    Writes processed events to Firestore
    
    Features:
    - Batch writes (efficient)
    - Upsert (update or insert)
    - Automatic timestamps
    - Error recovery
    """
    
    def __init__(self):
        """Initialize Firebase storage"""
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin library not installed")
        
        self.project_id = Config.FIREBASE_PROJECT_ID
        self.key_path = Config.FIREBASE_PRIVATE_KEY_PATH
        self.collection_name = Config.FIREBASE_OUTPUT_COLLECTION
        
        self.db = None
        self._initialize_firebase()
        
        logger.info(f"Firebase storage initialized for collection '{self.collection_name}'")
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if not firebase_admin._apps:
                if self.key_path:
                    cred = credentials.Certificate(self.key_path)
                    firebase_admin.initialize_app(cred)
                else:
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("✓ Connected to Firebase Firestore")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def _prepare_event_for_storage(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare event data for Firestore
        
        - Add processing timestamp
        - Remove internal metadata
        - Convert datetime objects to ISO strings
        
        Args:
            event: Event dictionary
        
        Returns:
            Prepared event
        """
        # Create copy to avoid modifying original
        stored_event = event.copy()
        
        # Add processing timestamp
        stored_event['processed_at'] = datetime.utcnow().isoformat()
        
        # Remove internal metadata (Kafka, Firebase read metadata)
        stored_event.pop('_kafka_metadata', None)
        stored_event.pop('_firebase_metadata', None)
        
        # Ensure timestamp is ISO string
        if 'timestamp' in stored_event and isinstance(stored_event['timestamp'], datetime):
            stored_event['timestamp'] = stored_event['timestamp'].isoformat()
        
        return stored_event
    
    def store_event(self, event: Dict[str, Any]) -> bool:
        """
        Store a single processed event
        
        Args:
            event: Processed event dictionary
        
        Returns:
            True if successful
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Prepare event
            stored_event = self._prepare_event_for_storage(event)
            
            # Get event ID
            event_id = stored_event.get('id')
            if not event_id:
                logger.error("Event missing ID")
                return False
            
            # Store in Firestore
            doc_ref = self.db.collection(self.collection_name).document(event_id)
            doc_ref.set(stored_event)
            
            logger.debug(f"Stored event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return False
    
    def store_batch(self, events: List[Dict[str, Any]]) -> int:
        """
        Store multiple events in a batch (more efficient)
        
        Args:
            events: List of processed events
        
        Returns:
            Number of successfully stored events
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return 0
        
        if not events:
            return 0
        
        try:
            # Firestore batches are limited to 500 operations
            BATCH_LIMIT = 500
            stored_count = 0
            
            for i in range(0, len(events), BATCH_LIMIT):
                batch_events = events[i:i + BATCH_LIMIT]
                
                # Create batch
                batch = self.db.batch()
                
                for event in batch_events:
                    stored_event = self._prepare_event_for_storage(event)
                    event_id = stored_event.get('id')
                    
                    if not event_id:
                        logger.warning("Skipping event without ID")
                        continue
                    
                    doc_ref = self.db.collection(self.collection_name).document(event_id)
                    batch.set(doc_ref, stored_event)
                    stored_count += 1
                
                # Commit batch
                batch.commit()
                logger.info(f"Batch committed: {len(batch_events)} events")
            
            logger.info(f"✓ Stored {stored_count} events")
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing batch: {e}")
            return 0
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields of an event
        
        Args:
            event_id: Event ID to update
            updates: Dictionary of fields to update
        
        Returns:
            True if successful
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return False
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(event_id)
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            doc_ref.update(updates)
            logger.debug(f"Updated event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {e}")
            return False
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific event
        
        Args:
            event_id: Event ID
        
        Returns:
            Event dictionary or None
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return None
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(event_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving event {event_id}: {e}")
            return None
    
    def query_events(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query events with filters
        
        Args:
            filters: Dictionary of field:value filters
            limit: Maximum events to return
        
        Returns:
            List of matching events
        """
        if not self.db:
            logger.error("Firebase not initialized")
            return []
        
        try:
            query = self.db.collection(self.collection_name)
            
            # Apply filters
            for field, value in filters.items():
                query = query.where(field, '==', value)
            
            # Order by timestamp (newest first)
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            # Limit results
            query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            
            events = []
            for doc in docs:
                event = doc.to_dict()
                event['id'] = doc.id
                events.append(event)
            
            logger.info(f"Query returned {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Error querying events: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.db:
            return {}
        
        try:
            collection = self.db.collection(self.collection_name)
            
            # Count total events
            docs = collection.stream()
            total_count = sum(1 for _ in docs)
            
            # Count by type
            type_counts = {}
            for event_type in ['traffic', 'civic', 'emergency', 'social']:
                count = len(list(collection.where('type', '==', event_type).stream()))
                if count > 0:
                    type_counts[event_type] = count
            
            # Count by urgency
            urgency_counts = {}
            for urgency in ['critical', 'needs_attention', 'can_wait', 'resolved']:
                count = len(list(collection.where('urgency', '==', urgency).stream()))
                if count > 0:
                    urgency_counts[urgency] = count
            
            return {
                'total_events': total_count,
                'by_type': type_counts,
                'by_urgency': urgency_counts,
                'collection': self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


def main():
    """Test Firebase storage"""
    print("\n" + "="*60)
    print("💾 Firebase Storage Test")
    print("="*60 + "\n")
    
    if not FIREBASE_AVAILABLE:
        print("❌ firebase-admin not installed")
        return
    
    if not Config.FIREBASE_PROJECT_ID:
        print("❌ Firebase not configured")
        return
    
    try:
        storage = FirebaseStorage()
        
        print(f"Project: {storage.project_id}")
        print(f"Collection: {storage.collection_name}")
        print()
        
        # Test event
        test_event = {
            'id': f'test_{datetime.now().timestamp()}',
            'type': 'traffic',
            'subtype': 'traffic_congestion',
            'description': 'Heavy traffic on MG Road',
            'location': 'MG Road',
            'coordinates': {'lat': 12.9716, 'lon': 77.5946},
            'zone': 'Central Bangalore',
            'urgency': 'needs_attention',
            'tags': ['traffic', 'mgroad', 'central_bangalore'],
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'test',
            'quality_score': 0.85
        }
        
        print("Storing test event...")
        success = storage.store_event(test_event)
        
        if success:
            print("✓ Event stored successfully")
            
            # Retrieve it
            print("\nRetrieving event...")
            retrieved = storage.get_event(test_event['id'])
            
            if retrieved:
                print("✓ Event retrieved:")
                print(json.dumps(retrieved, indent=2, default=str))
            
            # Get stats
            print("\nStorage statistics:")
            stats = storage.get_stats()
            print(json.dumps(stats, indent=2))
        else:
            print("❌ Failed to store event")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
