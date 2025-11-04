"""
Kafka Consumer
Reads events from Person 1's Kafka stream

EXPLANATION:
Person 1 publishes events to Kafka topic "smartcitysense_events".
This consumer reads those events and feeds them to our processing pipeline.

WHY KAFKA?
- Real-time streaming: Get events as they happen
- Reliability: Kafka guarantees message delivery
- Scalability: Can handle high volume of events
- Decoupling: Person 1 and Person 2 work independently

WORKFLOW:
1. Connect to Kafka broker
2. Subscribe to Person 1's topic
3. Continuously poll for new messages
4. Deserialize JSON events
5. Pass to processing pipeline

"""
from typing import Dict, Any, List, Callable, Optional
import json
from datetime import datetime

try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("⚠️  kafka-python not installed. Run: pip install kafka-python")

from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


class EventKafkaConsumer:
    """
    Consumes events from Kafka stream
    
    Features:
    - Auto-commit offsets (tracks what's been read)
    - JSON deserialization
    - Error recovery
    - Batch processing
    """
    
    def __init__(self):
        """Initialize Kafka consumer"""
        if not KAFKA_AVAILABLE:
            raise ImportError("kafka-python library not installed")
        
        self.broker = Config.KAFKA_BROKER
        self.topic = Config.KAFKA_TOPIC
        self.group_id = Config.KAFKA_GROUP_ID
        
        self.consumer = None
        self._setup_consumer()
        
        logger.info(f"Kafka consumer initialized for topic '{self.topic}'")
    
    def _setup_consumer(self):
        """Create and configure Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.broker,
                group_id=self.group_id,
                
                # Deserialize JSON messages
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                
                # Start from latest if no previous offset
                auto_offset_reset='latest',
                
                # Auto-commit offsets every 5 seconds
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                
                # Connection settings
                api_version=(0, 10, 1),
                consumer_timeout_ms=1000,  # Return after 1 second if no messages
            )
            
            logger.info(f"✓ Connected to Kafka broker: {self.broker}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def consume_batch(self, max_messages: int = None) -> List[Dict[str, Any]]:
        """
        Consume a batch of messages
        
        Args:
            max_messages: Maximum messages to consume (None = use Config.BATCH_SIZE)
        
        Returns:
            List of event dictionaries
        """
        if not self.consumer:
            logger.error("Consumer not initialized")
            return []
        
        batch_size = max_messages or Config.BATCH_SIZE
        events = []
        
        try:
            # Poll for messages
            for message in self.consumer:
                event = message.value
                
                # Add metadata
                event['_kafka_metadata'] = {
                    'partition': message.partition,
                    'offset': message.offset,
                    'timestamp': message.timestamp,
                    'consumed_at': datetime.utcnow().isoformat()
                }
                
                events.append(event)
                
                # Stop if batch size reached
                if len(events) >= batch_size:
                    break
            
            if events:
                logger.info(f"Consumed {len(events)} events from Kafka")
            
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
        
        return events
    
    def consume_stream(self, callback: Callable[[Dict[str, Any]], None], 
                      batch_size: int = None):
        """
        Continuously consume and process events
        
        Args:
            callback: Function to process each event
            batch_size: Process in batches of this size
        """
        if not self.consumer:
            logger.error("Consumer not initialized")
            return
        
        batch_size = batch_size or Config.BATCH_SIZE
        logger.info(f"Starting stream consumption (batch_size={batch_size})")
        
        batch = []
        
        try:
            for message in self.consumer:
                event = message.value
                
                # Add metadata
                event['_kafka_metadata'] = {
                    'partition': message.partition,
                    'offset': message.offset,
                    'timestamp': message.timestamp,
                    'consumed_at': datetime.utcnow().isoformat()
                }
                
                batch.append(event)
                
                # Process batch when full
                if len(batch) >= batch_size:
                    try:
                        callback(batch)
                        batch = []
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")
                        batch = []  # Clear batch to avoid reprocessing
        
        except KeyboardInterrupt:
            logger.info("Stream consumption stopped by user")
            
            # Process remaining events
            if batch:
                try:
                    callback(batch)
                except Exception as e:
                    logger.error(f"Error processing final batch: {e}")
        
        except Exception as e:
            logger.error(f"Error in stream consumption: {e}")
    
    def close(self):
        """Close consumer connection"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")


def main():
    """Test Kafka consumer"""
    print("\n" + "="*60)
    print("📡 Kafka Consumer Test")
    print("="*60 + "\n")
    
    if not KAFKA_AVAILABLE:
        print("❌ kafka-python not installed")
        print("   Install: pip install kafka-python")
        return
    
    try:
        consumer = EventKafkaConsumer()
        
        print(f"Broker: {consumer.broker}")
        print(f"Topic: {consumer.topic}")
        print(f"Group: {consumer.group_id}")
        print()
        
        print("Consuming messages (waiting 10 seconds)...")
        events = consumer.consume_batch(max_messages=10)
        
        if events:
            print(f"\n✓ Received {len(events)} events")
            print("\nFirst event:")
            print(json.dumps(events[0], indent=2))
        else:
            print("\n⚠️  No events received")
            print("   Make sure Person 1 is publishing events")
        
        consumer.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
