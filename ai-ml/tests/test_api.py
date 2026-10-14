"""Test suite for API endpoints"""
import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image
from unittest.mock import patch

from main import app
from utils.schemas import EventType, SeverityLevel, VisionAnalysisResponse


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing"""
    img = Image.new('RGB', (640, 640), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    def test_health_check(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'models_loaded' in data
        assert 'gpu_available' in data


class TestVisionEndpoints:
    """Test vision analysis endpoints"""
    
    def test_analyze_image(self, client, sample_image_file):
        """Test image analysis endpoint"""
        mock_classifier = patch("main.get_vision_classifier")
        with mock_classifier as get_classifier:
            get_classifier.return_value.classify_image.return_value = VisionAnalysisResponse(
                event_type=EventType.OTHER,
                description="Mocked image result",
                confidence=0.9,
                severity=SeverityLevel.LOW,
                processing_time_ms=1,
            )
            response = client.post(
                "/ai/vision/image",
                files={"file": ("test.jpg", sample_image_file, "image/jpeg")},
                data={"location": "Test Location"}
            )
        
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert 'event_type' in data
            assert 'confidence' in data
            assert 'description' in data
    
    def test_analyze_image_invalid_file(self, client):
        """Test image analysis with invalid file"""
        text_file = io.BytesIO(b"not an image")
        response = client.post(
            "/ai/vision/image",
            files={"file": ("test.txt", text_file, "text/plain")}
        )
        
        assert response.status_code == 415

    def test_analyze_image_rejects_invalid_image(self, client):
        response = client.post(
            "/ai/vision/image",
            files={"file": ("test.jpg", io.BytesIO(b"not an image"), "image/jpeg")}
        )
        assert response.status_code == 400

    def test_analyze_image_rejects_oversized_upload(self, client, monkeypatch):
        monkeypatch.setattr("main.config.api.max_upload_size_mb", 1)
        response = client.post(
            "/ai/vision/image",
            files={"file": ("test.jpg", io.BytesIO(b"x" * (1024 * 1024 + 1)), "image/jpeg")}
        )
        assert response.status_code == 413


class TestPredictiveEndpoints:
    """Test predictive analysis endpoints"""
    
    def test_detect_anomaly(self, client):
        """Test anomaly detection endpoint"""
        request_data = {
            "location": "MG Road",
            "time_window_minutes": 15
        }
        
        response = client.post("/ai/predict/anomaly", json=request_data)
        
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert 'severity' in data
            assert 'processing_time_ms' in data
    
    def test_forecast_events(self, client):
        """Test forecast endpoint"""
        request_data = {
            "forecast_hours": 12
        }
        
        response = client.post("/ai/predict/forecast", json=request_data)
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
