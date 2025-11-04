"""
AI/ML Client
Communicates with the AI/ML service for summarization, vision analysis, and predictions
"""

import httpx
from typing import Dict, Any, List, Optional
import structlog

from app.config import settings

logger = structlog.get_logger()


class AIMLClient:
    """Client for AI/ML service integration"""
    
    def __init__(self):
        self.base_url = settings.AI_ML_SERVICE_URL
        self.timeout = 30.0
    
    async def summarize_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize multiple events into a single coherent summary
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with summary text and metadata
        """
        try:
            url = f"{self.base_url}{settings.SUMMARIZATION_ENDPOINT}"
            
            payload = {
                "events": events
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully summarized {len(events)} events")
                return result
                
        except httpx.TimeoutException:
            logger.error("AI/ML service timeout during summarization")
            return {
                "success": False,
                "error": "Summarization service timeout"
            }
        except httpx.HTTPError as e:
            logger.error(f"AI/ML service error during summarization: {str(e)}")
            return {
                "success": False,
                "error": f"Summarization service error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def analyze_image(self, image_url: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze image using vision model
        
        Args:
            image_url: URL of the image to analyze
            context: Optional context about the image
            
        Returns:
            Dictionary with analysis results
        """
        try:
            url = f"{self.base_url}{settings.VISION_ANALYSIS_ENDPOINT}"
            
            payload = {
                "image_url": image_url,
                "context": context
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully analyzed image: {image_url}")
                return result
                
        except httpx.TimeoutException:
            logger.error("AI/ML service timeout during image analysis")
            return {
                "success": False,
                "error": "Vision analysis service timeout"
            }
        except httpx.HTTPError as e:
            logger.error(f"AI/ML service error during image analysis: {str(e)}")
            return {
                "success": False,
                "error": f"Vision analysis service error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during image analysis: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment score and classification
        """
        try:
            url = f"{self.base_url}{settings.SENTIMENT_ENDPOINT}"
            
            payload = {
                "text": text
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info("Successfully analyzed sentiment")
                return result
                
        except httpx.TimeoutException:
            logger.error("AI/ML service timeout during sentiment analysis")
            return {
                "success": False,
                "error": "Sentiment analysis service timeout"
            }
        except httpx.HTTPError as e:
            logger.error(f"AI/ML service error during sentiment analysis: {str(e)}")
            return {
                "success": False,
                "error": f"Sentiment analysis service error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during sentiment analysis: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def detect_anomalies(self, events: List[Dict[str, Any]], time_window: str = "1h") -> Dict[str, Any]:
        """
        Detect anomalies in event stream
        
        Args:
            events: List of event dictionaries
            time_window: Time window for analysis (e.g., "1h", "6h", "24h")
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            url = f"{self.base_url}{settings.ANOMALY_DETECTION_ENDPOINT}"
            
            payload = {
                "events": events,
                "time_window": time_window
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully detected anomalies in {len(events)} events")
                return result
                
        except httpx.TimeoutException:
            logger.error("AI/ML service timeout during anomaly detection")
            return {
                "success": False,
                "error": "Anomaly detection service timeout"
            }
        except httpx.HTTPError as e:
            logger.error(f"AI/ML service error during anomaly detection: {str(e)}")
            return {
                "success": False,
                "error": f"Anomaly detection service error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during anomaly detection: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def health_check(self) -> bool:
        """
        Check if AI/ML service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/health"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
                
        except:
            return False


# Singleton instance
ai_ml_client = AIMLClient()


def get_ai_ml_client() -> AIMLClient:
    """Get AI/ML client instance"""
    return ai_ml_client
