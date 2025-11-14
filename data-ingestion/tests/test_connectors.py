"""
Unit tests for data ingestion connectors
"""
import unittest
from datetime import datetime

from utils import Event, Coordinates
from connectors import TrafficAPIConnector, CivicPortalConnector, SocialMediaConnector


class TestEventSchema(unittest.TestCase):
    """Test Event schema validation"""
    
    def test_event_creation(self):
        """Test creating a valid event"""
        event = Event(
            type="traffic",
            source="google_maps",
            description="Test event",
            location="Test Location",
            severity="high"
        )
        
        self.assertEqual(event.type, "traffic")
        self.assertEqual(event.source, "google_maps")
        self.assertIsInstance(event.id, str)
        self.assertIsInstance(event.timestamp, datetime)
    
    def test_event_with_coordinates(self):
        """Test event with coordinates"""
        coords = Coordinates(lat=12.9716, lon=77.5946)
        event = Event(
            type="civic",
            source="civic_portal",
            description="Test",
            location="Bangalore",
            coordinates=coords
        )
        
        self.assertIsNotNone(event.coordinates)
        self.assertEqual(event.coordinates.lat, 12.9716)
        self.assertEqual(event.coordinates.lon, 77.5946)
    
    def test_event_to_dict(self):
        """Test event serialization"""
        event = Event(
            type="traffic",
            source="twitter",
            description="Test",
            location="Location"
        )
        
        data = event.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('timestamp', data)


class TestTrafficConnector(unittest.TestCase):
    """Test traffic API connector"""
    
    def setUp(self):
        self.connector = TrafficAPIConnector()
    
    def test_connector_initialization(self):
        """Test connector initializes correctly"""
        self.assertIsNotNone(self.connector)
    
    def test_get_traffic_conditions(self):
        """Test fetching traffic conditions"""
        events = self.connector.get_traffic_conditions()
        self.assertIsInstance(events, list)
        
        if events:
            event = events[0]
            self.assertIsInstance(event, Event)
            self.assertEqual(event.source, "google_maps")
    
    def test_mock_data(self):
        """Test mock data generation"""
        events = self.connector._get_mock_traffic_data()
        self.assertIsInstance(events, list)
        self.assertTrue(len(events) > 0)


class TestCivicConnector(unittest.TestCase):
    """Test civic portal connector"""
    
    def setUp(self):
        self.connector = CivicPortalConnector()
    
    def test_connector_initialization(self):
        """Test connector initializes correctly"""
        self.assertIsNotNone(self.connector)
    
    def test_fetch_civic_complaints(self):
        """Test fetching civic complaints"""
        events = self.connector.fetch_civic_complaints()
        self.assertIsInstance(events, list)
        
        if events:
            event = events[0]
            self.assertIsInstance(event, Event)
            self.assertEqual(event.source, "civic_portal")
    
    def test_categorize_complaint(self):
        """Test complaint categorization"""
        result = self.connector._categorize_complaint("power outage")
        self.assertEqual(result, "civic")
        
        result = self.connector._categorize_complaint("fire emergency")
        self.assertEqual(result, "emergency")


class TestSocialMediaConnector(unittest.TestCase):
    """Test social media connectors"""
    
    def setUp(self):
        self.connector = SocialMediaConnector()
    
    def test_connector_initialization(self):
        """Test connector initializes correctly"""
        self.assertIsNotNone(self.connector.twitter)
        self.assertIsNotNone(self.connector.reddit)
    
    def test_fetch_all_events(self):
        """Test fetching from all social media"""
        events = self.connector.fetch_all_events()
        self.assertIsInstance(events, list)


if __name__ == '__main__':
    unittest.main()
