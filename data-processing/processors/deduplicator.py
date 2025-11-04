"""
Event Deduplicator
Identifies and removes duplicate events using text similarity and location matching

EXPLANATION:
Person 1 might collect multiple reports of the same event from different sources:
- Twitter: "Heavy traffic on MG Road"
- Google Maps: "Traffic jam at MG Road"  
- Reddit: "Avoid MG Road, major traffic"

All three are talking about the SAME event! This module identifies duplicates and
keeps only one, marking the others as duplicates.

HOW IT WORKS:
1. Text Similarity: Compare descriptions using TF-IDF and fuzzy matching
2. Location Proximity: Events at similar locations are likely the same
3. Time Window: Only compare events within N minutes of each other
4. Clustering: Group similar events together

"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import math

from config import Config
from utils import setup_logger, text_similarity, DataValidator

logger = setup_logger(__name__)


class EventDeduplicator:
    """
    Identifies and removes duplicate events
    
    Uses multiple criteria:
    - Text similarity of descriptions
    - Geographic proximity
    - Temporal proximity
    - Event type matching
    """
    
    def __init__(
        self,
        similarity_threshold: float = None,
        time_window_minutes: int = None,
        distance_threshold_km: float = None
    ):
        """
        Initialize deduplicator
        
        Args:
            similarity_threshold: Text similarity threshold (0-1), default from config
            time_window_minutes: Time window for considering duplicates
            distance_threshold_km: Distance threshold in kilometers
        """
        self.similarity_threshold = similarity_threshold or Config.SIMILARITY_THRESHOLD
        self.time_window_minutes = time_window_minutes or Config.TIME_WINDOW_MINUTES
        self.distance_threshold_km = distance_threshold_km or Config.DISTANCE_THRESHOLD_KM
        
        logger.info(f"Deduplicator initialized:")
        logger.info(f"  Similarity threshold: {self.similarity_threshold}")
        logger.info(f"  Time window: {self.time_window_minutes} minutes")
        logger.info(f"  Distance threshold: {self.distance_threshold_km} km")
    
    def calculate_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
        
        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def are_events_similar(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> tuple[bool, float]:
        """
        Check if two events are similar (potential duplicates)
        
        Criteria:
        1. Same event type
        2. Within time window
        3. High text similarity OR close geographic proximity
        
        Args:
            event1: First event
            event2: Second event
        
        Returns:
            (is_similar, similarity_score)
        """
        # Must be same type
        if event1.get('type') != event2.get('type'):
            return False, 0.0
        
        # Check time window
        try:
            time1 = event1.get('timestamp')
            time2 = event2.get('timestamp')
            
            if isinstance(time1, str):
                time1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
            if isinstance(time2, str):
                time2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
            
            time_diff = abs((time1 - time2).total_seconds() / 60)  # minutes
            
            if time_diff > self.time_window_minutes:
                return False, 0.0
        
        except Exception as e:
            logger.warning(f"Error comparing timestamps: {e}")
            # Continue with other checks
        
        # Calculate text similarity
        desc1 = event1.get('description', '')
        desc2 = event2.get('description', '')
        
        text_sim = text_similarity.calculate_combined_similarity(desc1, desc2)
        
        # Check geographic proximity if coordinates available
        geo_sim = 0.0
        coords1 = event1.get('coordinates')
        coords2 = event2.get('coordinates')
        
        if coords1 and coords2:
            try:
                distance = self.calculate_distance(
                    coords1['lat'], coords1['lon'],
                    coords2['lat'], coords2['lon']
                )
                
                # Convert distance to similarity score (closer = higher)
                # If distance <= threshold, high similarity
                if distance <= self.distance_threshold_km:
                    geo_sim = 1.0 - (distance / self.distance_threshold_km)
                else:
                    geo_sim = 0.0
            
            except Exception as e:
                logger.warning(f"Error calculating distance: {e}")
        
        # Combined score: text similarity weighted higher, but geography can confirm
        # If both are similar → definitely duplicates
        # If text similar but no geo → might be duplicate
        # If geo similar but text different → probably different events at same place
        
        if text_sim >= self.similarity_threshold:
            # High text similarity - likely duplicate
            return True, text_sim
        elif geo_sim >= 0.8 and text_sim >= 0.6:
            # Very close location + moderate text similarity → duplicate
            return True, (text_sim + geo_sim) / 2
        else:
            return False, text_sim
    
    def find_duplicates(self, events: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Find duplicate events in a list
        
        Returns a mapping of original event IDs to their duplicate IDs
        
        Args:
            events: List of event dictionaries
        
        Returns:
            Dictionary: {original_event_id: [duplicate_event_ids]}
        """
        if len(events) < 2:
            return {}
        
        duplicates = {}
        processed: Set[str] = set()
        
        logger.info(f"Checking {len(events)} events for duplicates...")
        
        for i, event1 in enumerate(events):
            event1_id = event1.get('id')
            
            # Skip if already marked as duplicate
            if event1_id in processed:
                continue
            
            duplicate_ids = []
            
            # Compare with all subsequent events
            for j in range(i + 1, len(events)):
                event2 = events[j]
                event2_id = event2.get('id')
                
                # Skip if already processed
                if event2_id in processed:
                    continue
                
                # Check similarity
                is_similar, score = self.are_events_similar(event1, event2)
                
                if is_similar:
                    duplicate_ids.append(event2_id)
                    processed.add(event2_id)
                    logger.debug(f"Found duplicate: {event1_id} ≈ {event2_id} (score: {score:.2f})")
            
            if duplicate_ids:
                duplicates[event1_id] = duplicate_ids
        
        total_dupes = sum(len(v) for v in duplicates.values())
        logger.info(f"Found {len(duplicates)} groups with {total_dupes} duplicate events")
        
        return duplicates
    
    def mark_duplicates(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mark duplicate events in the list
        
        Keeps the first occurrence, marks others as duplicates
        
        Args:
            events: List of events
        
        Returns:
            List of events with duplicate markings
        """
        duplicates = self.find_duplicates(events)
        
        # Create lookup for duplicates
        duplicate_of = {}
        for original_id, dupe_ids in duplicates.items():
            for dupe_id in dupe_ids:
                duplicate_of[dupe_id] = original_id
        
        # Mark events
        marked_events = []
        for event in events:
            event_id = event.get('id')
            
            if event_id in duplicate_of:
                # This is a duplicate
                event['duplicate_of'] = duplicate_of[event_id]
                event['is_duplicate'] = True
            else:
                # Original or unique event
                event['duplicate_of'] = None
                event['is_duplicate'] = False
                
                # Add list of similar events if this is an original
                if event_id in duplicates:
                    event['similar_events'] = duplicates[event_id]
                else:
                    event['similar_events'] = []
            
            marked_events.append(event)
        
        return marked_events
    
    def remove_duplicates(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate events, keeping only originals
        
        Args:
            events: List of events
        
        Returns:
            List with duplicates removed
        """
        marked = self.mark_duplicates(events)
        
        # Keep only non-duplicates
        unique = [e for e in marked if not e.get('is_duplicate', False)]
        
        removed_count = len(events) - len(unique)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate events")
        
        return unique


def main():
    """Test the deduplicator"""
    print("\n" + "="*60)
    print("🔍 Event Deduplicator Test")
    print("="*60 + "\n")
    
    # Sample events with duplicates
    sample_events = [
        {
            'id': 'event1',
            'type': 'traffic',
            'description': 'Heavy traffic jam on MG Road near Trinity Circle',
            'location': 'MG Road',
            'coordinates': {'lat': 12.9760, 'lon': 77.6061},
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'id': 'event2',
            'type': 'traffic',
            'description': 'Traffic congestion at MG Road Trinity Circle',
            'location': 'MG Road',
            'coordinates': {'lat': 12.9765, 'lon': 77.6065},
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'id': 'event3',
            'type': 'civic',
            'description': 'Power outage in Koramangala 5th Block',
            'location': 'Koramangala',
            'coordinates': {'lat': 12.9352, 'lon': 77.6245},
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'id': 'event4',
            'type': 'traffic',
            'description': 'Major traffic jam on Silk Board flyover',
            'location': 'Silk Board',
            'coordinates': {'lat': 12.9173, 'lon': 77.6221},
            'timestamp': datetime.utcnow().isoformat()
        }
    ]
    
    deduplicator = EventDeduplicator()
    
    # Find duplicates
    print("Finding duplicates...\n")
    duplicates = deduplicator.find_duplicates(sample_events)
    
    print(f"Found {len(duplicates)} duplicate groups:\n")
    for original, dupes in duplicates.items():
        print(f"Original: {original}")
        print(f"Duplicates: {dupes}\n")
    
    # Remove duplicates
    unique_events = deduplicator.remove_duplicates(sample_events)
    print(f"\nOriginal events: {len(sample_events)}")
    print(f"Unique events: {len(unique_events)}")
    print(f"Removed: {len(sample_events) - len(unique_events)}")


if __name__ == "__main__":
    main()
