"""
Civic Portal API Connector
Fetches civic issues, complaints, and government announcements
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config import Config
from utils import setup_logger, Event, Coordinates

logger = setup_logger(__name__)


class CivicPortalConnector:
    """
    Connector for civic data sources:
    - BBMP (Bangalore Municipal Corporation) complaints
    - Government civic portals
    - Infrastructure updates
    - Public announcements
    """
    
    def __init__(self):
        self.api_key = Config.CIVIC_PORTAL_API_KEY
        self.base_url = Config.CIVIC_PORTAL_BASE_URL
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            logger.info("✓ Civic Portal API configured")
        else:
            logger.warning("⚠️  Civic Portal API key not configured")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_civic_complaints(self) -> List[Event]:
        """
        Fetch recent civic complaints and issues
        
        Returns:
            List of Event objects containing civic issues
        """
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("API key not configured, returning mock data")
            return self._get_mock_civic_data()
        
        events = []
        
        try:
            # Example endpoint - adjust based on actual API
            response = self.session.get(
                f"{self.base_url}/complaints",
                params={
                    "status": "open",
                    "limit": 50,
                    "city": "bangalore"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("complaints", []):
                    event = self._parse_complaint(item)
                    if event:
                        events.append(event)
                
                logger.info(f"Fetched {len(events)} civic complaints")
            else:
                logger.error(f"API request failed with status {response.status_code}")
                # Return mock data on error
                return self._get_mock_civic_data()
        
        except requests.exceptions.Timeout:
            logger.error("API request timed out, returning mock data")
            return self._get_mock_civic_data()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}, returning mock data")
            return self._get_mock_civic_data()
        except Exception as e:
            logger.error(f"Error fetching civic complaints: {e}, returning mock data")
            return self._get_mock_civic_data()
        
        return events
    
    def _parse_complaint(self, complaint_data: Dict[str, Any]) -> Optional[Event]:
        """Parse complaint data into Event object"""
        try:
            # Determine event type based on category
            category = complaint_data.get("category", "").lower()
            event_type = self._categorize_complaint(category)
            
            # Determine severity
            priority = complaint_data.get("priority", "low").lower()
            severity_map = {
                "low": "low",
                "medium": "medium",
                "high": "high",
                "critical": "critical"
            }
            severity = severity_map.get(priority, "medium")
            
            # Extract location
            location = complaint_data.get("location", "Bangalore")
            coords = None
            if "latitude" in complaint_data and "longitude" in complaint_data:
                coords = Coordinates(
                    lat=float(complaint_data["latitude"]),
                    lon=float(complaint_data["longitude"])
                )
            
            event = Event(
                type=event_type,
                source="civic_portal",
                description=complaint_data.get("description", "Civic complaint"),
                location=location,
                coordinates=coords,
                severity=severity,
                tags=[category, "civic", "complaint"],
                raw_data=complaint_data
            )
            
            return event
        
        except Exception as e:
            logger.error(f"Error parsing complaint: {e}")
            return None
    
    def _categorize_complaint(self, category: str) -> str:
        """Map complaint category to event type"""
        civic_keywords = ["water", "electricity", "power", "garbage", "pothole", "drainage", "street"]
        emergency_keywords = ["fire", "accident", "medical", "urgent"]
        
        category_lower = category.lower()
        
        if any(keyword in category_lower for keyword in emergency_keywords):
            return "emergency"
        elif any(keyword in category_lower for keyword in civic_keywords):
            return "civic"
        else:
            return "other"
    
    def _get_mock_civic_data(self) -> List[Event]:
        """Generate mock civic data for testing"""
        logger.info("Generating mock civic data")
        
        mock_events = [
            Event(
                type="civic",
                source="civic_portal",
                description="Power outage reported in Koramangala 5th Block, affecting 200+ households. BESCOM teams dispatched.",
                location="Koramangala 5th Block, Bangalore",
                coordinates=Coordinates(lat=12.9352, lon=77.6245),
                severity="high",
                tags=["power", "outage", "BESCOM", "civic"],
                raw_data={"mock": True, "affected_count": 200, "complaint_id": "BESCOM-2025-10-07-001"}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Water supply disruption on Whitefield Main Road due to pipeline maintenance. Expected restoration by 8 PM.",
                location="Whitefield Main Road",
                coordinates=Coordinates(lat=12.9698, lon=77.7500),
                severity="medium",
                tags=["water", "maintenance", "civic", "BWSSB"],
                raw_data={"mock": True, "complaint_id": "BWSSB-2025-10-07-045"}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Multiple potholes reported on Old Airport Road causing traffic slowdown. BBMP has marked for urgent repair.",
                location="Old Airport Road, Bangalore",
                coordinates=Coordinates(lat=12.9539, lon=77.6646),
                severity="medium",
                tags=["pothole", "road", "civic", "BBMP"],
                raw_data={"mock": True, "complaint_id": "BBMP-2025-10-07-123", "pothole_count": 7}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Garbage not collected in HSR Layout Sector 2 for past 3 days. Sanitation vehicle breakdown reported.",
                location="HSR Layout Sector 2",
                coordinates=Coordinates(lat=12.9121, lon=77.6446),
                severity="low",
                tags=["garbage", "waste", "civic", "sanitation"],
                raw_data={"mock": True, "complaint_id": "BBMP-2025-10-07-089"}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Street light failure on 100 Feet Road Indiranagar. 15 lights non-functional for safety concern.",
                location="100 Feet Road, Indiranagar",
                coordinates=Coordinates(lat=12.9716, lon=77.6412),
                severity="medium",
                tags=["streetlight", "safety", "civic", "BESCOM"],
                raw_data={"mock": True, "complaint_id": "BESCOM-2025-10-07-078", "lights_affected": 15}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Drainage overflow near Jayanagar 4th Block metro station causing waterlogging.",
                location="Jayanagar 4th Block",
                coordinates=Coordinates(lat=12.9250, lon=77.5838),
                severity="high",
                tags=["drainage", "waterlogging", "civic", "BBMP"],
                raw_data={"mock": True, "complaint_id": "BBMP-2025-10-07-156"}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Tree fallen on road near Cubbon Park blocking one lane. BBMP forest cell notified.",
                location="Cubbon Park Road",
                coordinates=Coordinates(lat=12.9762, lon=77.5929),
                severity="medium",
                tags=["tree", "obstruction", "civic", "BBMP"],
                raw_data={"mock": True, "complaint_id": "BBMP-2025-10-07-201"}
            ),
            Event(
                type="civic",
                source="civic_portal",
                description="Stray dog menace reported in Malleshwaram 8th Cross. Multiple complaints from residents.",
                location="Malleshwaram 8th Cross",
                coordinates=Coordinates(lat=13.0031, lon=77.5697),
                severity="low",
                tags=["stray_dogs", "animal", "civic", "BBMP"],
                raw_data={"mock": True, "complaint_id": "BBMP-2025-10-07-167"}
            )
        ]
        
        return mock_events
    
    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.api_key:
            logger.warning("API key not configured")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                logger.info("✓ Civic Portal API connection successful")
                return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
        
        return False


def main():
    """Test the civic portal connector"""
    print("\n" + "="*60)
    print("🏛️  Civic Portal API Connector Test")
    print("="*60 + "\n")
    
    connector = CivicPortalConnector()
    
    # Test connection
    if connector.test_connection():
        print("✓ API connection successful\n")
    else:
        print("⚠️  Using mock data (API not configured)\n")
    
    # Fetch civic complaints
    print("Fetching civic complaints...\n")
    events = connector.fetch_civic_complaints()
    
    print(f"\n📊 Found {len(events)} civic events:\n")
    for i, event in enumerate(events, 1):
        print(f"{i}. [{event.severity.upper()}] {event.description}")
        print(f"   Location: {event.location}")
        print(f"   Tags: {', '.join(event.tags)}")
        print()


if __name__ == "__main__":
    main()
