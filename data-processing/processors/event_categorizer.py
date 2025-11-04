"""
Event Categorizer
Refines event types and adds detailed tags

EXPLANATION:
Person 1 provides basic categorization:
- type: "traffic"
- tags: ["traffic"]

This is too generic! We need more detail for the AI/ML and frontend.

This module adds:
1. Subtype: traffic_congestion, traffic_accident, traffic_road_closure
2. Context tags: rush_hour, weather_related, government, urgent
3. Urgency classification: can_wait, needs_attention, critical
4. Enhanced tagging based on content analysis

EXAMPLE:
Input: type="traffic", description="Accident on MG Road blocking two lanes"
Output: 
  type="traffic"
  subtype="traffic_accident"
  urgency="critical"
  tags=["traffic", "accident", "mgroad", "urgent", "road_block"]

"""
from typing import Dict, Any, List, Set, Optional
import re
from datetime import datetime

from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


class EventCategorizer:
    """
    Refines event categorization and adds detailed tags
    
    Features:
    - Determine event subtype
    - Extract relevant tags from description
    - Classify urgency
    - Add context tags (time-based, weather-related, etc.)
    """
    
    def __init__(self):
        """Initialize categorizer with keyword mappings"""
        self.type_mapping = Config.EVENT_TYPE_MAPPING
        self.tag_keywords = Config.TAG_KEYWORDS
        
        logger.info("Event categorizer initialized")
    
    def determine_subtype(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Determine specific subtype based on event type and description
        
        Args:
            event: Event dictionary
        
        Returns:
            Subtype string or None
        """
        event_type = event.get('type', '')
        description = event.get('description', '').lower()
        
        # Get subtypes for this event type
        if event_type not in self.type_mapping:
            return None
        
        subtypes = self.type_mapping[event_type]
        
        # Check keywords for each subtype
        for subtype, keywords in subtypes.items():
            for keyword in keywords:
                if keyword.lower() in description:
                    full_subtype = f"{event_type}_{subtype}"
                    logger.debug(f"Determined subtype: {full_subtype}")
                    return full_subtype
        
        return None
    
    def extract_tags(self, event: Dict[str, Any]) -> List[str]:
        """
        Extract relevant tags from event description
        
        Looks for:
        - Location names
        - Event-specific keywords
        - Context indicators
        
        Args:
            event: Event dictionary
        
        Returns:
            List of tags
        """
        tags = set(event.get('tags', []))  # Start with existing tags
        
        description = event.get('description', '').lower()
        event_type = event.get('type', '')
        
        # Add event type as tag
        if event_type:
            tags.add(event_type)
        
        # Add subtype if present
        subtype = event.get('subtype')
        if subtype:
            tags.add(subtype.split('_')[-1])  # e.g., "traffic_accident" → "accident"
        
        # Extract context tags
        for context, keywords in self.tag_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description:
                    tags.add(context)
                    break
        
        # Add zone and neighborhood as tags
        if event.get('zone'):
            zone_tag = event['zone'].lower().replace(' ', '_')
            tags.add(zone_tag)
        
        if event.get('neighborhood'):
            neighborhood_tag = event['neighborhood'].lower().replace(' ', '_')
            tags.add(neighborhood_tag)
        
        # Extract location-specific tags
        # Look for common Bangalore location patterns
        bangalore_locations = [
            'mg road', 'koramangala', 'whitefield', 'indiranagar', 
            'jayanagar', 'silk board', 'hebbal', 'electronic city',
            'marathahalli', 'bellandur', 'hsr layout', 'btm'
        ]
        
        for location in bangalore_locations:
            if location in description:
                location_tag = location.replace(' ', '_')
                tags.add(location_tag)
        
        # Add source as tag
        source = event.get('source')
        if source:
            tags.add(source)
        
        return list(tags)
    
    def classify_urgency(self, event: Dict[str, Any]) -> str:
        """
        Classify event urgency level
        
        Levels:
        - can_wait: Low priority, informational
        - needs_attention: Medium priority, should be addressed
        - critical: High priority, immediate action needed
        - resolved: Event is resolved/completed
        
        Args:
            event: Event dictionary
        
        Returns:
            Urgency level string
        """
        description = event.get('description', '').lower()
        severity = event.get('severity', 'medium').lower()
        event_type = event.get('type', '')
        subtype = event.get('subtype', '')
        
        # Check for resolved indicators
        resolved_keywords = ['resolved', 'cleared', 'fixed', 'completed', 'over']
        if any(keyword in description for keyword in resolved_keywords):
            return 'resolved'
        
        # Critical keywords
        critical_keywords = [
            'emergency', 'urgent', 'critical', 'fire', 'accident', 
            'medical', 'ambulance', 'serious', 'major', 'severe'
        ]
        if any(keyword in description for keyword in critical_keywords):
            return 'critical'
        
        # Emergency events are always critical
        if event_type == 'emergency':
            return 'critical'
        
        # High severity accidents are critical
        if 'accident' in subtype and severity in ['high', 'critical']:
            return 'critical'
        
        # Needs attention keywords
        attention_keywords = [
            'blocked', 'closure', 'jam', 'heavy', 'outage', 
            'shortage', 'flooding', 'problem'
        ]
        if any(keyword in description for keyword in attention_keywords):
            return 'needs_attention'
        
        # High severity needs attention
        if severity in ['high', 'critical']:
            return 'needs_attention'
        
        # Default based on severity
        if severity == 'medium':
            return 'needs_attention'
        else:
            return 'can_wait'
    
    def add_time_context(self, event: Dict[str, Any]) -> List[str]:
        """
        Add time-based context tags
        
        Args:
            event: Event dictionary
        
        Returns:
            List of time-based tags
        """
        time_tags = []
        
        timestamp = event.get('timestamp')
        if not timestamp:
            return time_tags
        
        try:
            # Parse timestamp
            if isinstance(timestamp, str):
                event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                event_time = timestamp
            
            # Get hour
            hour = event_time.hour
            day_of_week = event_time.weekday()  # 0 = Monday, 6 = Sunday
            
            # Morning rush hour (7 AM - 10 AM)
            if 7 <= hour < 10 and day_of_week < 5:  # Weekdays
                time_tags.append('morning_rush_hour')
            
            # Evening rush hour (5 PM - 9 PM)
            elif 17 <= hour < 21 and day_of_week < 5:
                time_tags.append('evening_rush_hour')
            
            # Weekend
            if day_of_week >= 5:
                time_tags.append('weekend')
            else:
                time_tags.append('weekday')
            
            # Night time (10 PM - 6 AM)
            if hour >= 22 or hour < 6:
                time_tags.append('night_time')
        
        except Exception as e:
            logger.warning(f"Error adding time context: {e}")
        
        return time_tags
    
    def categorize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method: Categorize and enhance an event
        
        Args:
            event: Event dictionary
        
        Returns:
            Enhanced event with categorization
        """
        # Determine subtype
        subtype = self.determine_subtype(event)
        if subtype:
            event['subtype'] = subtype
        
        # Extract and enhance tags
        tags = self.extract_tags(event)
        
        # Add time context
        time_tags = self.add_time_context(event)
        tags.extend(time_tags)
        
        # Remove duplicates and update
        event['tags'] = list(set(tags))
        
        # Classify urgency
        urgency = self.classify_urgency(event)
        event['urgency'] = urgency
        
        logger.debug(f"Categorized event {event.get('id')}: subtype={subtype}, urgency={urgency}, tags={len(tags)}")
        
        return event
    
    def batch_categorize(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize multiple events
        
        Args:
            events: List of events
        
        Returns:
            List of categorized events
        """
        logger.info(f"Categorizing {len(events)} events...")
        
        categorized = []
        for event in events:
            try:
                categorized_event = self.categorize_event(event)
                categorized.append(categorized_event)
            except Exception as e:
                logger.error(f"Error categorizing event {event.get('id')}: {e}")
                categorized.append(event)  # Keep original
        
        logger.info(f"✓ Categorized {len(categorized)} events")
        return categorized


def main():
    """Test event categorizer"""
    print("\n" + "="*60)
    print("🏷️  Event Categorizer Test")
    print("="*60 + "\n")
    
    categorizer = EventCategorizer()
    
    # Test events
    sample_events = [
        {
            'id': 'event1',
            'type': 'traffic',
            'description': 'Major accident on MG Road blocking two lanes. Avoid the area!',
            'location': 'MG Road',
            'severity': 'critical',
            'timestamp': datetime.now().isoformat(),
            'tags': ['traffic']
        },
        {
            'id': 'event2',
            'type': 'civic',
            'description': 'Power outage reported in Koramangala 5th Block by BESCOM',
            'location': 'Koramangala',
            'severity': 'high',
            'timestamp': datetime.now().isoformat(),
            'tags': ['civic']
        },
        {
            'id': 'event3',
            'type': 'traffic',
            'description': 'Traffic cleared on Silk Board. Situation back to normal.',
            'location': 'Silk Board',
            'severity': 'low',
            'timestamp': datetime.now().isoformat(),
            'tags': ['traffic']
        }
    ]
    
    print("Categorizing events...\n")
    
    for event in sample_events:
        print(f"Event: {event['id']}")
        print(f"Original: type={event['type']}, tags={event['tags']}")
        
        categorized = categorizer.categorize_event(event)
        
        print(f"Enhanced:")
        if categorized.get('subtype'):
            print(f"  Subtype: {categorized['subtype']}")
        print(f"  Urgency: {categorized['urgency']}")
        print(f"  Tags: {categorized['tags']}")
        print()


if __name__ == "__main__":
    main()
