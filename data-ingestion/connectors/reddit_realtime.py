"""
Reddit Real-Time Connector for CityPulse
Continuously monitors r/bangalore for new posts and comments
"""
import time
import praw
from datetime import datetime, timedelta
from typing import List, Set
from threading import Thread, Event as ThreadEvent

from config import Config
from utils import setup_logger, Event, Coordinates

logger = setup_logger(__name__)


class RedditRealtimeConnector:
    """
    Real-time Reddit connector that:
    1. Monitors r/bangalore for new posts
    2. Filters for relevant city events
    3. Provides streaming updates
    """
    
    def __init__(self):
        """Initialize Reddit real-time connector"""
        self.client_id = Config.REDDIT_CLIENT_ID
        self.client_secret = Config.REDDIT_CLIENT_SECRET
        self.user_agent = Config.REDDIT_USER_AGENT
        self.reddit = None
        
        # Track seen posts to avoid duplicates
        self.seen_posts: Set[str] = set()
        self.seen_comments: Set[str] = set()
        
        # Control streaming
        self.stop_event = ThreadEvent()
        
        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("✓ Reddit Real-Time API initialized")
                logger.info(f"  User Agent: {self.user_agent}")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {e}")
                self.reddit = None
        else:
            logger.warning("⚠️  Reddit API credentials not configured")
    
    def is_configured(self) -> bool:
        """Check if Reddit API is properly configured"""
        return self.reddit is not None
    
    def fetch_latest_posts(self, subreddit_name: str = "bangalore", limit: int = 50) -> List[Event]:
        """
        Fetch latest posts from subreddit
        
        Args:
            subreddit_name: Subreddit to monitor (default: bangalore)
            limit: Number of posts to fetch
            
        Returns:
            List of Event objects from new posts
        """
        if not self.reddit:
            logger.warning("Reddit client not available")
            return []
        
        events = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Fetch new posts
            for post in subreddit.new(limit=limit):
                # Skip if already seen
                if post.id in self.seen_posts:
                    continue
                
                # Parse post
                event = self._parse_post(post)
                if event:
                    events.append(event)
                    self.seen_posts.add(post.id)
            
            if events:
                logger.info(f"✓ Fetched {len(events)} new events from r/{subreddit_name}")
            
        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
        
        return events
    
    def fetch_hot_posts(self, subreddit_name: str = "bangalore", limit: int = 25) -> List[Event]:
        """
        Fetch hot/trending posts from subreddit
        
        Args:
            subreddit_name: Subreddit to monitor
            limit: Number of posts to fetch
            
        Returns:
            List of Event objects from hot posts
        """
        if not self.reddit:
            logger.warning("Reddit client not available")
            return []
        
        events = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Fetch hot posts
            for post in subreddit.hot(limit=limit):
                # Skip if already seen
                if post.id in self.seen_posts:
                    continue
                
                # Parse post
                event = self._parse_post(post)
                if event:
                    events.append(event)
                    self.seen_posts.add(post.id)
            
            if events:
                logger.info(f"✓ Fetched {len(events)} hot events from r/{subreddit_name}")
            
        except Exception as e:
            logger.error(f"Error fetching hot Reddit posts: {e}")
        
        return events
    
    def stream_posts(self, subreddit_name: str = "bangalore", callback=None) -> None:
        """
        Stream new posts in real-time
        
        Args:
            subreddit_name: Subreddit to monitor
            callback: Function to call with new events (receives List[Event])
        """
        if not self.reddit:
            logger.error("Cannot stream: Reddit client not available")
            return
        
        logger.info(f"📡 Starting real-time stream for r/{subreddit_name}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Stream submissions
            for submission in subreddit.stream.submissions(skip_existing=True, pause_after=-1):
                if self.stop_event.is_set():
                    break
                
                if submission is None:
                    # No new submissions, wait a bit
                    time.sleep(1)
                    continue
                
                # Parse submission
                event = self._parse_post(submission)
                if event and submission.id not in self.seen_posts:
                    self.seen_posts.add(submission.id)
                    
                    # Call callback if provided
                    if callback:
                        callback([event])
                    else:
                        logger.info(f"New event: {event.description[:100]}")
        
        except Exception as e:
            logger.error(f"Error in Reddit stream: {e}")
        
        logger.info("Reddit stream stopped")
    
    def _parse_post(self, post) -> Event:
        """
        Parse Reddit post into Event object
        
        Args:
            post: PRAW submission object
            
        Returns:
            Event object or None if not relevant
        """
        try:
            title = post.title
            
            # Filter for relevant posts
            if not self._is_relevant(title):
                return None
            
            # Classify event type
            event_type = self._classify_post(title)
            
            # Combine title and selftext
            description = title
            if post.selftext and len(post.selftext) > 0:
                description += f". {post.selftext[:200]}"
            
            # Calculate severity based on score and engagement
            severity = self._calculate_severity(post)
            
            # Extract location if mentioned
            location = self._extract_location(title + " " + post.selftext)
            
            event = Event(
                type=event_type,
                source="reddit",
                description=description[:500],
                location=location,
                coordinates=None,  # Reddit doesn't provide coordinates
                severity=severity,
                tags=self._extract_tags(title, post.selftext),
                raw_data={
                    "post_id": post.id,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "created_utc": post.created_utc,
                    "author": str(post.author) if post.author else "[deleted]"
                }
            )
            
            return event
        
        except Exception as e:
            logger.error(f"Error parsing Reddit post: {e}")
            return None
    
    def _is_relevant(self, text: str) -> bool:
        """Check if post is relevant to city events"""
        keywords = [
            "traffic", "jam", "accident", "road", "congestion",
            "power", "electricity", "water", "pothole", "garbage",
            "civic", "bbmp", "bescom", "bwssb", "emergency",
            "alert", "psa", "avoid", "closed", "blocked"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _classify_post(self, text: str) -> str:
        """Classify post into event type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["traffic", "jam", "accident", "road", "congestion", "signal"]):
            return "traffic"
        elif any(word in text_lower for word in ["power", "electricity", "water", "pothole", "garbage", "bbmp", "bescom"]):
            return "civic"
        elif any(word in text_lower for word in ["emergency", "urgent", "fire", "help"]):
            return "emergency"
        else:
            return "other"
    
    def _calculate_severity(self, post) -> str:
        """Calculate severity based on post engagement"""
        score = post.score
        comments = post.num_comments
        
        # High severity if lots of engagement
        if score > 100 or comments > 50:
            return "high"
        elif score > 50 or comments > 20:
            return "medium"
        else:
            return "low"
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text (simple keyword matching)"""
        # Common Bangalore locations
        locations = [
            "Silk Board", "Marathahalli", "Whitefield", "Electronic City",
            "Koramangala", "Indiranagar", "HSR Layout", "BTM Layout",
            "Jayanagar", "MG Road", "Brigade Road", "Commercial Street",
            "Hebbal", "Yeshwantpur", "Majestic", "KR Puram", "Sarjapur",
            "Bellandur", "Outer Ring Road", "ORR", "Hosur Road",
            "Tumkur Road", "Mysore Road", "Bannerghatta Road"
        ]
        
        text_lower = text.lower()
        for location in locations:
            if location.lower() in text_lower:
                return f"{location}, Bangalore"
        
        return "Bangalore"
    
    def _extract_tags(self, title: str, body: str) -> List[str]:
        """Extract relevant tags from post content"""
        tags = ["reddit", "social_media"]
        
        text = (title + " " + body).lower()
        
        # Add specific tags
        tag_keywords = {
            "traffic": ["traffic", "jam", "congestion", "accident"],
            "power": ["power", "electricity", "bescom"],
            "water": ["water", "bwssb"],
            "pothole": ["pothole"],
            "civic": ["bbmp", "civic", "garbage"],
            "emergency": ["emergency", "urgent"],
            "psa": ["psa", "alert"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def stop_streaming(self):
        """Stop the streaming thread"""
        self.stop_event.set()
    
    def clear_cache(self):
        """Clear seen posts cache"""
        self.seen_posts.clear()
        self.seen_comments.clear()
        logger.info("Cache cleared")


def main():
    """Test Reddit real-time connector"""
    print("\n" + "="*60)
    print("📡 Reddit Real-Time Connector Test")
    print("="*60 + "\n")
    
    connector = RedditRealtimeConnector()
    
    if not connector.is_configured():
        print("❌ Reddit API not configured!")
        print("Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET in .env")
        return
    
    print("✓ Reddit API configured\n")
    
    # Test 1: Fetch latest posts
    print("Test 1: Fetching latest posts...")
    events = connector.fetch_latest_posts(limit=10)
    print(f"Found {len(events)} events\n")
    
    for i, event in enumerate(events[:5], 1):
        print(f"{i}. [{event.type.upper()}] {event.description[:80]}...")
        print(f"   Location: {event.location} | Severity: {event.severity}")
        print()
    
    # Test 2: Fetch hot posts
    print("\nTest 2: Fetching hot/trending posts...")
    hot_events = connector.fetch_hot_posts(limit=10)
    print(f"Found {len(hot_events)} hot events\n")
    
    print("\n✅ Tests completed!")


if __name__ == "__main__":
    main()
