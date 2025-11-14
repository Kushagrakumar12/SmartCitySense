"""
Geospatial Utilities
Helper functions for geospatial calculations
"""

from typing import Tuple, List, Dict, Any
from haversine import haversine, Unit
import structlog

logger = structlog.get_logger()


def calculate_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    unit: str = "km"
) -> float:
    """
    Calculate distance between two geographic points
    
    Args:
        point1: (latitude, longitude) tuple
        point2: (latitude, longitude) tuple
        unit: Distance unit ('km' or 'miles')
        
    Returns:
        Distance in specified unit
    """
    try:
        unit_enum = Unit.KILOMETERS if unit == "km" else Unit.MILES
        distance = haversine(point1, point2, unit=unit_enum)
        return distance
    except Exception as e:
        logger.error(f"Failed to calculate distance: {str(e)}")
        return 0.0


def is_within_radius(
    center: Tuple[float, float],
    point: Tuple[float, float],
    radius_km: float
) -> bool:
    """
    Check if a point is within radius of center point
    
    Args:
        center: (latitude, longitude) of center
        point: (latitude, longitude) of point to check
        radius_km: Radius in kilometers
        
    Returns:
        True if point is within radius
    """
    distance = calculate_distance(center, point, "km")
    return distance <= radius_km


def filter_by_location(
    items: List[Dict[str, Any]],
    center_lat: float,
    center_lng: float,
    radius_km: float
) -> List[Dict[str, Any]]:
    """
    Filter items by geographic proximity
    
    Args:
        items: List of items with 'latitude' and 'longitude' fields
        center_lat: Center point latitude
        center_lng: Center point longitude
        radius_km: Radius in kilometers
        
    Returns:
        Filtered list of items within radius
    """
    filtered = []
    center = (center_lat, center_lng)
    
    for item in items:
        try:
            if 'latitude' in item and 'longitude' in item:
                point = (item['latitude'], item['longitude'])
                if is_within_radius(center, point, radius_km):
                    # Add distance to item
                    item['distance_km'] = calculate_distance(center, point, "km")
                    filtered.append(item)
            elif 'location' in item and 'lat' in item['location'] and 'lng' in item['location']:
                point = (item['location']['lat'], item['location']['lng'])
                if is_within_radius(center, point, radius_km):
                    item['distance_km'] = calculate_distance(center, point, "km")
                    filtered.append(item)
        except Exception as e:
            logger.warning(f"Failed to process item location: {str(e)}")
            continue
    
    # Sort by distance
    filtered.sort(key=lambda x: x.get('distance_km', float('inf')))
    
    return filtered


def get_bounding_box(
    center_lat: float,
    center_lng: float,
    radius_km: float
) -> Dict[str, float]:
    """
    Calculate bounding box for a given center and radius
    
    Args:
        center_lat: Center latitude
        center_lng: Center longitude
        radius_km: Radius in kilometers
        
    Returns:
        Dictionary with min/max lat/lng
    """
    # Approximate conversion (1 degree ≈ 111 km at equator)
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * abs(center_lat / 90.0))
    
    return {
        'min_lat': center_lat - lat_delta,
        'max_lat': center_lat + lat_delta,
        'min_lng': center_lng - lng_delta,
        'max_lng': center_lng + lng_delta
    }
