"""
Social Media API Connector
Fetches city events from Twitter/X, Reddit, and Instagram
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import tweepy
import praw
from tenacity import retry, stop_after_attempt, wait_exponential

from config import Config
from utils import setup_logger, Event, Coordinates

logger = setup_logger(__name__)


class TwitterConnector:
    """Twitter/X API connector for real-time city events"""
    
    def __init__(self):
        self.bearer_token = Config.TWITTER_BEARER_TOKEN
        self.client = None
        
        if self.bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info("✓ Twitter API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
        else:
            logger.warning("⚠️  Twitter API not configured")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_tweets(self, query: str = "bangalore OR bengaluru", max_results: int = 50) -> List[Event]:
        """
        Fetch recent tweets about Bangalore
        
        Args:
            query: Search query
            max_results: Maximum tweets to fetch
        
        Returns:
            List of Event objects from tweets
        """
        if not self.client:
            logger.warning("Twitter client not available, returning mock data")
            return self._get_mock_twitter_data()
        
        events = []
        
        try:
            # Build search query with traffic/civic keywords
            full_query = f"({query}) (traffic OR accident OR power OR water OR pothole OR jam) -is:retweet"
            
            # Search recent tweets (last 7 days for free tier)
            tweets = self.client.search_recent_tweets(
                query=full_query,
                max_results=max_results,
                tweet_fields=['created_at', 'geo', 'public_metrics'],
                expansions=['geo.place_id'],
                place_fields=['full_name', 'geo']
            )
            
            if tweets.data:
                for tweet in tweets.data:
                    event = self._parse_tweet(tweet)
                    if event:
                        events.append(event)
                
                logger.info(f"Fetched {len(events)} events from Twitter")
            else:
                logger.info("No tweets found")
        
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {e}")
            return self._get_mock_twitter_data()
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return self._get_mock_twitter_data()
        
        return events
    
    def _parse_tweet(self, tweet) -> Optional[Event]:
        """Parse tweet into Event object"""
        try:
            text = tweet.text
            
            # Determine event type from content
            event_type = self._classify_tweet(text)
            
            # Extract location (simplified - in production, use NLP)
            location = "Bangalore"  # Default
            
            # Basic severity (can be improved with sentiment analysis)
            severity = "medium"
            if "urgent" in text.lower() or "critical" in text.lower():
                severity = "high"
            
            event = Event(
                type=event_type,
                source="twitter",
                description=text[:280],  # Limit description length
                location=location,
                coordinates=None,  # Twitter API v2 geo is limited
                severity=severity,
                tags=["social_media", "twitter"],
                raw_data={
                    "tweet_id": tweet.id,
                    "created_at": str(tweet.created_at),
                    "retweets": tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                    "likes": tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0
                }
            )
            
            return event
        
        except Exception as e:
            logger.error(f"Error parsing tweet: {e}")
            return None
    
    def _classify_tweet(self, text: str) -> str:
        """Classify tweet into event type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["traffic", "jam", "accident", "road", "congestion"]):
            return "traffic"
        elif any(word in text_lower for word in ["power", "electricity", "water", "pothole", "garbage"]):
            return "civic"
        elif any(word in text_lower for word in ["fire", "emergency", "urgent", "help"]):
            return "emergency"
        else:
            return "other"
    
    def _get_mock_twitter_data(self) -> List[Event]:
        """Generate mock Twitter data"""
        logger.info("Generating mock Twitter data")
        
        return [
            Event(
                type="traffic",
                source="twitter",
                description="Massive traffic jam at Silk Board junction. Avoid this route! Been stuck here for 45 mins 😤 #BangaloreTraffic #SilkBoard",
                location="Silk Board, Bangalore",
                coordinates=Coordinates(lat=12.9173, lon=77.6221),
                severity="high",
                tags=["twitter", "traffic", "silkboard"],
                raw_data={"mock": True, "likes": 145, "retweets": 67, "tweet_id": "mock_tw_001"}
            ),
            Event(
                type="civic",
                source="twitter",
                description="Power cut in Indiranagar since 2 hours. No update from BESCOM. When will this be fixed?? @BESCOM_Official #PowerOutage",
                location="Indiranagar, Bangalore",
                coordinates=Coordinates(lat=12.9716, lon=77.6412),
                severity="medium",
                tags=["twitter", "power", "civic"],
                raw_data={"mock": True, "likes": 89, "retweets": 34, "tweet_id": "mock_tw_002"}
            ),
            Event(
                type="traffic",
                source="twitter",
                description="Accident on Outer Ring Road near Marathahalli bridge. One lane blocked. Traffic moving very slowly. #Bangalore #TrafficAlert",
                location="Marathahalli, Bangalore",
                coordinates=Coordinates(lat=12.9591, lon=77.6974),
                severity="high",
                tags=["twitter", "traffic", "accident"],
                raw_data={"mock": True, "likes": 76, "retweets": 43, "tweet_id": "mock_tw_003"}
            ),
            Event(
                type="civic",
                source="twitter",
                description="Huge pothole on Sarjapur Road near Wipro campus. Almost damaged my car! @BBMP please fix ASAP #BangaloreRoads #Pothole",
                location="Sarjapur Road, Bangalore",
                coordinates=Coordinates(lat=12.9000, lon=77.6900),
                severity="medium",
                tags=["twitter", "pothole", "civic"],
                raw_data={"mock": True, "likes": 52, "retweets": 19, "tweet_id": "mock_tw_004"}
            ),
            Event(
                type="civic",
                source="twitter",
                description="Water pipeline burst near Electronic City Phase 1. Huge water wastage! Someone tag BWSSB please 💧 #WaterCrisis",
                location="Electronic City, Bangalore",
                coordinates=Coordinates(lat=12.8456, lon=77.6603),
                severity="high",
                tags=["twitter", "water", "civic", "emergency"],
                raw_data={"mock": True, "likes": 112, "retweets": 58, "tweet_id": "mock_tw_005"}
            ),
            Event(
                type="traffic",
                source="twitter",
                description="Heavy rain + traffic = nightmare at Hebbal flyover. Moving at snail's pace 🐌 #BangaloreRains #Traffic",
                location="Hebbal, Bangalore",
                coordinates=Coordinates(lat=13.0358, lon=77.5970),
                severity="medium",
                tags=["twitter", "traffic", "rain"],
                raw_data={"mock": True, "likes": 94, "retweets": 28, "tweet_id": "mock_tw_006"}
            )
        ]


class RedditConnector:
    """Reddit API connector for r/bangalore"""
    
    def __init__(self):
        self.client_id = Config.REDDIT_CLIENT_ID
        self.client_secret = Config.REDDIT_CLIENT_SECRET
        self.user_agent = Config.REDDIT_USER_AGENT
        self.reddit = None
        
        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("✓ Reddit API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {e}")
        else:
            logger.warning("⚠️  Reddit API not configured")
    
    def fetch_posts(self, subreddit_name: str = "bangalore", limit: int = 50) -> List[Event]:
        """
        Fetch recent posts from r/bangalore
        
        Args:
            subreddit_name: Subreddit to search
            limit: Maximum posts to fetch
        
        Returns:
            List of Event objects from Reddit posts
        """
        if not self.reddit:
            logger.warning("Reddit client not available, returning mock data")
            return self._get_mock_reddit_data()
        
        events = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Fetch hot posts
            for post in subreddit.hot(limit=limit):
                event = self._parse_post(post)
                if event:
                    events.append(event)
            
            logger.info(f"Fetched {len(events)} events from Reddit")
        
        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
            return self._get_mock_reddit_data()
        
        return events
    
    def _parse_post(self, post) -> Optional[Event]:
        """Parse Reddit post into Event object"""
        try:
            title = post.title
            
            # Filter for relevant posts
            if not self._is_relevant(title):
                return None
            
            event_type = self._classify_post(title)
            
            # Combine title and selftext
            description = title
            if post.selftext and len(post.selftext) > 0:
                description += f". {post.selftext[:200]}"
            
            event = Event(
                type=event_type,
                source="reddit",
                description=description[:500],
                location="Bangalore",
                coordinates=None,
                severity="medium",
                tags=["reddit", "social_media"],
                raw_data={
                    "post_id": post.id,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": post.url
                }
            )
            
            return event
        
        except Exception as e:
            logger.error(f"Error parsing Reddit post: {e}")
            return None
    
    def _is_relevant(self, text: str) -> bool:
        """Check if post is relevant to city events"""
        keywords = ["traffic", "power", "water", "accident", "jam", "road", "civic", "emergency"]
        return any(keyword in text.lower() for keyword in keywords)
    
    def _classify_post(self, text: str) -> str:
        """Classify post into event type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["traffic", "jam", "accident", "road"]):
            return "traffic"
        elif any(word in text_lower for word in ["power", "water", "civic", "garbage"]):
            return "civic"
        else:
            return "other"
    
    def _get_mock_reddit_data(self) -> List[Event]:
        """Generate mock Reddit data"""
        logger.info("Generating mock Reddit data")
        
        return [
            Event(
                type="traffic",
                source="reddit",
                description="PSA: Avoid Outer Ring Road today. Major construction causing 1+ hour delays. Take alternative route via Sarjapur Road.",
                location="Outer Ring Road, Bangalore",
                coordinates=Coordinates(lat=12.9350, lon=77.6900),
                severity="high",
                tags=["reddit", "traffic", "construction", "PSA"],
                raw_data={"mock": True, "score": 287, "comments": 54, "post_id": "mock_rd_001"}
            ),
            Event(
                type="civic",
                source="reddit",
                description="Power outage in Koramangala for 4 hours now. Anyone else facing this? BESCOM not responding to complaints.",
                location="Koramangala, Bangalore",
                coordinates=Coordinates(lat=12.9352, lon=77.6245),
                severity="medium",
                tags=["reddit", "power", "civic"],
                raw_data={"mock": True, "score": 123, "comments": 42, "post_id": "mock_rd_002"}
            ),
            Event(
                type="traffic",
                source="reddit",
                description="Daily reminder that Silk Board junction is still Bangalore's worst traffic nightmare. Lost 2 hours of my life today.",
                location="Silk Board, Bangalore",
                coordinates=Coordinates(lat=12.9173, lon=77.6221),
                severity="medium",
                tags=["reddit", "traffic", "silkboard"],
                raw_data={"mock": True, "score": 412, "comments": 89, "post_id": "mock_rd_003"}
            ),
            Event(
                type="civic",
                source="reddit",
                description="Massive pothole on Hosur Road near Bommanahalli. Saw 2 bikes fall today. This is dangerous! BBMP please take action.",
                location="Hosur Road, Bangalore",
                coordinates=Coordinates(lat=12.9150, lon=77.6380),
                severity="high",
                tags=["reddit", "pothole", "civic", "safety"],
                raw_data={"mock": True, "score": 198, "comments": 67, "post_id": "mock_rd_004"}
            ),
            Event(
                type="traffic",
                source="reddit",
                description="Traffic update: MG Road metro work causing congestion. Suggest using Vittal Mallya Road as alternative.",
                location="MG Road, Bangalore",
                coordinates=Coordinates(lat=12.9760, lon=77.6061),
                severity="low",
                tags=["reddit", "traffic", "metro"],
                raw_data={"mock": True, "score": 76, "comments": 23, "post_id": "mock_rd_005"}
            )
        ]


class SocialMediaConnector:
    """Main social media connector combining all platforms"""
    
    def __init__(self):
        self.twitter = TwitterConnector()
        self.reddit = RedditConnector()
    
    def fetch_all_events(self) -> List[Event]:
        """Fetch events from all social media sources"""
        all_events = []
        
        # Twitter
        twitter_events = self.twitter.fetch_tweets()
        all_events.extend(twitter_events)
        logger.info(f"Collected {len(twitter_events)} Twitter events")
        
        # Reddit
        reddit_events = self.reddit.fetch_posts()
        all_events.extend(reddit_events)
        logger.info(f"Collected {len(reddit_events)} Reddit events")
        
        logger.info(f"Total social media events: {len(all_events)}")
        return all_events


def main():
    """Test social media connectors"""
    print("\n" + "="*60)
    print("📱 Social Media API Connector Test")
    print("="*60 + "\n")
    
    connector = SocialMediaConnector()
    
    # Fetch events
    print("Fetching social media events...\n")
    events = connector.fetch_all_events()
    
    print(f"\n📊 Found {len(events)} social media events:\n")
    for i, event in enumerate(events, 1):
        print(f"{i}. [{event.source.upper()}] {event.description[:100]}...")
        print(f"   Type: {event.type} | Severity: {event.severity}")
        print()


if __name__ == "__main__":
    main()
