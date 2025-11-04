"""
Monitoring & Metrics
Track pipeline performance and health

EXPLANATION:
Tracks key metrics to ensure Person 2's system is working properly:

METRICS TRACKED:
1. Processing Rate: events/second
2. Deduplication Rate: % of duplicates found
3. Geocoding Success Rate: % successfully geocoded
4. Average Quality Score: How good is our data?
5. Processing Time: Time per event
6. Error Rate: % of failures

WHY MONITORING?
- Detect issues early (e.g., API rate limits, connection problems)
- Optimize performance (find bottlenecks)
- Report to team (Member A, B, C want to know system status)
- Track data quality over time

"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import json

from utils import setup_logger

logger = setup_logger(__name__)


class ProcessingMonitor:
    """
    Monitors pipeline performance and health
    
    Tracks metrics and provides reporting
    """
    
    def __init__(self):
        """Initialize monitor"""
        self.metrics = {
            'events_received': 0,
            'events_processed': 0,
            'events_stored': 0,
            'duplicates_found': 0,
            'geocoding_success': 0,
            'geocoding_failures': 0,
            'categorization_success': 0,
            'validation_failures': 0,
            'storage_errors': 0,
            'total_errors': 0
        }
        
        # Track quality scores
        self.quality_scores = []
        
        # Track processing times
        self.processing_times = []
        
        # Track by event type
        self.type_counts = defaultdict(int)
        
        # Track by urgency
        self.urgency_counts = defaultdict(int)
        
        # Track by zone
        self.zone_counts = defaultdict(int)
        
        self.start_time = datetime.utcnow()
        
        logger.info("Monitoring initialized")
    
    def record_batch_received(self, count: int):
        """Record batch of events received"""
        self.metrics['events_received'] += count
    
    def record_duplicate_found(self):
        """Record duplicate detected"""
        self.metrics['duplicates_found'] += 1
    
    def record_geocoding(self, success: bool):
        """Record geocoding attempt"""
        if success:
            self.metrics['geocoding_success'] += 1
        else:
            self.metrics['geocoding_failures'] += 1
    
    def record_processing(self, event: Dict[str, Any], processing_time: float):
        """
        Record successful event processing
        
        Args:
            event: Processed event
            processing_time: Time taken in seconds
        """
        self.metrics['events_processed'] += 1
        
        # Track processing time
        self.processing_times.append(processing_time)
        
        # Track quality score
        if 'quality_score' in event:
            self.quality_scores.append(event['quality_score'])
        
        # Track by type
        event_type = event.get('type', 'unknown')
        self.type_counts[event_type] += 1
        
        # Track by urgency
        urgency = event.get('urgency', 'unknown')
        self.urgency_counts[urgency] += 1
        
        # Track by zone
        zone = event.get('zone', 'unknown')
        self.zone_counts[zone] += 1
    
    def record_stored(self, count: int):
        """Record events successfully stored"""
        self.metrics['events_stored'] += count
    
    def record_error(self, error_type: str):
        """Record an error"""
        self.metrics['total_errors'] += 1
        
        if error_type == 'validation':
            self.metrics['validation_failures'] += 1
        elif error_type == 'storage':
            self.metrics['storage_errors'] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate and return statistics
        
        Returns:
            Dictionary of statistics
        """
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Calculate rates
        processing_rate = self.metrics['events_processed'] / elapsed if elapsed > 0 else 0
        
        # Calculate percentages
        total_received = self.metrics['events_received']
        
        if total_received > 0:
            deduplication_rate = (self.metrics['duplicates_found'] / total_received) * 100
            storage_rate = (self.metrics['events_stored'] / total_received) * 100
            error_rate = (self.metrics['total_errors'] / total_received) * 100
        else:
            deduplication_rate = storage_rate = error_rate = 0
        
        # Geocoding success rate
        total_geocoding = self.metrics['geocoding_success'] + self.metrics['geocoding_failures']
        if total_geocoding > 0:
            geocoding_success_rate = (self.metrics['geocoding_success'] / total_geocoding) * 100
        else:
            geocoding_success_rate = 0
        
        # Average quality score
        avg_quality = sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0
        
        # Average processing time
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            'uptime_seconds': elapsed,
            'uptime_formatted': str(timedelta(seconds=int(elapsed))),
            
            'events': {
                'received': self.metrics['events_received'],
                'processed': self.metrics['events_processed'],
                'stored': self.metrics['events_stored']
            },
            
            'rates': {
                'processing_rate_per_sec': round(processing_rate, 2),
                'deduplication_rate_percent': round(deduplication_rate, 2),
                'storage_rate_percent': round(storage_rate, 2),
                'geocoding_success_percent': round(geocoding_success_rate, 2),
                'error_rate_percent': round(error_rate, 2)
            },
            
            'quality': {
                'average_score': round(avg_quality, 3),
                'samples': len(self.quality_scores)
            },
            
            'performance': {
                'avg_processing_time_ms': round(avg_processing_time * 1000, 2),
                'samples': len(self.processing_times)
            },
            
            'by_type': dict(self.type_counts),
            'by_urgency': dict(self.urgency_counts),
            'by_zone': dict(self.zone_counts),
            
            'errors': {
                'total': self.metrics['total_errors'],
                'validation': self.metrics['validation_failures'],
                'storage': self.metrics['storage_errors']
            }
        }
    
    def print_report(self):
        """Print monitoring report"""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("📊 Processing Monitor Report")
        print("="*70)
        
        print(f"\n⏱️  UPTIME: {stats['uptime_formatted']}")
        
        print("\n📥 EVENTS:")
        print(f"  Received:  {stats['events']['received']}")
        print(f"  Processed: {stats['events']['processed']}")
        print(f"  Stored:    {stats['events']['stored']}")
        
        print("\n📈 RATES:")
        print(f"  Processing: {stats['rates']['processing_rate_per_sec']} events/sec")
        print(f"  Deduplication: {stats['rates']['deduplication_rate_percent']}% duplicates")
        print(f"  Geocoding Success: {stats['rates']['geocoding_success_percent']}%")
        print(f"  Storage Success: {stats['rates']['storage_rate_percent']}%")
        print(f"  Error Rate: {stats['rates']['error_rate_percent']}%")
        
        print("\n⭐ QUALITY:")
        print(f"  Average Score: {stats['quality']['average_score']}")
        print(f"  Samples: {stats['quality']['samples']}")
        
        print("\n⚡ PERFORMANCE:")
        print(f"  Avg Processing Time: {stats['performance']['avg_processing_time_ms']} ms")
        
        if stats['by_type']:
            print("\n📋 BY TYPE:")
            for event_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {event_type}: {count}")
        
        if stats['by_urgency']:
            print("\n🚨 BY URGENCY:")
            for urgency, count in sorted(stats['by_urgency'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {urgency}: {count}")
        
        if stats['by_zone']:
            print("\n🗺️  BY ZONE:")
            for zone, count in sorted(stats['by_zone'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {zone}: {count}")
        
        if stats['errors']['total'] > 0:
            print("\n❌ ERRORS:")
            print(f"  Total: {stats['errors']['total']}")
            print(f"  Validation: {stats['errors']['validation']}")
            print(f"  Storage: {stats['errors']['storage']}")
        
        print("\n" + "="*70 + "\n")
    
    def export_json(self) -> str:
        """
        Export statistics as JSON
        
        Returns:
            JSON string
        """
        stats = self.get_statistics()
        return json.dumps(stats, indent=2)
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check system health
        
        Returns:
            Health status dictionary
        """
        stats = self.get_statistics()
        
        # Define health thresholds
        HEALTHY_ERROR_RATE = 5.0  # % errors acceptable
        HEALTHY_GEOCODING_RATE = 80.0  # % geocoding success needed
        HEALTHY_QUALITY_SCORE = 0.6  # Minimum quality score
        
        issues = []
        
        # Check error rate
        if stats['rates']['error_rate_percent'] > HEALTHY_ERROR_RATE:
            issues.append(f"High error rate: {stats['rates']['error_rate_percent']}%")
        
        # Check geocoding
        if stats['rates']['geocoding_success_percent'] < HEALTHY_GEOCODING_RATE:
            issues.append(f"Low geocoding success: {stats['rates']['geocoding_success_percent']}%")
        
        # Check quality
        if stats['quality']['average_score'] < HEALTHY_QUALITY_SCORE:
            issues.append(f"Low quality score: {stats['quality']['average_score']}")
        
        # Determine overall status
        if not issues:
            status = 'healthy'
            message = 'All systems operational'
        elif len(issues) == 1:
            status = 'degraded'
            message = 'Some issues detected'
        else:
            status = 'unhealthy'
            message = 'Multiple issues detected'
        
        return {
            'status': status,
            'message': message,
            'issues': issues,
            'timestamp': datetime.utcnow().isoformat()
        }


def main():
    """Test monitoring"""
    print("\n" + "="*60)
    print("📊 Monitoring Test")
    print("="*60 + "\n")
    
    monitor = ProcessingMonitor()
    
    # Simulate some activity
    print("Simulating processing...")
    
    monitor.record_batch_received(100)
    
    for i in range(100):
        # Simulate processing
        event = {
            'type': 'traffic' if i % 2 == 0 else 'civic',
            'urgency': 'critical' if i % 10 == 0 else 'needs_attention',
            'zone': 'Central Bangalore',
            'quality_score': 0.7 + (i % 3) * 0.1
        }
        
        monitor.record_processing(event, 0.05)  # 50ms processing time
        
        # Some duplicates
        if i % 15 == 0:
            monitor.record_duplicate_found()
        
        # Some geocoding
        monitor.record_geocoding(i % 8 != 0)  # 87.5% success
    
    monitor.record_stored(95)
    monitor.record_error('validation')
    monitor.record_error('validation')
    monitor.record_error('storage')
    
    # Print report
    monitor.print_report()
    
    # Check health
    health = monitor.check_health()
    print(f"Health Status: {health['status'].upper()}")
    print(f"Message: {health['message']}")
    if health['issues']:
        print("Issues:")
        for issue in health['issues']:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
