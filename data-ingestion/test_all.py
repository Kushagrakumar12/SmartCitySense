#!/usr/bin/env python3
"""
Quick test script to verify all components are working
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from utils import Event, Coordinates
from connectors import TrafficAPIConnector, CivicPortalConnector, SocialMediaConnector


def test_configuration():
    """Test configuration"""
    print("\n" + "="*60)
    print("🧪 Testing Configuration")
    print("="*60)
    Config.print_config()
    return True


def test_event_schema():
    """Test event creation"""
    print("\n" + "="*60)
    print("🧪 Testing Event Schema")
    print("="*60)
    
    try:
        event = Event(
            type="traffic",
            source="google_maps",
            description="Test event",
            location="Bangalore",
            coordinates=Coordinates(lat=12.9716, lon=77.5946),
            severity="medium"
        )
        
        print(f"✓ Event created: {event.id}")
        print(f"  Type: {event.type}")
        print(f"  Source: {event.source}")
        print(f"  Location: {event.location}")
        print(f"  Severity: {event.severity}")
        
        # Test serialization
        data = event.to_dict()
        print(f"✓ Event serialized to dict ({len(data)} fields)")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_connectors():
    """Test all connectors"""
    print("\n" + "="*60)
    print("🧪 Testing Connectors")
    print("="*60)
    
    success = True
    
    # Traffic connector
    try:
        print("\n📍 Traffic Connector:")
        traffic = TrafficAPIConnector()
        events = traffic.get_traffic_conditions()
        print(f"✓ Collected {len(events)} traffic events")
    except Exception as e:
        print(f"✗ Traffic connector error: {e}")
        success = False
    
    # Civic connector
    try:
        print("\n📍 Civic Portal Connector:")
        civic = CivicPortalConnector()
        events = civic.fetch_civic_complaints()
        print(f"✓ Collected {len(events)} civic events")
    except Exception as e:
        print(f"✗ Civic connector error: {e}")
        success = False
    
    # Social media connector
    try:
        print("\n📍 Social Media Connector:")
        social = SocialMediaConnector()
        events = social.fetch_all_events()
        print(f"✓ Collected {len(events)} social media events")
    except Exception as e:
        print(f"✗ Social media connector error: {e}")
        success = False
    
    return success


def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀 "*20)
    print("SmartCitySense - Data Ingestion Test Suite")
    print("🚀 "*20)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_configuration()))
    results.append(("Event Schema", test_event_schema()))
    results.append(("Connectors", test_connectors()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python main.py --mode once")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
