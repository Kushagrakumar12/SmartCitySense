"""
Kafka Producer for Event Streaming
Pushes events to Kafka topic for processing
"""
import json
from typing import List, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError

from config import Config
from utils import setup_logger, Event

logger = setup_logger(__name__)


class KafkaEventProducer:
    """
    Kafka producer for streaming events to processing pipeline
    """
    
    def __init__(self, bootstrap_servers: Optional[str] = None, topic: Optional[str] = None):
        """
        Initialize Kafka producer
        
        Args:
            bootstrap_servers: Kafka broker address (default from config)
            topic: Topic name (default from config)
        """
        self.bootstrap_servers = bootstrap_servers or Config.KAFKA_BROKER
        self.topic = topic or Config.KAFKA_TOPIC
        self.producer = None
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1  # Ensure ordering
            )
            logger.info(f"✓ Kafka producer connected to {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            logger.warning("⚠️  Kafka producer not available, events will be logged only")
    
    def send_event(self, event: Event) -> bool:
        """
        Send a single event to Kafka
        
        Args:
            event: Event object to send
        
        Returns:
            True if successful, False otherwise
        """
        if not self.producer:
            logger.warning(f"Kafka not available, would send: {event.description[:50]}...")
            return False
        
        try:
            # Convert event to dictionary
            event_data = event.to_dict()
            
            # Use event ID as key for partitioning
            future = self.producer.send(
                self.topic,
                key=event.id,
                value=event_data
            )
            
            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Event sent: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
            return True
        
        except KafkaError as e:
            logger.error(f"Kafka error sending event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending event: {e}")
            return False
    
    def send_events_batch(self, events: List[Event]) -> int:
        """
        Send multiple events in batch
        
        Args:
            events: List of Event objects
        
        Returns:
            Number of successfully sent events
        """
        if not events:
            logger.warning("No events to send")
            return 0
        
        success_count = 0
        
        for event in events:
            if self.send_event(event):
                success_count += 1
        
        # Flush to ensure all messages are sent
        if self.producer:
            self.producer.flush()
        
        logger.info(f"Sent {success_count}/{len(events)} events to Kafka")
        return success_count
    
    def close(self):
        """Close Kafka producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def main():
    """Test Kafka producer"""
    print("\n" + "="*60)
    print("📤 Kafka Producer Test")
    print("="*60 + "\n")
    
    # Create sample events
    from utils import Coordinates
    
    sample_events = [
        Event(
            type="traffic",
            source="google_maps",
            description="Test traffic event",
            location="Test Location",
            coordinates=Coordinates(lat=12.9716, lon=77.5946),
            severity="medium"
        ),
        Event(
            type="civic",
            source="civic_portal",
            description="Test civic event",
            location="Test Location 2",
            severity="low"
        )
    ]
    
    # Test sending
    with KafkaEventProducer() as producer:
        if producer.producer:
            print(f"✓ Connected to Kafka: {producer.bootstrap_servers}\n")
            print(f"Sending {len(sample_events)} test events...\n")
            
            success = producer.send_events_batch(sample_events)
            print(f"\n✓ Sent {success}/{len(sample_events)} events")
        else:
            print("⚠️  Kafka not configured")
            print("To use Kafka, set KAFKA_BROKER in your .env file")
            print("\nMock sending events:")
            for event in sample_events:
                print(f"  - {event.type}: {event.description}")


if __name__ == "__main__":
    main()
