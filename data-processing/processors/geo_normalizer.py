"""
Geo-Normalizer
Converts addresses to coordinates and maps events to city zones

EXPLANATION:
Person 1 sends locations in various formats:
- "MG Road, Bangalore"
- "Near Cubbon Park"
- "Koramangala"
- Just coordinates: (12.9716, 77.5946)

This module:
1. Converts text addresses → precise lat/lon coordinates (Geocoding)
2. Converts coordinates → full addresses (Reverse Geocoding)
3. Maps coordinates → city zones (North/South/East/West/Central Bangalore)
4. Identifies neighborhoods (Koramangala, Whitefield, etc.)

WHY THIS MATTERS:
- Frontend can display events on a map
- AI/ML can cluster events by location
- Users can search "Show me events in Koramangala"
- Consistent location data across all events

"""
from typing import Dict, Any, Optional, Tuple, List
import time
from functools import lru_cache

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False

from config import Config
from utils import setup_logger, DataValidator

logger = setup_logger(__name__)


class GeoNormalizer:
    """
    Geocoding and zone mapping for events
    
    Features:
    - Convert addresses to coordinates
    - Convert coordinates to addresses
    - Map to Bangalore zones
    - Identify neighborhoods
    - Caching for performance
    """
    
    def __init__(self):
        """Initialize geocoding clients"""
        self.google_client = None
        self.nominatim_client = None
        self.cache_enabled = Config.ENABLE_CACHING
        
        # Initialize Google Maps client
        if Config.GOOGLE_MAPS_API_KEY and GOOGLEMAPS_AVAILABLE:
            try:
                self.google_client = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
                logger.info("✓ Google Maps geocoding initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps: {e}")
        
        # Initialize Nominatim (free, no API key needed)
        if GEOPY_AVAILABLE:
            try:
                self.nominatim_client = Nominatim(user_agent="smartcitysense_ai")
                logger.info("✓ Nominatim geocoding initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Nominatim: {e}")
        
        if not self.google_client and not self.nominatim_client:
            logger.warning("⚠️  No geocoding service available, using mock data")
    
    @lru_cache(maxsize=1000)
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates (with caching)
        
        Args:
            address: Address string
        
        Returns:
            (lat, lon) tuple or None
        """
        if not address:
            return None
        
        # Add "Bangalore" if not present for better results
        if 'bangalore' not in address.lower() and 'bengaluru' not in address.lower():
            address = f"{address}, Bangalore, India"
        
        # Try Google Maps first (more accurate for India)
        if self.google_client:
            try:
                result = self.google_client.geocode(address)
                if result and len(result) > 0:
                    location = result[0]['geometry']['location']
                    lat, lon = location['lat'], location['lng']
                    
                    # Validate coordinates
                    if DataValidator.validate_coordinates(lat, lon):
                        logger.debug(f"Geocoded: {address} → ({lat}, {lon})")
                        return (lat, lon)
                    else:
                        logger.warning(f"Coordinates outside Bangalore: {address}")
                        return None
            
            except Exception as e:
                logger.warning(f"Google Maps geocoding failed: {e}")
        
        # Fallback to Nominatim
        if self.nominatim_client:
            try:
                time.sleep(1)  # Rate limiting for Nominatim
                location = self.nominatim_client.geocode(address)
                
                if location:
                    lat, lon = location.latitude, location.longitude
                    
                    if DataValidator.validate_coordinates(lat, lon):
                        logger.debug(f"Geocoded (Nominatim): {address} → ({lat}, {lon})")
                        return (lat, lon)
            
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logger.warning(f"Nominatim geocoding failed: {e}")
            except Exception as e:
                logger.error(f"Geocoding error: {e}")
        
        logger.warning(f"Could not geocode: {address}")
        return None
    
    @lru_cache(maxsize=500)
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to address (with caching)
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Address string or None
        """
        # Validate coordinates
        if not DataValidator.validate_coordinates(lat, lon):
            return None
        
        # Try Google Maps first
        if self.google_client:
            try:
                result = self.google_client.reverse_geocode((lat, lon))
                if result and len(result) > 0:
                    address = result[0]['formatted_address']
                    logger.debug(f"Reverse geocoded: ({lat}, {lon}) → {address}")
                    return address
            except Exception as e:
                logger.warning(f"Google Maps reverse geocoding failed: {e}")
        
        # Fallback to Nominatim
        if self.nominatim_client:
            try:
                time.sleep(1)  # Rate limiting
                location = self.nominatim_client.reverse((lat, lon))
                
                if location:
                    address = location.address
                    logger.debug(f"Reverse geocoded (Nominatim): ({lat}, {lon}) → {address}")
                    return address
            
            except Exception as e:
                logger.warning(f"Nominatim reverse geocoding failed: {e}")
        
        return None
    
    def find_zone(self, lat: float, lon: float) -> Optional[str]:
        """
        Map coordinates to Bangalore zone
        
        Zones: North, South, East, West, Central Bangalore
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Zone name or None
        """
        if not DataValidator.validate_coordinates(lat, lon):
            return None
        
        # Find closest zone by comparing to zone centers
        min_distance = float('inf')
        closest_zone = None
        
        from processors.deduplicator import EventDeduplicator
        deduplicator = EventDeduplicator()
        
        for zone_name, zone_info in Config.BANGALORE_ZONES.items():
            zone_lat, zone_lon = zone_info['center']
            distance = deduplicator.calculate_distance(lat, lon, zone_lat, zone_lon)
            
            if distance < min_distance:
                min_distance = distance
                closest_zone = zone_name
        
        return closest_zone
    
    def find_neighborhood(self, lat: float, lon: float, address: str = None) -> Optional[str]:
        """
        Identify neighborhood from coordinates or address
        
        Args:
            lat: Latitude
            lon: Longitude
            address: Optional address string
        
        Returns:
            Neighborhood name or None
        """
        # First try to extract from address
        if address:
            address_lower = address.lower()
            
            # Check all known neighborhoods
            for zone_info in Config.BANGALORE_ZONES.values():
                for neighborhood in zone_info['neighborhoods']:
                    if neighborhood.lower() in address_lower:
                        return neighborhood
        
        # If no match in address, try by proximity to known neighborhoods
        # (This is simplified - in production, you'd use more sophisticated methods)
        if DataValidator.validate_coordinates(lat, lon):
            # For now, return the zone as neighborhood if no specific match
            return self.find_zone(lat, lon)
        
        return None
    
    def normalize_event_location(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize location data for an event
        
        This is the main method that enhances an event with geo data:
        - If has address but no coords → geocode to get coords
        - If has coords but no address → reverse geocode to get address
        - Add zone and neighborhood
        
        Args:
            event: Event dictionary
        
        Returns:
            Enhanced event with normalized location data
        """
        location = event.get('location', '')
        coords = event.get('coordinates')
        
        # Extract lat/lon if coordinates exist
        lat, lon = None, None
        if coords:
            lat = coords.get('lat')
            lon = coords.get('lon')
        
        # Case 1: Has address but no coordinates → Geocode
        if location and not (lat and lon):
            logger.debug(f"Geocoding address: {location}")
            result = self.geocode_address(location)
            
            if result:
                lat, lon = result
                event['coordinates'] = {'lat': lat, 'lon': lon}
                logger.info(f"✓ Geocoded: {location} → ({lat:.4f}, {lon:.4f})")
            else:
                logger.warning(f"Could not geocode: {location}")
        
        # Case 2: Has coordinates but no detailed address → Reverse geocode
        if lat and lon:
            # Validate coordinates
            if not DataValidator.validate_coordinates(lat, lon):
                logger.warning(f"Invalid coordinates: ({lat}, {lon})")
                return event
            
            # Get full address if not present
            if not event.get('full_address'):
                address = self.reverse_geocode(lat, lon)
                if address:
                    event['full_address'] = address
            
            # Add zone
            zone = self.find_zone(lat, lon)
            if zone:
                event['zone'] = zone
                logger.debug(f"Mapped to zone: {zone}")
            
            # Add neighborhood
            neighborhood = self.find_neighborhood(
                lat, lon, 
                event.get('full_address', '') or location
            )
            if neighborhood:
                event['neighborhood'] = neighborhood
                logger.debug(f"Identified neighborhood: {neighborhood}")
        
        return event
    
    def batch_normalize(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize location data for multiple events
        
        Args:
            events: List of events
        
        Returns:
            List of enhanced events
        """
        logger.info(f"Normalizing locations for {len(events)} events...")
        
        normalized = []
        success_count = 0
        
        for event in events:
            try:
                normalized_event = self.normalize_event_location(event)
                normalized.append(normalized_event)
                
                # Count as success if we added coordinates or zone
                if normalized_event.get('coordinates') or normalized_event.get('zone'):
                    success_count += 1
            
            except Exception as e:
                logger.error(f"Error normalizing event {event.get('id')}: {e}")
                normalized.append(event)  # Keep original
        
        logger.info(f"✓ Successfully normalized {success_count}/{len(events)} events")
        
        return normalized


def main():
    """Test geo-normalizer"""
    print("\n" + "="*60)
    print("🗺️  Geo-Normalizer Test")
    print("="*60 + "\n")
    
    normalizer = GeoNormalizer()
    
    # Test geocoding
    print("Testing geocoding...\n")
    addresses = [
        "MG Road, Bangalore",
        "Koramangala, Bangalore",
        "Whitefield, Bangalore"
    ]
    
    for address in addresses:
        coords = normalizer.geocode_address(address)
        if coords:
            print(f"✓ {address}")
            print(f"  → ({coords[0]:.4f}, {coords[1]:.4f})")
            
            # Test zone mapping
            zone = normalizer.find_zone(coords[0], coords[1])
            print(f"  → Zone: {zone}")
        else:
            print(f"✗ Could not geocode: {address}")
        print()
    
    # Test event normalization
    print("\nTesting event normalization...\n")
    sample_event = {
        'id': 'test1',
        'type': 'traffic',
        'description': 'Traffic jam',
        'location': 'Silk Board, Bangalore',
    }
    
    normalized = normalizer.normalize_event_location(sample_event)
    print("Original event:")
    print(f"  Location: {sample_event['location']}")
    print("\nNormalized event:")
    if normalized.get('coordinates'):
        print(f"  Coordinates: {normalized['coordinates']}")
    if normalized.get('zone'):
        print(f"  Zone: {normalized['zone']}")
    if normalized.get('neighborhood'):
        print(f"  Neighborhood: {normalized['neighborhood']}")


if __name__ == "__main__":
    main()
