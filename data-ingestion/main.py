"""
Main Data Ingestion Orchestrator
Runs all connectors periodically and pushes events to streaming queue
"""
import time
import schedule
import json
from datetime import datetime
from typing import List
from pathlib import Path

from config import Config
from utils import setup_logger, Event
from connectors import TrafficAPIConnector, CivicPortalConnector, SocialMediaConnector
from pipelines import KafkaEventProducer, FirebaseProducer

logger = setup_logger(__name__)


class DataIngestionOrchestrator:
    """
    Main orchestrator that:
    1. Runs all API connectors periodically
    2. Collects events from all sources
    3. Pushes events to Kafka/Firebase
    4. Monitors and logs statistics
    """
    
    def __init__(self, use_firebase: bool = False, mock_mode: bool = False, mock_file: str = None):
        """
        Initialize orchestrator
        
        Args:
            use_firebase: If True, use Firebase instead of Kafka
            mock_mode: If True, load events from mock file instead of APIs
            mock_file: Path to mock data JSON file
        """
        logger.info("="*60)
        logger.info("🚀 Initializing Data Ingestion Orchestrator")
        logger.info("="*60)
        
        self.mock_mode = mock_mode
        self.mock_file = mock_file
        self.mock_events = []
        
        if mock_mode:
            logger.info(f"🧪 Running in MOCK MODE")
            logger.info(f"Loading events from: {mock_file}")
            self._load_mock_events()
        else:
            # Initialize connectors only if not in mock mode
            self.traffic_connector = TrafficAPIConnector()
            self.civic_connector = CivicPortalConnector()
            self.social_connector = SocialMediaConnector()
        
        # Initialize producer
        if use_firebase:
            self.producer = FirebaseProducer()
            logger.info("Using Firebase for event streaming")
        else:
            self.producer = KafkaEventProducer()
            logger.info("Using Kafka for event streaming")
        
        # Statistics
        self.total_events_collected = 0
        self.total_events_sent = 0
        self.run_count = 0
        self.start_time = datetime.now()
    
    def _load_mock_events(self):
        """Load events from mock data file"""
        try:
            with open(self.mock_file, 'r') as f:
                data = json.load(f)
                
            # Convert dict to Event objects
            for event_dict in data:
                # Map mock data fields to Event fields
                event = Event(
                    id=event_dict.get('id', event_dict.get('event_id')),  # Handle both field names
                    type=event_dict.get('type'),
                    source=event_dict.get('source'),
                    description=event_dict.get('description'),
                    location=event_dict.get('location'),
                    coordinates=event_dict.get('coordinates'),
                    timestamp=event_dict.get('timestamp'),
                    severity=event_dict.get('severity', 'low'),
                    raw_data=event_dict.get('metadata', {}),
                    tags=event_dict.get('tags', [])
                )
                self.mock_events.append(event)
            
            logger.info(f"✓ Loaded {len(self.mock_events)} mock events")
        except Exception as e:
            logger.error(f"Error loading mock events: {e}")
            import traceback
            traceback.print_exc()
            self.mock_events = []
    
    def collect_all_events(self) -> List[Event]:
        """
        Collect events from all sources
        
        Returns:
            Combined list of events from all connectors
        """
        # If in mock mode, return mock events
        if self.mock_mode:
            logger.info(f"📦 Returning {len(self.mock_events)} mock events")
            return self.mock_events
        
        # Otherwise collect from real APIs
        all_events = []
        
        logger.info("\n" + "─"*60)
        logger.info(f"📡 Collection Run #{self.run_count + 1}")
        logger.info("─"*60)
        
        # Traffic events
        try:
            logger.info("Fetching traffic events...")
            traffic_events = self.traffic_connector.get_traffic_conditions()
            all_events.extend(traffic_events)
            logger.info(f"✓ Collected {len(traffic_events)} traffic events")
        except Exception as e:
            logger.error(f"Error collecting traffic events: {e}")
        
        # Civic events
        try:
            logger.info("Fetching civic events...")
            civic_events = self.civic_connector.fetch_civic_complaints()
            all_events.extend(civic_events)
            logger.info(f"✓ Collected {len(civic_events)} civic events")
        except Exception as e:
            logger.error(f"Error collecting civic events: {e}")
        
        # Social media events
        try:
            logger.info("Fetching social media events...")
            social_events = self.social_connector.fetch_all_events()
            all_events.extend(social_events)
            logger.info(f"✓ Collected {len(social_events)} social media events")
        except Exception as e:
            logger.error(f"Error collecting social media events: {e}")
        
        return all_events
    
    def send_events(self, events: List[Event]) -> int:
        """
        Send events to streaming queue
        
        Args:
            events: List of events to send
        
        Returns:
            Number of successfully sent events
        """
        if not events:
            logger.warning("No events to send")
            return 0
        
        try:
            if isinstance(self.producer, KafkaEventProducer):
                success_count = self.producer.send_events_batch(events)
            else:  # FirebaseProducer
                success_count = self.producer.send_events_batch(events)
            
            return success_count
        except Exception as e:
            logger.error(f"Error sending events: {e}")
            return 0
    
    def run_ingestion_cycle(self):
        """
        Run one complete ingestion cycle:
        1. Collect from all sources
        2. Send to streaming queue
        3. Update statistics
        """
        cycle_start = datetime.now()
        
        try:
            # Collect events
            events = self.collect_all_events()
            self.total_events_collected += len(events)
            
            # Send events
            if events:
                sent_count = self.send_events(events)
                self.total_events_sent += sent_count
                
                logger.info(f"\n📊 Cycle Summary:")
                logger.info(f"   Collected: {len(events)} events")
                logger.info(f"   Sent: {sent_count} events")
                logger.info(f"   Success rate: {sent_count/len(events)*100:.1f}%")
            else:
                logger.info("No new events in this cycle")
            
            self.run_count += 1
            
            # Print overall statistics
            self.print_statistics()
        
        except Exception as e:
            logger.error(f"Error in ingestion cycle: {e}")
        
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        logger.info(f"⏱️  Cycle completed in {cycle_duration:.2f}s\n")
    
    def print_statistics(self):
        """Print overall statistics"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        runtime_minutes = runtime / 60
        
        logger.info("\n" + "="*60)
        logger.info("📈 Overall Statistics")
        logger.info("="*60)
        logger.info(f"Runtime: {runtime_minutes:.1f} minutes")
        logger.info(f"Cycles completed: {self.run_count}")
        logger.info(f"Total events collected: {self.total_events_collected}")
        logger.info(f"Total events sent: {self.total_events_sent}")
        if self.total_events_collected > 0:
            logger.info(f"Overall success rate: {self.total_events_sent/self.total_events_collected*100:.1f}%")
        logger.info(f"Events per cycle (avg): {self.total_events_collected/max(1, self.run_count):.1f}")
        logger.info("="*60 + "\n")
    
    def start_scheduled(self, interval_minutes: int = None):
        """
        Start scheduled ingestion
        
        Args:
            interval_minutes: Polling interval in minutes (default from config)
        """
        if interval_minutes is None:
            interval_minutes = Config.POLLING_INTERVAL_SECONDS / 60
        
        logger.info(f"🕐 Starting scheduled ingestion (every {interval_minutes} minutes)")
        logger.info("Press Ctrl+C to stop\n")
        
        # Run immediately
        self.run_ingestion_cycle()
        
        # Schedule periodic runs
        schedule.every(interval_minutes).minutes.do(self.run_ingestion_cycle)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Stopping ingestion...")
            self.print_statistics()
            logger.info("Goodbye! 👋")
    
    def run_once(self):
        """Run ingestion cycle once (for testing)"""
        logger.info("Running one-time ingestion cycle\n")
        self.run_ingestion_cycle()
        self.print_statistics()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartCitySense Data Ingestion')
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduled', 'mock'],
        default='once',
        help='Run mode: once (single run), scheduled (continuous), or mock (test with mock data)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Polling interval in minutes (default: 5)'
    )
    parser.add_argument(
        '--firebase',
        action='store_true',
        help='Use Firebase instead of Kafka'
    )
    parser.add_argument(
        '--mock-file',
        type=str,
        default='data/mock/events_100.json',
        help='Path to mock data file (for mock mode)'
    )
    parser.add_argument(
        '--events',
        type=int,
        default=None,
        help='Number of events to send in mock mode (default: all)'
    )
    
    args = parser.parse_args()
    
    # Print configuration
    Config.print_config()
    
    # Determine if mock mode
    is_mock = args.mode == 'mock'
    
    # Create orchestrator
    orchestrator = DataIngestionOrchestrator(
        use_firebase=args.firebase or is_mock,  # Use Firebase for mock by default
        mock_mode=is_mock,
        mock_file=args.mock_file if is_mock else None
    )
    
    # If limiting events in mock mode
    if is_mock and args.events is not None and args.events < len(orchestrator.mock_events):
        logger.info(f"Limiting to first {args.events} events")
        orchestrator.mock_events = orchestrator.mock_events[:args.events]
    
    # Run
    if args.mode == 'once' or args.mode == 'mock':
        orchestrator.run_once()
    else:
        orchestrator.start_scheduled(interval_minutes=args.interval)


if __name__ == "__main__":
    main()
