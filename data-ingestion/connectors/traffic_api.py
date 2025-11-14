"""
Traffic API Connector
Fetches real-time traffic data from Google Maps and other traffic sources
"""
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import googlemaps
from tenacity import retry, stop_after_attempt, wait_exponential

from config import Config
from utils import setup_logger, Event, Coordinates

logger = setup_logger(__name__)


class TrafficAPIConnector:
    """
    Connector for traffic data sources
    - Google Maps Traffic API
    - Road closures
    - Public transport delays
    """
    
    def __init__(self):
        self.api_key = Config.GOOGLE_MAPS_API_KEY
        self.gmaps_client = None
        
        if self.api_key:
            try:
                self.gmaps_client = googlemaps.Client(key=self.api_key)
                logger.info("✓ Google Maps client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
        else:
            logger.warning("⚠️  Google Maps API key not configured")
        
        # Key traffic areas in Bangalore
        self.monitored_areas = [
            {"name": "MG Road", "lat": 12.9760, "lon": 77.6061},
            {"name": "Koramangala", "lat": 12.9352, "lon": 77.6245},
            {"name": "Whitefield", "lat": 12.9698, "lon": 77.7500},
            {"name": "Electronic City", "lat": 12.8456, "lon": 77.6603},
            {"name": "Indiranagar", "lat": 12.9716, "lon": 77.6412},
            {"name": "HSR Layout", "lat": 12.9121, "lon": 77.6446},
            {"name": "Jayanagar", "lat": 12.9250, "lon": 77.5838},
            {"name": "Malleshwaram", "lat": 13.0031, "lon": 77.5697},
            {"name": "Hebbal", "lat": 13.0358, "lon": 77.5970},
            {"name": "Silk Board", "lat": 12.9173, "lon": 77.6221},
        ]
        
        # Major routes to monitor
        self.routes = [
            {
                "name": "Airport to MG Road",
                "origin": (13.1986, 77.7066),
                "destination": (12.9760, 77.6061)
            },
            {
                "name": "Whitefield to Koramangala",
                "origin": (12.9698, 77.7500),
                "destination": (12.9352, 77.6245)
            },
            {
                "name": "Electronic City to Silk Board",
                "origin": (12.8456, 77.6603),
                "destination": (12.9173, 77.6221)
            }
        ]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_traffic_conditions(self) -> List[Event]:
        """
        Fetch current traffic conditions for monitored areas
        
        Returns:
            List of Event objects containing traffic information
        """
        events = []
        
        if not self.gmaps_client:
            logger.warning("Google Maps client not available, returning mock data")
            return self._get_mock_traffic_data()
        
        try:
            # Check traffic on major routes
            for route in self.routes:
                try:
                    directions = self.gmaps_client.directions(
                        origin=route["origin"],
                        destination=route["destination"],
                        mode="driving",
                        departure_time="now",
                        traffic_model="best_guess"
                    )
                    
                    if directions:
                        leg = directions[0]['legs'][0]
                        duration = leg['duration']['value']
                        duration_in_traffic = leg.get('duration_in_traffic', {}).get('value', duration)
                        
                        # Calculate delay
                        delay_seconds = duration_in_traffic - duration
                        delay_minutes = delay_seconds / 60
                        
                        # Only create event if significant delay
                        if delay_minutes > 10:
                            severity = self._calculate_severity(delay_minutes)
                            
                            event = Event(
                                type="traffic",
                                source="google_maps",
                                description=f"Heavy traffic on {route['name']}: {int(delay_minutes)} min delay. "
                                           f"Current travel time: {leg['duration_in_traffic']['text']}",
                                location=route['name'],
                                coordinates=Coordinates(
                                    lat=(route['origin'][0] + route['destination'][0]) / 2,
                                    lon=(route['origin'][1] + route['destination'][1]) / 2
                                ),
                                severity=severity,
                                tags=["traffic", "delay", "route"],
                                raw_data={
                                    "delay_minutes": delay_minutes,
                                    "normal_duration": leg['duration']['text'],
                                    "current_duration": leg['duration_in_traffic']['text'],
                                    "distance": leg['distance']['text']
                                }
                            )
                            events.append(event)
                            logger.info(f"Traffic event: {route['name']} - {int(delay_minutes)} min delay")
                
                except Exception as e:
                    logger.error(f"Error fetching traffic for {route['name']}: {e}")
                    continue
                
                # Rate limiting - don't overwhelm API
                time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error in get_traffic_conditions: {e}")
        
        logger.info(f"Collected {len(events)} traffic events")
        return events
    
    def _calculate_severity(self, delay_minutes: float) -> str:
        """Calculate severity based on delay"""
        if delay_minutes < 15:
            return "low"
        elif delay_minutes < 30:
            return "medium"
        elif delay_minutes < 60:
            return "high"
        else:
            return "critical"
    
    def _get_mock_traffic_data(self) -> List[Event]:
        """
        Generate mock traffic data for testing without API keys
        Useful for development and testing
        """
        logger.info("Generating mock traffic data")
        
        mock_events = [
            Event(
                type="traffic",
                source="google_maps",
                description="Heavy traffic on Outer Ring Road near Silk Board due to accident. Current travel time: 45 minutes (normal: 12 minutes)",
                location="Silk Board Junction, Bangalore",
                coordinates=Coordinates(lat=12.9173, lon=77.6221),
                severity="critical",
                tags=["traffic", "accident", "silkboard", "delay"],
                raw_data={
                    "mock": True, 
                    "delay_minutes": 33,
                    "normal_duration": "12 mins",
                    "current_duration": "45 mins",
                    "distance": "8.5 km"
                }
            ),
            Event(
                type="traffic",
                source="google_maps",
                description="Moderate congestion on Hosur Road near Electronic City. Expected delay: 15 minutes due to lane closure.",
                location="Hosur Road, Electronic City",
                coordinates=Coordinates(lat=12.8456, lon=77.6603),
                severity="medium",
                tags=["traffic", "congestion", "construction"],
                raw_data={
                    "mock": True,
                    "delay_minutes": 15,
                    "normal_duration": "18 mins",
                    "current_duration": "33 mins",
                    "distance": "12.3 km"
                }
            ),
            Event(
                type="traffic",
                source="google_maps",
                description="Slow moving traffic on Whitefield Main Road towards Marathahalli. Travel time: 28 mins (normal: 15 mins)",
                location="Whitefield to Marathahalli",
                coordinates=Coordinates(lat=12.9645, lon=77.7236),
                severity="medium",
                tags=["traffic", "congestion", "whitefield"],
                raw_data={
                    "mock": True,
                    "delay_minutes": 13,
                    "normal_duration": "15 mins",
                    "current_duration": "28 mins",
                    "distance": "9.2 km"
                }
            ),
            Event(
                type="traffic",
                source="google_maps",
                description="Heavy congestion at Hebbal flyover due to metro construction. Current travel time: 35 minutes (normal: 8 minutes)",
                location="Hebbal Flyover, Bangalore",
                coordinates=Coordinates(lat=13.0358, lon=77.5970),
                severity="high",
                tags=["traffic", "construction", "hebbal", "metro"],
                raw_data={
                    "mock": True,
                    "delay_minutes": 27,
                    "normal_duration": "8 mins",
                    "current_duration": "35 mins",
                    "distance": "5.8 km"
                }
            ),
            Event(
                type="traffic",
                source="google_maps",
                description="Traffic buildup on Old Airport Road near HAL. Current travel time: 22 mins (normal: 10 mins)",
                location="Old Airport Road, HAL",
                coordinates=Coordinates(lat=12.9539, lon=77.6646),
                severity="medium",
                tags=["traffic", "congestion"],
                raw_data={
                    "mock": True,
                    "delay_minutes": 12,
                    "normal_duration": "10 mins",
                    "current_duration": "22 mins",
                    "distance": "7.1 km"
                }
            ),
            Event(
                type="traffic",
                source="google_maps",
                description="Smooth traffic on ORR from Bellandur to Sarjapur. Travel time: 16 mins (normal: 14 mins)",
                location="ORR Bellandur to Sarjapur",
                coordinates=Coordinates(lat=12.9259, lon=77.6766),
                severity="low",
                tags=["traffic", "smooth", "ORR"],
                raw_data={
                    "mock": True,
                    "delay_minutes": 2,
                    "normal_duration": "14 mins",
                    "current_duration": "16 mins",
                    "distance": "11.4 km"
                }
            )
        ]
        
        return mock_events
    
    def test_connection(self) -> bool:
        """Test if API connection is working"""
        if not self.gmaps_client:
            logger.warning("API key not configured")
            return False
        
        try:
            # Simple geocode test
            result = self.gmaps_client.geocode("Bangalore, India")
            if result:
                logger.info("✓ Google Maps API connection successful")
                return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
        
        return False


def main():
    """Test the traffic connector"""
    print("\n" + "="*60)
    print("🚗 Traffic API Connector Test")
    print("="*60 + "\n")
    
    connector = TrafficAPIConnector()
    
    # Test connection
    if connector.test_connection():
        print("✓ API connection successful\n")
    else:
        print("⚠️  Using mock data (API not configured)\n")
    
    # Fetch traffic events
    print("Fetching traffic conditions...\n")
    events = connector.get_traffic_conditions()
    
    print(f"\n📊 Found {len(events)} traffic events:\n")
    for i, event in enumerate(events, 1):
        print(f"{i}. [{event.severity.upper()}] {event.description}")
        print(f"   Location: {event.location}")
        print(f"   Time: {event.timestamp.strftime('%H:%M:%S')}")
        print()


if __name__ == "__main__":
    main()
