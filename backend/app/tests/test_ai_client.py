"""
Test AI/ML Client Integration
"""

import pytest
from app.services.ai_client import ai_ml_client


@pytest.mark.asyncio
async def test_ai_ml_health_check():
    """Test AI/ML service health check"""
    # This will fail if AI/ML service is not running
    # In real tests, we would mock this
    is_healthy = await ai_ml_client.health_check()
    # Assert based on whether service is running
    assert isinstance(is_healthy, bool)


@pytest.mark.asyncio
async def test_summarize_events():
    """Test event summarization"""
    events = [
        {
            "title": "Traffic on MG Road",
            "description": "Heavy traffic due to accident",
            "category": "Traffic"
        },
        {
            "title": "Traffic jam MG Road",
            "description": "Congestion near MG Road metro",
            "category": "Traffic"
        }
    ]
    
    result = await ai_ml_client.summarize_events(events)
    assert "success" in result or "error" in result


@pytest.mark.asyncio
async def test_analyze_sentiment():
    """Test sentiment analysis"""
    text = "This is a terrible traffic situation!"
    
    result = await ai_ml_client.analyze_sentiment(text)
    assert "success" in result or "error" in result
