"""
Test Event Routes
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_events():
    """Test listing events"""
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total" in data
    assert "page" in data


def test_list_events_with_filter():
    """Test listing events with category filter"""
    response = client.get("/api/events?category=Traffic")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data


def test_list_events_with_location():
    """Test listing events with geospatial filter"""
    response = client.get("/api/events?latitude=12.9716&longitude=77.5946&radius_km=5")
    assert response.status_code == 200


def test_get_nonexistent_event():
    """Test getting a non-existent event"""
    response = client.get("/api/events/nonexistent123")
    # Should return empty or 404 depending on implementation
    assert response.status_code in [200, 404]


# Add more tests for create, update, delete with authentication
