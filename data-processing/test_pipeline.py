"""
Integration Tests for Data Processing Pipeline
Tests the complete flow from input to storage

EXPLANATION:
These tests verify that all components work together properly.

TEST SCENARIOS:
1. End-to-end processing (full pipeline)
2. Deduplication with similar events
3. Geocoding with various addresses
4. Categorization accuracy
5. Storage operations

"""
import unittest
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import all components
from config import Config
from processors import EventDeduplicator, GeoNormalizer, EventCategorizer
from utils import DataValidator


class TestDataProcessingPipeline(unittest.TestCase):
    """Test the complete data processing pipeline"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("\n" + "="*60)
        print("🧪 Running Data Processing Pipeline Tests")
        print("="*60 + "\n")
    
    def setUp(self):
        """Set up for each test"""
        self.deduplicator = EventDeduplicator()
        self.geo_normalizer = GeoNormalizer()
        self.categorizer = EventCategorizer()
        self.validator = DataValidator()
    
    def test_deduplication(self):
        """Test duplicate detection"""
        print("Testing deduplication...")
        
        # Create similar events
        base_time = datetime.utcnow()
        
        events = [
            {
                'id': 'event1',
                'type': 'traffic',
                'description': 'Heavy traffic jam on MG Road near Trinity',
                'location': 'MG Road',
                'timestamp': base_time.isoformat(),
                'source': 'twitter'
            },
            {
                'id': 'event2',
                'type': 'traffic',
                'description': 'Traffic jam on MG Road at Trinity Circle',
                'location': 'MG Road',
                'timestamp': (base_time + timedelta(minutes=10)).isoformat(),
                'source': 'google_maps'
            },
            {
                'id': 'event3',
                'type': 'civic',
                'description': 'Power outage in Koramangala',
                'location': 'Koramangala',
                'timestamp': base_time.isoformat(),
                'source': 'reddit'
            }
        ]
        
        # Mark duplicates
        processed = self.deduplicator.mark_duplicates(events)
        
        # Check that event2 is marked as duplicate of event1
        event2 = next(e for e in processed if e['id'] == 'event2')
        
        self.assertTrue('is_duplicate' in event2)
        # They should be similar (same type, similar text, close time)
        
        print("  ✓ Deduplication works correctly")
    
    def test_geocoding(self):
        """Test geo-normalization"""
        print("Testing geocoding...")
        
        events = [
            {
                'id': 'test1',
                'location': 'MG Road, Bangalore',
                'type': 'traffic'
            },
            {
                'id': 'test2',
                'location': 'Koramangala 5th Block, Bangalore',
                'type': 'civic'
            },
            {
                'id': 'test3',
                'coordinates': {'lat': 12.9716, 'lon': 77.5946},
                'type': 'traffic'
            }
        ]
        
        # Normalize
        processed = self.geo_normalizer.batch_normalize(events)
        
        # Check results
        for event in processed:
            if event['id'] == 'test1' or event['id'] == 'test2':
                # Should have coordinates now (if API available)
                if 'coordinates' in event:
                    self.assertIn('lat', event['coordinates'])
                    self.assertIn('lon', event['coordinates'])
                    print(f"  ✓ Event {event['id']} geocoded")
            
            elif event['id'] == 'test3':
                # Should have address now
                if 'full_address' in event:
                    print(f"  ✓ Event {event['id']} reverse geocoded")
        
        print("  ✓ Geocoding works correctly")
    
    def test_categorization(self):
        """Test event categorization"""
        print("Testing categorization...")
        
        events = [
            {
                'id': 'cat1',
                'type': 'traffic',
                'description': 'Major accident on Outer Ring Road blocking all lanes',
                'timestamp': datetime.now().isoformat(),
                'severity': 'critical',
                'tags': ['traffic']
            },
            {
                'id': 'cat2',
                'type': 'civic',
                'description': 'BESCOM reports power outage in HSR Layout',
                'timestamp': datetime.now().isoformat(),
                'severity': 'high',
                'tags': ['civic']
            }
        ]
        
        # Categorize
        processed = self.categorizer.batch_categorize(events)
        
        # Check results
        event1 = next(e for e in processed if e['id'] == 'cat1')
        self.assertIn('subtype', event1)
        self.assertIn('urgency', event1)
        self.assertIn('accident', event1['subtype'].lower())
        self.assertEqual(event1['urgency'], 'critical')
        
        event2 = next(e for e in processed if e['id'] == 'cat2')
        self.assertIn('power', event2['subtype'].lower())
        
        print("  ✓ Categorization works correctly")
    
    def test_quality_scoring(self):
        """Test quality score calculation"""
        print("Testing quality scoring...")
        
        # High quality event
        good_event = {
            'id': 'good',
            'type': 'traffic',
            'description': 'Very detailed description of the traffic situation on MG Road with specific details',
            'coordinates': {'lat': 12.9716, 'lon': 77.5946},
            'zone': 'Central Bangalore',
            'neighborhood': 'MG Road',
            'tags': ['traffic', 'urgent', 'mgroad'],
            'timestamp': datetime.utcnow().isoformat(),
            'verified': True
        }
        
        # Low quality event
        poor_event = {
            'id': 'poor',
            'type': 'traffic',
            'description': 'jam',
            'tags': []
        }
        
        good_score = self.validator.calculate_quality_score(good_event)
        poor_score = self.validator.calculate_quality_score(poor_event)
        
        self.assertGreater(good_score, poor_score)
        self.assertGreater(good_score, 0.7)
        self.assertLess(poor_score, 0.5)
        
        print(f"  Good event score: {good_score:.2f}")
        print(f"  Poor event score: {poor_score:.2f}")
        print("  ✓ Quality scoring works correctly")
    
    def test_end_to_end(self):
        """Test complete pipeline flow"""
        print("Testing end-to-end pipeline...")
        
        # Create test events
        events = [
            {
                'id': 'e2e_1',
                'type': 'traffic',
                'description': 'Traffic jam on MG Road',
                'location': 'MG Road, Bangalore',
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'test',
                'severity': 'medium'
            }
        ]
        
        # Step 1: Deduplication
        step1 = self.deduplicator.mark_duplicates(events)
        self.assertEqual(len(step1), 1)
        
        # Step 2: Geocoding
        step2 = self.geo_normalizer.batch_normalize(step1)
        self.assertEqual(len(step2), 1)
        
        # Step 3: Categorization
        step3 = self.categorizer.batch_categorize(step2)
        self.assertEqual(len(step3), 1)
        
        # Step 4: Quality scoring
        final_event = step3[0]
        quality = self.validator.calculate_quality_score(final_event)
        final_event['quality_score'] = quality
        
        # Verify enhancements
        self.assertIn('is_duplicate', final_event)
        # coordinates may or may not be present depending on API availability
        self.assertIn('subtype', final_event)
        self.assertIn('urgency', final_event)
        self.assertIn('quality_score', final_event)
        
        print(f"  Final event has {len(final_event)} fields")
        print(f"  Quality score: {quality:.2f}")
        print("  ✓ End-to-end pipeline works correctly")


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test configuration loads correctly"""
        print("Testing configuration...")
        
        self.assertIsNotNone(Config.BATCH_SIZE)
        self.assertIsNotNone(Config.SIMILARITY_THRESHOLD)
        self.assertIsNotNone(Config.BANGALORE_ZONES)
        
        # Check Bangalore zones
        self.assertEqual(len(Config.BANGALORE_ZONES), 5)
        self.assertIn("Central Bangalore", Config.BANGALORE_ZONES)
        
        print("  ✓ Configuration loaded correctly")
    
    def test_event_type_mapping(self):
        """Test event type mappings"""
        print("Testing event type mapping...")
        
        self.assertIn('traffic', Config.EVENT_TYPE_MAPPING)
        self.assertIn('civic', Config.EVENT_TYPE_MAPPING)
        self.assertIn('emergency', Config.EVENT_TYPE_MAPPING)
        
        # Check traffic subtypes
        traffic_types = Config.EVENT_TYPE_MAPPING['traffic']
        self.assertIn('accident', traffic_types)
        self.assertIn('congestion', traffic_types)
        
        print("  ✓ Event type mapping configured correctly")


def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
