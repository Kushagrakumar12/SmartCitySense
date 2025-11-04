"""
Monitoring and Statistics Dashboard
Real-time monitoring of data ingestion pipeline
"""
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

from utils import setup_logger

logger = setup_logger(__name__)


class IngestionMonitor:
    """
    Monitor data ingestion pipeline health and statistics
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        
        # Event counters by source
        self.events_by_source = defaultdict(int)
        self.events_by_type = defaultdict(int)
        
        # Error tracking
        self.errors = []
        self.api_failures = defaultdict(int)
        
        # Performance metrics
        self.cycle_durations = []
        self.events_per_cycle = []
        
        # Rate limiting
        self.api_calls = defaultdict(list)
    
    def record_event(self, source: str, event_type: str):
        """Record an event"""
        self.events_by_source[source] += 1
        self.events_by_type[event_type] += 1
    
    def record_events_batch(self, events: List):
        """Record multiple events"""
        for event in events:
            self.record_event(event.source, event.type)
    
    def record_error(self, source: str, error: str):
        """Record an error"""
        self.errors.append({
            'timestamp': datetime.now(),
            'source': source,
            'error': error
        })
        self.api_failures[source] += 1
    
    def record_cycle(self, duration: float, event_count: int):
        """Record a cycle completion"""
        self.cycle_durations.append(duration)
        self.events_per_cycle.append(event_count)
    
    def record_api_call(self, api_name: str):
        """Record an API call for rate limiting monitoring"""
        self.api_calls[api_name].append(datetime.now())
    
    def get_api_call_rate(self, api_name: str, window_minutes: int = 60) -> int:
        """Get API calls in the last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        calls = self.api_calls[api_name]
        return len([c for c in calls if c > cutoff])
    
    def get_statistics(self) -> Dict:
        """Get current statistics"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        stats = {
            'runtime_seconds': runtime,
            'runtime_minutes': runtime / 60,
            'total_events': sum(self.events_by_source.values()),
            'events_by_source': dict(self.events_by_source),
            'events_by_type': dict(self.events_by_type),
            'total_errors': len(self.errors),
            'api_failures': dict(self.api_failures),
            'cycles_completed': len(self.cycle_durations),
            'avg_cycle_duration': sum(self.cycle_durations) / len(self.cycle_durations) if self.cycle_durations else 0,
            'avg_events_per_cycle': sum(self.events_per_cycle) / len(self.events_per_cycle) if self.events_per_cycle else 0
        }
        
        return stats
    
    def print_dashboard(self):
        """Print monitoring dashboard"""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("📊 DATA INGESTION MONITORING DASHBOARD")
        print("="*70)
        
        # Runtime
        print(f"\n⏱️  Runtime: {stats['runtime_minutes']:.1f} minutes")
        print(f"🔄 Cycles: {stats['cycles_completed']}")
        if stats['avg_cycle_duration'] > 0:
            print(f"⏲️  Avg Cycle Duration: {stats['avg_cycle_duration']:.2f}s")
        
        # Events
        print(f"\n📥 Total Events: {stats['total_events']}")
        print(f"📈 Avg Events/Cycle: {stats['avg_events_per_cycle']:.1f}")
        
        # By source
        print("\n📡 Events by Source:")
        for source, count in sorted(stats['events_by_source'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {source:20} {count:5} ({count/max(1, stats['total_events'])*100:.1f}%)")
        
        # By type
        print("\n🏷️  Events by Type:")
        for event_type, count in sorted(stats['events_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {event_type:20} {count:5} ({count/max(1, stats['total_events'])*100:.1f}%)")
        
        # Errors
        if stats['total_errors'] > 0:
            print(f"\n⚠️  Errors: {stats['total_errors']}")
            print("   Recent errors:")
            for error in self.errors[-5:]:  # Last 5 errors
                timestamp = error['timestamp'].strftime('%H:%M:%S')
                print(f"   [{timestamp}] {error['source']}: {error['error'][:50]}")
        
        # API failures
        if stats['api_failures']:
            print("\n❌ API Failures:")
            for api, count in stats['api_failures'].items():
                print(f"   {api:20} {count} failures")
        
        # API rate monitoring
        print("\n🔌 API Call Rate (last hour):")
        for api_name in ['google_maps', 'twitter', 'reddit', 'civic_portal']:
            rate = self.get_api_call_rate(api_name)
            print(f"   {api_name:20} {rate} calls")
        
        print("\n" + "="*70 + "\n")
    
    def health_check(self) -> Dict[str, str]:
        """Perform health check"""
        stats = self.get_statistics()
        
        health = {
            'overall': 'healthy',
            'issues': []
        }
        
        # Check for too many errors
        if stats['total_errors'] > 10:
            health['overall'] = 'degraded'
            health['issues'].append('High error rate')
        
        # Check for API failures
        if any(count > 5 for count in stats['api_failures'].values()):
            health['overall'] = 'degraded'
            health['issues'].append('Multiple API failures')
        
        # Check for low event collection
        if stats['cycles_completed'] > 5 and stats['avg_events_per_cycle'] < 1:
            health['overall'] = 'warning'
            health['issues'].append('Low event collection rate')
        
        return health


# Global monitor instance
monitor = IngestionMonitor()


def main():
    """Demo monitoring"""
    print("Monitoring Dashboard Demo\n")
    
    # Simulate some data
    from utils import Event, Coordinates
    
    events = [
        Event(type="traffic", source="google_maps", description="Test 1", location="Loc1"),
        Event(type="civic", source="civic_portal", description="Test 2", location="Loc2"),
        Event(type="traffic", source="twitter", description="Test 3", location="Loc3"),
    ]
    
    monitor.record_events_batch(events)
    monitor.record_cycle(5.2, 3)
    monitor.record_api_call('google_maps')
    monitor.record_api_call('twitter')
    
    # Print dashboard
    monitor.print_dashboard()
    
    # Health check
    health = monitor.health_check()
    print(f"Health Status: {health['overall'].upper()}")
    if health['issues']:
        print(f"Issues: {', '.join(health['issues'])}")


if __name__ == "__main__":
    main()
