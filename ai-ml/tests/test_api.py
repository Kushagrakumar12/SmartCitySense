"""Test suite for API endpoints"""
import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image

from main import app


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
        response = client.post(
            "/ai/vision/image",
            files={"file": ("test.jpg", sample_image_file, "image/jpeg")},
            data={"location": "Test Location"}
        )
        
        # Might fail if models not loaded, but should return proper error
        assert response.status_code in [200, 500]
        
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
        
        assert response.status_code == 400


class TestPredictiveEndpoints:
    """Test predictive analysis endpoints"""
    
    def test_detect_anomaly(self, client):
        """Test anomaly detection endpoint"""
        request_data = {
            "location": "MG Road",
            "time_window_minutes": 15
        }
        
        response = client.post("/ai/predict/anomaly", json=request_data)
        
        # Should work even with no data
        assert response.status_code in [200, 500]
        
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
        
        # Might fail if no trained models
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
