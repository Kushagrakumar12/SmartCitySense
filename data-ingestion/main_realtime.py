"""
Real-Time Data Ingestion for CityPulse
Continuously monitors Reddit for new city events
Combines real-time data with mock data
"""
import time
import signal
import sys
from datetime import datetime
from typing import List
from pathlib import Path

from config import Config
from utils import setup_logger, Event
from connectors.reddit_realtime import RedditRealtimeConnector
from pipelines import FirebaseProducer

logger = setup_logger(__name__)


class RealtimeIngestionOrchestrator:
    """
    Real-time orchestrator that:
    1. Continuously monitors Reddit for new posts
    2. Processes and enriches events
    3. Streams to Firebase in real-time
    4. Maintains statistics and monitoring
    """
    
    def __init__(self, mock_enabled: bool = True, mock_file: str = None):
        """
        Initialize real-time orchestrator
        
        Args:
            mock_enabled: Whether to also load mock data
            mock_file: Path to mock data file
        """
        logger.info("="*60)
        logger.info("🔴 Initializing Real-Time Data Ingestion")
        logger.info("="*60)
        
        # Initialize Reddit connector
        self.reddit_connector = RedditRealtimeConnector()
        
        # Initialize Firebase producer
        self.producer = FirebaseProducer()
        logger.info("Using Firebase for real-time streaming")
        
        # Load mock data if enabled
        self.mock_enabled = mock_enabled
        self.mock_events = []
        if mock_enabled and mock_file:
            self._load_mock_events(mock_file)
        
        # Statistics
        self.total_events_collected = 0
        self.total_events_sent = 0
        self.realtime_events = 0
        self.mock_events_sent = 0
        self.start_time = datetime.now()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
    
    def _load_mock_events(self, mock_file: str):
        """Load mock events from file"""
        try:
            import json
            with open(mock_file, 'r') as f:
                data = json.load(f)
            
            # Convert to Event objects
            for event_dict in data:
                event = Event(
                    id=event_dict.get('id', event_dict.get('event_id')),
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
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        logger.info("\n\n🛑 Received shutdown signal, stopping gracefully...")
        self.running = False
        self.reddit_connector.stop_streaming()
    
    def send_events(self, events: List[Event]) -> int:
        """
        Send events to Firebase
        
        Args:
            events: List of events to send
            
        Returns:
            Number of successfully sent events
        """
        if not events:
            return 0
        
        try:
            success_count = self.producer.send_events_batch(events)
            return success_count
        except Exception as e:
            logger.error(f"Error sending events: {e}")
            return 0
    
    def send_mock_data(self):
        """Send all mock data to Firebase"""
        if not self.mock_enabled or not self.mock_events:
            logger.info("Mock data disabled or not available")
            return
        
        logger.info(f"\n📦 Sending {len(self.mock_events)} mock events to Firebase...")
        
        # Send in batches
        batch_size = 100
        total_sent = 0
        
        for i in range(0, len(self.mock_events), batch_size):
            batch = self.mock_events[i:i+batch_size]
            sent = self.send_events(batch)
            total_sent += sent
            logger.info(f"  Sent batch {i//batch_size + 1}: {sent}/{len(batch)} events")
            time.sleep(1)  # Small delay between batches
        
        self.mock_events_sent = total_sent
        logger.info(f"✓ Mock data sent: {total_sent}/{len(self.mock_events)} events\n")
    
    def run_polling_mode(self, interval_seconds: int = 60):
        """
        Run in polling mode - check Reddit periodically
        
        Args:
            interval_seconds: Time between polls
        """
        if not self.reddit_connector.is_configured():
            logger.error("❌ Reddit API not configured! Cannot run real-time mode.")
            logger.info("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
            return
        
        logger.info(f"🔄 Starting polling mode (every {interval_seconds} seconds)")
        logger.info("Press Ctrl+C to stop\n")
        
        # Send mock data first
        if self.mock_enabled:
            self.send_mock_data()
        
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                cycle_start = datetime.now()
                
                logger.info(f"\n{'─'*60}")
                logger.info(f"📡 Polling Cycle #{cycle_count}")
                logger.info(f"{'─'*60}")
                
                # Fetch new posts from Reddit
                new_events = self.reddit_connector.fetch_latest_posts(limit=30)
                hot_events = self.reddit_connector.fetch_hot_posts(limit=15)
                
                # Combine and deduplicate
                all_events = new_events + hot_events
                unique_events = self._deduplicate_events(all_events)
                
                self.total_events_collected += len(unique_events)
                self.realtime_events += len(unique_events)
                
                # Send to Firebase
                if unique_events:
                    sent_count = self.send_events(unique_events)
                    self.total_events_sent += sent_count
                    
                    logger.info(f"\n📊 Cycle Summary:")
                    logger.info(f"   New events: {len(unique_events)}")
                    logger.info(f"   Sent to Firebase: {sent_count}")
                    logger.info(f"   Success rate: {sent_count/len(unique_events)*100:.1f}%")
                else:
                    logger.info("No new events in this cycle")
                
                # Print statistics
                self._print_statistics()
                
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                logger.info(f"⏱️  Cycle completed in {cycle_duration:.2f}s")
                
                # Wait for next cycle
                wait_time = max(0, interval_seconds - cycle_duration)
                if wait_time > 0 and self.running:
                    logger.info(f"💤 Waiting {wait_time:.0f}s until next cycle...\n")
                    time.sleep(wait_time)
        
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Interrupted by user")
        finally:
            self._print_final_statistics()
    
    def run_continuous_mode(self):
        """
        Run in continuous streaming mode
        Monitors Reddit stream continuously
        """
        if not self.reddit_connector.is_configured():
            logger.error("❌ Reddit API not configured! Cannot run real-time mode.")
            return
        
        logger.info("🌊 Starting continuous streaming mode")
        logger.info("Press Ctrl+C to stop\n")
        
        # Send mock data first
        if self.mock_enabled:
            self.send_mock_data()
        
        # Define callback for new events
        def event_callback(events: List[Event]):
            if events:
                self.total_events_collected += len(events)
                self.realtime_events += len(events)
                
                sent = self.send_events(events)
                self.total_events_sent += sent
                
                for event in events:
                    logger.info(f"🆕 New event: [{event.type.upper()}] {event.description[:80]}...")
        
        try:
            # Start streaming (blocking)
            self.reddit_connector.stream_posts(callback=event_callback)
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Interrupted by user")
        finally:
            self._print_final_statistics()
    
    def _deduplicate_events(self, events: List[Event]) -> List[Event]:
        """Remove duplicate events based on description"""
        seen = set()
        unique = []
        
        for event in events:
            # Create a simple hash of the event
            event_hash = f"{event.source}_{event.description[:50]}"
            if event_hash not in seen:
                seen.add(event_hash)
                unique.append(event)
        
        return unique
    
    def _print_statistics(self):
        """Print current statistics"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        runtime_minutes = runtime / 60
        
        logger.info(f"\n📈 Real-Time Statistics:")
        logger.info(f"   Runtime: {runtime_minutes:.1f} minutes")
        logger.info(f"   Real-time events: {self.realtime_events}")
        logger.info(f"   Mock events: {self.mock_events_sent}")
        logger.info(f"   Total collected: {self.total_events_collected}")
        logger.info(f"   Total sent: {self.total_events_sent}")
        if self.total_events_collected > 0:
            logger.info(f"   Success rate: {self.total_events_sent/self.total_events_collected*100:.1f}%")
    
    def _print_final_statistics(self):
        """Print final statistics on shutdown"""
        runtime = (datetime.now() - self.start_time).total_seconds()
        runtime_minutes = runtime / 60
        
        logger.info("\n" + "="*60)
        logger.info("📊 Final Statistics")
        logger.info("="*60)
        logger.info(f"Total runtime: {runtime_minutes:.1f} minutes")
        logger.info(f"Real-time events collected: {self.realtime_events}")
        logger.info(f"Mock events sent: {self.mock_events_sent}")
        logger.info(f"Total events collected: {self.total_events_collected}")
        logger.info(f"Total events sent to Firebase: {self.total_events_sent}")
        if self.total_events_collected > 0:
            logger.info(f"Overall success rate: {self.total_events_sent/self.total_events_collected*100:.1f}%")
        logger.info("="*60)
        logger.info("\n👋 Goodbye!\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CityPulse Real-Time Data Ingestion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Polling mode with mock data (recommended)
  python main_realtime.py --mode polling --interval 60 --mock-file data/mock/events_1000.json
  
  # Polling mode without mock data
  python main_realtime.py --mode polling --interval 60 --no-mock
  
  # Continuous streaming mode (advanced)
  python main_realtime.py --mode streaming
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['polling', 'streaming'],
        default='polling',
        help='Run mode: polling (check periodically) or streaming (continuous)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Polling interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--mock-file',
        type=str,
        default='data/mock/events_1000.json',
        help='Path to mock data file'
    )
    parser.add_argument(
        '--no-mock',
        action='store_true',
        help='Disable mock data (real-time only)'
    )
    
    args = parser.parse_args()
    
    # Print configuration
    print("\n")
    Config.print_config()
    print("\n")
    
    # Check if mock file exists
    mock_enabled = not args.no_mock
    if mock_enabled and not Path(args.mock_file).exists():
        logger.warning(f"Mock file not found: {args.mock_file}")
        logger.warning("Running without mock data")
        mock_enabled = False
    
    # Create orchestrator
    orchestrator = RealtimeIngestionOrchestrator(
        mock_enabled=mock_enabled,
        mock_file=args.mock_file if mock_enabled else None
    )
    
    # Run based on mode
    if args.mode == 'polling':
        orchestrator.run_polling_mode(interval_seconds=args.interval)
    else:
        orchestrator.run_continuous_mode()


if __name__ == "__main__":
    main()
