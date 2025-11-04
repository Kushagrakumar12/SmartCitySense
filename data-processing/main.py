"""
Main Data Processing Pipeline
Person 2's Orchestrator

EXPLANATION:
This is the heart of Person 2's system. It coordinates all components:

PIPELINE FLOW:
┌──────────────┐
│   Person 1   │ (Data Ingestion)
│ Kafka/Firebase│
└──────┬───────┘
       │ Raw Events
       ▼
┌──────────────┐
│   CONSUMER   │ Read events
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ DEDUPLICATOR │ Find & mark duplicates
└──────┬───────┘
       │
       ▼
┌──────────────┐
│GEO NORMALIZER│ Add coordinates, zones
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ CATEGORIZER  │ Refine types, add tags
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  VALIDATOR   │ Check quality
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   STORAGE    │ Save to Firestore
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Member B/C  │ (AI/ML & Frontend)
└──────────────┘

MODES:
1. Batch Mode: Process existing events once
2. Stream Mode: Continuously process new events
3. Backfill Mode: Reprocess historical events

"""
import argparse
import sys
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta

from config import Config
from utils import setup_logger, DataValidator
from processors import EventDeduplicator, GeoNormalizer, EventCategorizer
from storage import FirebaseStorage

# Consumer imports (may not be available)
try:
    from consumers import EventKafkaConsumer
    KAFKA_AVAILABLE = True
except:
    KAFKA_AVAILABLE = False

try:
    from consumers import FirebaseEventReader
    FIREBASE_READER_AVAILABLE = True
except:
    FIREBASE_READER_AVAILABLE = False

logger = setup_logger(__name__)


class DataProcessingPipeline:
    """
    Main orchestrator for data processing
    
    Coordinates all components and handles the processing workflow
    """
    
    def __init__(self, input_source: str = 'auto'):
        """
        Initialize pipeline
        
        Args:
            input_source: 'kafka', 'firebase', or 'auto' (detect automatically)
        """
        logger.info("Initializing data processing pipeline...")
        
        # Initialize processors
        self.deduplicator = EventDeduplicator()
        self.geo_normalizer = GeoNormalizer()
        self.categorizer = EventCategorizer()
        self.validator = DataValidator()
        
        # Initialize storage
        self.storage = FirebaseStorage()
        
        # Initialize consumer
        self.consumer = None
        self.input_source = self._detect_input_source(input_source)
        
        if self.input_source == 'kafka':
            if KAFKA_AVAILABLE:
                self.consumer = EventKafkaConsumer()
            else:
                logger.error("Kafka not available")
                raise ImportError("kafka-python not installed")
        
        elif self.input_source == 'firebase':
            if FIREBASE_READER_AVAILABLE:
                self.consumer = FirebaseEventReader()
            else:
                logger.error("Firebase reader not available")
                raise ImportError("firebase-admin not installed")
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'duplicates_found': 0,
            'geocoded': 0,
            'categorized': 0,
            'stored': 0,
            'errors': 0,
            'start_time': datetime.utcnow()
        }
        
        logger.info(f"✓ Pipeline initialized (input: {self.input_source})")
    
    def _detect_input_source(self, preferred: str) -> str:
        """Detect which input source to use"""
        if preferred != 'auto':
            return preferred
        
        # Auto-detect
        if KAFKA_AVAILABLE and Config.KAFKA_BROKER:
            return 'kafka'
        elif FIREBASE_READER_AVAILABLE and Config.FIREBASE_PROJECT_ID:
            return 'firebase'
        else:
            logger.error("No input source available")
            raise ValueError("No input source configured")
    
    def process_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of events through the pipeline
        
        Args:
            events: List of raw events from Person 1
        
        Returns:
            List of processed events
        """
        if not events:
            return []
        
        logger.info(f"Processing {len(events)} events...")
        
        # Step 1: Deduplication
        logger.info("Step 1/4: Deduplication")
        deduplicated = self.deduplicator.mark_duplicates(events)
        
        # Count duplicates
        duplicates = sum(1 for e in deduplicated if e.get('is_duplicate'))
        self.stats['duplicates_found'] += duplicates
        logger.info(f"  Found {duplicates} duplicates")
        
        # Step 2: Geo-normalization
        logger.info("Step 2/4: Geo-normalization")
        geocoded = self.geo_normalizer.batch_normalize(deduplicated)
        
        # Count successfully geocoded
        geocoded_count = sum(1 for e in geocoded if e.get('coordinates'))
        self.stats['geocoded'] += geocoded_count
        logger.info(f"  Geocoded {geocoded_count} events")
        
        # Step 3: Categorization
        logger.info("Step 3/4: Categorization")
        categorized = self.categorizer.batch_categorize(geocoded)
        self.stats['categorized'] += len(categorized)
        logger.info(f"  Categorized {len(categorized)} events")
        
        # Step 4: Validation & Quality Scoring
        logger.info("Step 4/4: Validation")
        validated = []
        for event in categorized:
            try:
                # Validate and add quality score
                quality_score = self.validator.calculate_quality_score(event)
                event['quality_score'] = quality_score
                
                # Only store if quality is acceptable (>0.3)
                if quality_score > 0.3:
                    validated.append(event)
                else:
                    logger.debug(f"Skipping low quality event: {event.get('id')}")
            
            except Exception as e:
                logger.warning(f"Validation error for event {event.get('id')}: {e}")
                self.stats['errors'] += 1
        
        logger.info(f"  Validated {len(validated)} events (quality > 0.3)")
        
        self.stats['total_processed'] += len(validated)
        
        return validated
    
    def run_batch(self, max_events: int = None):
        """
        Run pipeline in batch mode (process once and exit)
        
        Args:
            max_events: Maximum events to process
        """
        logger.info("Starting batch processing...")
        
        try:
            # Read events
            if self.input_source == 'kafka':
                events = self.consumer.consume_batch(max_events)
            else:  # firebase
                events = self.consumer.read_new_events(max_events)
            
            if not events:
                logger.info("No events to process")
                return
            
            # Process
            processed = self.process_events(events)
            
            # Store
            if processed:
                stored_count = self.storage.store_batch(processed)
                self.stats['stored'] += stored_count
                logger.info(f"✓ Stored {stored_count} processed events")
            
            self._print_stats()
        
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            self.stats['errors'] += 1
    
    def run_stream(self):
        """
        Run pipeline in stream mode (continuous processing)
        """
        logger.info("Starting stream processing...")
        logger.info("Press Ctrl+C to stop")
        
        def process_and_store(events: List[Dict[str, Any]]):
            """Callback for processing batches"""
            processed = self.process_events(events)
            
            if processed:
                stored_count = self.storage.store_batch(processed)
                self.stats['stored'] += stored_count
                
                # Print stats every 10 batches
                if self.stats['total_processed'] % (Config.BATCH_SIZE * 10) == 0:
                    self._print_stats()
        
        try:
            if self.input_source == 'kafka':
                # Kafka stream
                self.consumer.consume_stream(process_and_store)
            
            else:  # Firebase
                # Poll continuously
                self.consumer.poll_continuously(process_and_store)
        
        except KeyboardInterrupt:
            logger.info("\nStream processing stopped by user")
            self._print_stats()
        
        except Exception as e:
            logger.error(f"Error in stream processing: {e}")
    
    def backfill(self, hours: int = 24):
        """
        Reprocess historical events
        
        Args:
            hours: Number of hours to look back
        """
        logger.info(f"Starting backfill (last {hours} hours)...")
        
        if self.input_source != 'firebase':
            logger.error("Backfill only supported with Firebase input")
            return
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Read historical events
            events = self.consumer.read_events_in_range(start_time, end_time)
            
            if not events:
                logger.info("No events to backfill")
                return
            
            # Process in batches
            batch_size = Config.BATCH_SIZE
            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]
                processed = self.process_events(batch)
                
                if processed:
                    stored_count = self.storage.store_batch(processed)
                    self.stats['stored'] += stored_count
            
            logger.info("✓ Backfill complete")
            self._print_stats()
        
        except Exception as e:
            logger.error(f"Error in backfill: {e}")
    
    def _print_stats(self):
        """Print processing statistics"""
        elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
        print("\n" + "="*60)
        print("📊 Processing Statistics")
        print("="*60)
        print(f"Total Processed:  {self.stats['total_processed']}")
        print(f"Duplicates Found: {self.stats['duplicates_found']}")
        print(f"Geocoded:         {self.stats['geocoded']}")
        print(f"Categorized:      {self.stats['categorized']}")
        print(f"Stored:           {self.stats['stored']}")
        print(f"Errors:           {self.stats['errors']}")
        print(f"Elapsed Time:     {elapsed:.1f}s")
        
        if elapsed > 0:
            rate = self.stats['total_processed'] / elapsed
            print(f"Processing Rate:  {rate:.2f} events/sec")
        
        print("="*60 + "\n")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="SmartCitySense - Data Processing Pipeline (Person 2)")
    
    parser.add_argument(
        'mode',
        choices=['batch', 'stream', 'backfill'],
        help='Processing mode'
    )
    
    parser.add_argument(
        '--input',
        choices=['kafka', 'firebase', 'auto'],
        default='auto',
        help='Input source (default: auto-detect)'
    )
    
    parser.add_argument(
        '--max-events',
        type=int,
        help='Maximum events to process (batch mode only)'
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours to look back (backfill mode only)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*60)
    print("🚀 SmartCitySense - Data Processing Pipeline")
    print("   Person 2: Event Processing & Enhancement")
    print("="*60 + "\n")
    
    # Validate config
    if not Config.validate():
        print("❌ Configuration invalid")
        sys.exit(1)
    
    Config.print_config()
    
    try:
        # Initialize pipeline
        pipeline = DataProcessingPipeline(input_source=args.input)
        
        # Run selected mode
        if args.mode == 'batch':
            pipeline.run_batch(max_events=args.max_events)
        
        elif args.mode == 'stream':
            pipeline.run_stream()
        
        elif args.mode == 'backfill':
            pipeline.backfill(hours=args.hours)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
