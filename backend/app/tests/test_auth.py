"""
Test Authentication Routes
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_verify_token_missing():
    """Test token verification without token"""
    response = client.post("/api/auth/verify")
    assert response.status_code == 403  # Missing authorization


def test_get_profile_unauthorized():
    """Test getting profile without authentication"""
    response = client.get("/api/auth/profile")
    assert response.status_code == 403  # Not authenticated


# Add more tests with mocked Firebase auth tokens
