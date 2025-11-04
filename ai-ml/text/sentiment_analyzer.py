"""
Sentiment Analysis Module - Member B1
NLP-based sentiment analysis with location-based aggregation

Features:
- Sentiment classification (Positive, Negative, Neutral)
- Location-based aggregation for mood mapping
- Multilingual support (English, Kannada, Hindi)
- Batch processing for multiple posts
- Integration with Hugging Face transformers
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from utils.logger import logger
from config.config import config


class SentimentAnalyzer:
    """
    Sentiment analysis for public mood mapping across Bengaluru
    """
    
    def __init__(self):
        """Initialize sentiment analyzer with model"""
        logger.info("Initializing Sentiment Analyzer...")
        
        self.config = config.text
        self.model_name = self.config.sentiment_model_name
        
        # Force CPU for Apple Silicon stability
        self.device = "cpu"
        
        # Load sentiment model
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._load_model()
        
        # Multilingual support
        self.translation_enabled = self.config.enable_multilingual
        
        # Location extraction patterns
        self.location_patterns = self._load_location_patterns()
        
        logger.success(f"✅ Sentiment Analyzer initialized on {self.device}")
    
    def _load_model(self):
        """Load pre-trained sentiment analysis model"""
        try:
            logger.info(f"Loading sentiment model: {self.model_name}")
            
            # Force CPU for Apple Silicon stability (avoid MPS backend issues)
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Disable tokenizer parallelism
            
            # Set device to CPU explicitly for stability
            self.device = "cpu"
            
            # Load tokenizer first
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True  # Use fast tokenizer for better stability
            )
            
            # Load model with explicit device mapping
            logger.info("Loading model...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Explicitly use float32 for stability
                low_cpu_mem_usage=True      # Reduce memory footprint
            )
            
            # Move to CPU explicitly
            self.model = self.model.to("cpu")
            self.model.eval()  # Set to evaluation mode
            
            # Disable gradient computation for inference
            torch.set_grad_enabled(False)
            
            # Note: We're NOT using pipeline to avoid bus errors on ARM64
            self.pipeline = None
            
            logger.success(f"✅ Model loaded: {self.model_name} on CPU (direct inference mode)")
            
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
    
    def _load_location_patterns(self) -> Dict[str, List[str]]:
        """
        Load location patterns for major Bengaluru areas
        
        Returns:
            Dictionary mapping canonical names to variations
        """
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
        """
        Clean and preprocess text for sentiment analysis
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove mentions (@username)
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags but keep the text
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove emojis (basic pattern)
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub(r'', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()
    
    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from text using pattern matching
        
        Args:
            text: Text to extract location from
            
        Returns:
            Canonical location name or None
        """
        text_lower = text.lower()
        
        # Check each location pattern
        for canonical_name, variations in self.location_patterns.items():
            for variation in variations:
                if variation in text_lower:
                    return canonical_name
        
        # Default to "Bengaluru" if no specific area found
        return "Bengaluru"
    
    def analyze_sentiment(
        self,
        text: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text
        
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
            
            # Use direct model inference instead of pipeline for stability
            # Tokenize input
            inputs = self.tokenizer(
                cleaned_text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Run inference (no gradient computation needed)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
            # Get predictions
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Map to sentiment labels
            # distilbert-sst-2 uses: 0 = NEGATIVE, 1 = POSITIVE
            sentiment_map = {0: "negative", 1: "positive"}
            sentiment = sentiment_map.get(predicted_class, "neutral")
            
            # Convert to signed score (-1 to 1)
            if sentiment == "positive":
                signed_score = confidence
            elif sentiment == "negative":
                signed_score = -confidence
            else:
                signed_score = 0.0
            
            # Extract location if not provided
            if not location:
                location = self.extract_location(text)
            
            return {
                "sentiment": sentiment,
                "score": round(signed_score, 3),
                "confidence": round(confidence, 3),
                "location": location,
                "original_text": text[:100],  # First 100 chars
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
        """
        Analyze sentiment for multiple texts
        
        Args:
            texts: List of texts to analyze
            locations: Optional list of locations (same length as texts)
            
        Returns:
            List of sentiment results
        """
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
                # Add placeholder for failed analysis
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
        """
        Aggregate sentiment scores by location for mood mapping
        
        Args:
            sentiment_results: List of sentiment analysis results
            
        Returns:
            Dictionary mapping location to aggregated sentiment
        """
        location_data = defaultdict(lambda: {
            "scores": [],
            "sentiments": [],
            "count": 0
        })
        
        # Group by location
        for result in sentiment_results:
            location = result.get("location", "Unknown")
            score = result.get("score", 0.0)
            sentiment = result.get("sentiment", "neutral")
            
            location_data[location]["scores"].append(score)
            location_data[location]["sentiments"].append(sentiment)
            location_data[location]["count"] += 1
        
        # Aggregate
        aggregated = {}
        for location, data in location_data.items():
            scores = data["scores"]
            sentiments = data["sentiments"]
            count = data["count"]
            
            # Calculate average score
            avg_score = np.mean(scores) if scores else 0.0
            
            # Determine overall sentiment
            sentiment_counts = Counter(sentiments)
            overall_sentiment = sentiment_counts.most_common(1)[0][0] if sentiments else "neutral"
            
            # Calculate sentiment distribution
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
                "confidence": self._calculate_location_confidence(count, scores)
            }
        
        return aggregated
    
    def _calculate_location_confidence(
        self,
        sample_size: int,
        scores: List[float]
    ) -> float:
        """
        Calculate confidence score for location-based sentiment
        
        Args:
            sample_size: Number of samples
            scores: List of sentiment scores
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from sample size
        size_confidence = min(sample_size / 50, 1.0)  # Max confidence at 50+ samples
        
        # Agreement confidence from score variance
        if len(scores) > 1:
            variance = np.var(scores)
            agreement_confidence = 1.0 - min(variance, 1.0)
        else:
            agreement_confidence = 0.5
        
        # Combined confidence
        confidence = (size_confidence * 0.6) + (agreement_confidence * 0.4)
        
        return round(float(confidence), 3)
    
    def create_mood_map(
        self,
        texts: List[str],
        locations: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create mood map for Bengaluru
        
        Args:
            texts: List of text posts
            locations: Optional locations for each text
            timestamp: Timestamp for the mood map
            
        Returns:
            Mood map with aggregated sentiment by location
        """
        try:
            logger.info(f"Creating mood map from {len(texts)} texts")
            
            # Batch analyze
            results = self.batch_analyze(texts, locations)
            
            # Aggregate by location
            mood_map = self.aggregate_by_location(results)
            
            # Calculate city-wide sentiment
            all_scores = [r.get("score", 0.0) for r in results if "error" not in r]
            city_score = np.mean(all_scores) if all_scores else 0.0
            
            all_sentiments = [r.get("sentiment") for r in results if "error" not in r]
            sentiment_counts = Counter(all_sentiments)
            city_sentiment = sentiment_counts.most_common(1)[0][0] if all_sentiments else "neutral"
            
            # Prepare final output
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
    
    def analyze_trend(
        self,
        historical_mood_maps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze sentiment trends over time
        
        Args:
            historical_mood_maps: List of mood maps ordered by time
            
        Returns:
            Trend analysis
        """
        if len(historical_mood_maps) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Extract city-wide scores over time
        scores = [m["city_wide"]["score"] for m in historical_mood_maps]
        
        # Calculate trend
        if len(scores) > 1:
            # Simple linear trend
            x = np.arange(len(scores))
            coeffs = np.polyfit(x, scores, 1)
            slope = coeffs[0]
            
            if slope > 0.05:
                trend = "improving"
            elif slope < -0.05:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
            slope = 0.0
        
        return {
            "trend": trend,
            "slope": round(float(slope), 4),
            "current_score": scores[-1],
            "previous_score": scores[-2] if len(scores) > 1 else None,
            "change": round(float(scores[-1] - scores[-2]), 3) if len(scores) > 1 else 0.0
        }
