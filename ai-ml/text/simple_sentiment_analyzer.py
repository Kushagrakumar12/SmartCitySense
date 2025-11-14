"""
Simple Sentiment Analyzer - Fallback for ARM64/Python 3.13 Issues
Uses TextBlob instead of PyTorch BERT to avoid bus errors

This is a temporary workaround until you switch to Python 3.11
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

from textblob import TextBlob
import numpy as np

from utils.logger import logger
from config.config import config


class SimpleSentimentAnalyzer:
    """
    Simple sentiment analysis using TextBlob (no PyTorch required)
    This avoids bus errors on Python 3.13 + ARM64
    """
    
    def __init__(self):
        """Initialize simple sentiment analyzer"""
        logger.info("Initializing Simple Sentiment Analyzer (TextBlob-based)...")
        
        self.config = config.text
        
        # Location extraction patterns
        self.location_patterns = self._load_location_patterns()
        
        logger.success("✅ Simple Sentiment Analyzer initialized (no PyTorch)")
    
    def _load_location_patterns(self) -> Dict[str, List[str]]:
        """Load location patterns for major Bengaluru areas"""
        locations = {
            "Koramangala": ["koramangala", "kormangala", "koramangla"],
            "Indiranagar": ["indiranagar", "indira nagar", "indiranagara"],
            "Whitefield": ["whitefield", "white field", "whitefld"],
            "Electronic City": ["electronic city", "e-city", "ecity", "electronics city"],
            "HSR Layout": ["hsr", "hsr layout", "hsr sector"],
            "BTM Layout": ["btm", "btm layout"],
            "Jayanagar": ["jayanagar", "jaya nagar"],
            "Marathahalli": ["marathahalli", "marathalli", "marthahalli"],
            "Yelahanka": ["yelahanka", "yehalanka"],
            "JP Nagar": ["jp nagar", "jpnagar", "j.p. nagar"],
            "MG Road": ["mg road", "mahatma gandhi road", "m.g. road"],
            "Brigade Road": ["brigade road", "brigade rd"],
            "Bannerghatta": ["bannerghatta", "bannergatta"],
            "Hebbal": ["hebbal", "hebal"],
            "Silk Board": ["silk board", "silkboard"],
            "Bellandur": ["bellandur", "bellanduru"],
            "Sarjapur": ["sarjapur", "sarjapura"],
            "Old Airport Road": ["old airport road", "oar", "old airport"],
            "ORR": ["orr", "outer ring road", "outer ring"],
        }
        return locations
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        text_lower = text.lower()
        for canonical_name, variations in self.location_patterns.items():
            for variation in variations:
                if variation in text_lower:
                    return canonical_name
        return "Bengaluru"
    
    def analyze_sentiment(
        self,
        text: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment using TextBlob
        
        Args:
            text: Text to analyze
            location: Optional location override
            
        Returns:
            Dictionary with sentiment, score, and metadata
        """
        try:
            # Preprocess
            cleaned_text = self.preprocess_text(text)
            
            if not cleaned_text or len(cleaned_text) < 3:
                raise ValueError("Text too short after preprocessing")
            
            # Use TextBlob for sentiment analysis
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
            subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
            
            # Determine sentiment category
            if polarity > 0.1:
                sentiment = "positive"
                confidence = min(abs(polarity) + 0.2, 1.0)
            elif polarity < -0.1:
                sentiment = "negative"
                confidence = min(abs(polarity) + 0.2, 1.0)
            else:
                sentiment = "neutral"
                confidence = 0.6
            
            # Extract location if not provided
            if not location:
                location = self.extract_location(text)
            
            return {
                "sentiment": sentiment,
                "score": round(polarity, 3),
                "confidence": round(confidence, 3),
                "subjectivity": round(subjectivity, 3),
                "location": location,
                "original_text": text[:100],
                "processed_text": cleaned_text[:100]
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise
    
    def batch_analyze(
        self,
        texts: List[str],
        locations: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        results = []
        
        if locations and len(locations) != len(texts):
            raise ValueError("Locations list must match texts list length")
        
        for i, text in enumerate(texts):
            try:
                location = locations[i] if locations else None
                result = self.analyze_sentiment(text, location)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to analyze text {i}: {e}")
                results.append({
                    "sentiment": "neutral",
                    "score": 0.0,
                    "confidence": 0.0,
                    "location": locations[i] if locations else "Unknown",
                    "error": str(e)
                })
        
        logger.info(f"Batch analyzed {len(results)} texts")
        return results
    
    def aggregate_by_location(
        self,
        sentiment_results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregate sentiment scores by location"""
        location_data = defaultdict(lambda: {
            "scores": [],
            "sentiments": [],
            "count": 0
        })
        
        for result in sentiment_results:
            location = result.get("location", "Unknown")
            score = result.get("score", 0.0)
            sentiment = result.get("sentiment", "neutral")
            
            location_data[location]["scores"].append(score)
            location_data[location]["sentiments"].append(sentiment)
            location_data[location]["count"] += 1
        
        aggregated = {}
        for location, data in location_data.items():
            scores = data["scores"]
            sentiments = data["sentiments"]
            count = data["count"]
            
            avg_score = np.mean(scores) if scores else 0.0
            sentiment_counts = Counter(sentiments)
            overall_sentiment = sentiment_counts.most_common(1)[0][0] if sentiments else "neutral"
            
            total = len(sentiments)
            distribution = {
                "positive": sentiment_counts.get("positive", 0) / total if total > 0 else 0,
                "negative": sentiment_counts.get("negative", 0) / total if total > 0 else 0,
                "neutral": sentiment_counts.get("neutral", 0) / total if total > 0 else 0,
            }
            
            aggregated[location] = {
                "location": location,
                "sentiment": overall_sentiment,
                "score": round(float(avg_score), 3),
                "sample_size": count,
                "distribution": {k: round(v, 3) for k, v in distribution.items()},
                "confidence": self._calculate_confidence(count, scores)
            }
        
        return aggregated
    
    def _calculate_confidence(
        self,
        sample_size: int,
        scores: List[float]
    ) -> float:
        """Calculate confidence score"""
        size_confidence = min(sample_size / 50, 1.0)
        
        if len(scores) > 1:
            variance = np.var(scores)
            agreement_confidence = 1.0 - min(variance, 1.0)
        else:
            agreement_confidence = 0.5
        
        confidence = (size_confidence * 0.6) + (agreement_confidence * 0.4)
        return round(float(confidence), 3)
    
    def create_mood_map(
        self,
        texts: List[str],
        locations: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create mood map for Bengaluru"""
        try:
            logger.info(f"Creating mood map from {len(texts)} texts")
            
            results = self.batch_analyze(texts, locations)
            mood_map = self.aggregate_by_location(results)
            
            all_scores = [r.get("score", 0.0) for r in results if "error" not in r]
            city_score = np.mean(all_scores) if all_scores else 0.0
            
            all_sentiments = [r.get("sentiment") for r in results if "error" not in r]
            sentiment_counts = Counter(all_sentiments)
            city_sentiment = sentiment_counts.most_common(1)[0][0] if all_sentiments else "neutral"
            
            mood_map_result = {
                "timestamp": (timestamp or datetime.now()).isoformat(),
                "total_analyzed": len(texts),
                "successful_analyses": len([r for r in results if "error" not in r]),
                "city_wide": {
                    "sentiment": city_sentiment,
                    "score": round(float(city_score), 3),
                    "distribution": {
                        "positive": round(sentiment_counts.get("positive", 0) / len(all_sentiments), 3) if all_sentiments else 0,
                        "negative": round(sentiment_counts.get("negative", 0) / len(all_sentiments), 3) if all_sentiments else 0,
                        "neutral": round(sentiment_counts.get("neutral", 0) / len(all_sentiments), 3) if all_sentiments else 0,
                    }
                },
                "locations": mood_map
            }
            
            logger.success(f"✅ Mood map created with {len(mood_map)} locations")
            return mood_map_result
            
        except Exception as e:
            logger.error(f"Mood map creation failed: {e}")
            raise
