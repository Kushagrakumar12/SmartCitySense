"""
Enhanced Mock Data Generator
Generates 100+ diverse realistic city events for testing

This creates a comprehensive dataset covering:
- Traffic incidents (accidents, jams, road closures)
- Civic issues (power, water, garbage, infrastructure)
- Emergency situations (fire, medical, crime)
- Social events (protests, gatherings)
- Various Bangalore locations
- Different times of day
- Different severity levels
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Bangalore locations with coordinates - EXPANDED
BANGALORE_LOCATIONS = [
    {"name": "MG Road", "lat": 12.9716, "lon": 77.5946, "zone": "Central"},
    {"name": "Koramangala", "lat": 12.9352, "lon": 77.6245, "zone": "South"},
    {"name": "Whitefield", "lat": 12.9698, "lon": 77.7500, "zone": "East"},
    {"name": "Indiranagar", "lat": 12.9719, "lon": 77.6412, "zone": "Central"},
    {"name": "Jayanagar", "lat": 12.9250, "lon": 77.5838, "zone": "South"},
    {"name": "Hebbal", "lat": 13.0358, "lon": 77.5970, "zone": "North"},
    {"name": "Electronic City", "lat": 12.8456, "lon": 77.6603, "zone": "South"},
    {"name": "Marathahalli", "lat": 12.9591, "lon": 77.6974, "zone": "East"},
    {"name": "Silk Board", "lat": 12.9173, "lon": 77.6221, "zone": "South"},
    {"name": "Malleshwaram", "lat": 13.0050, "lon": 77.5697, "zone": "North"},
    {"name": "HSR Layout", "lat": 12.9121, "lon": 77.6446, "zone": "South"},
    {"name": "Bellandur", "lat": 12.9259, "lon": 77.6766, "zone": "East"},
    {"name": "Yeshwanthpur", "lat": 13.0280, "lon": 77.5380, "zone": "North"},
    {"name": "BTM Layout", "lat": 12.9165, "lon": 77.6101, "zone": "South"},
    {"name": "Banashankari", "lat": 12.9250, "lon": 77.5480, "zone": "South"},
    {"name": "Rajajinagar", "lat": 12.9894, "lon": 77.5544, "zone": "West"},
    {"name": "Peenya", "lat": 13.0293, "lon": 77.5197, "zone": "West"},
    {"name": "Sarjapur Road", "lat": 12.8826, "lon": 77.7213, "zone": "East"},
    {"name": "Yelahanka", "lat": 13.1007, "lon": 77.5963, "zone": "North"},
    {"name": "JP Nagar", "lat": 12.9077, "lon": 77.5859, "zone": "South"},
    # Additional locations for more diversity
    {"name": "Kengeri", "lat": 12.9077, "lon": 77.4854, "zone": "West"},
    {"name": "RT Nagar", "lat": 13.0367, "lon": 77.5970, "zone": "North"},
    {"name": "Vijayanagar", "lat": 12.9716, "lon": 77.5331, "zone": "West"},
    {"name": "Kammanahalli", "lat": 13.0112, "lon": 77.6388, "zone": "North"},
    {"name": "CV Raman Nagar", "lat": 12.9890, "lon": 77.6680, "zone": "East"},
    {"name": "Kalyan Nagar", "lat": 13.0280, "lon": 77.6394, "zone": "North"},
    {"name": "Devanahalli", "lat": 13.2472, "lon": 77.7083, "zone": "North"},
    {"name": "Kengeri Satellite Town", "lat": 12.9146, "lon": 77.4854, "zone": "West"},
    {"name": "KR Puram", "lat": 13.0117, "lon": 77.6956, "zone": "East"},
    {"name": "Domlur", "lat": 12.9606, "lon": 77.6387, "zone": "Central"},
    {"name": "Cunningham Road", "lat": 12.9927, "lon": 77.5901, "zone": "Central"},
    {"name": "Richmond Town", "lat": 12.9771, "lon": 77.6077, "zone": "Central"},
    {"name": "Shivajinagar", "lat": 12.9859, "lon": 77.6009, "zone": "Central"},
    {"name": "Frazer Town", "lat": 12.9890, "lon": 77.6206, "zone": "North"},
    {"name": "Cox Town", "lat": 12.9890, "lon": 77.6306, "zone": "North"},
    {"name": "Benson Town", "lat": 12.9967, "lon": 77.6206, "zone": "North"},
    {"name": "Nagawara", "lat": 13.0419, "lon": 77.6213, "zone": "North"},
    {"name": "Hennur", "lat": 13.0367, "lon": 77.6440, "zone": "North"},
    {"name": "Horamavu", "lat": 13.0263, "lon": 77.6607, "zone": "North"},
    {"name": "Ramamurthy Nagar", "lat": 13.0117, "lon": 77.6774, "zone": "East"},
    {"name": "Kadugodi", "lat": 12.9888, "lon": 77.7580, "zone": "East"},
    {"name": "Varthur", "lat": 12.9352, "lon": 77.7500, "zone": "East"},
    {"name": "Hoskote", "lat": 13.0719, "lon": 77.7990, "zone": "East"},
    {"name": "Jigani", "lat": 12.7770, "lon": 77.6350, "zone": "South"},
    {"name": "Attibele", "lat": 12.7770, "lon": 77.7639, "zone": "South"},
    {"name": "Bommanahalli", "lat": 12.9077, "lon": 77.6277, "zone": "South"},
    {"name": "Begur", "lat": 12.8826, "lon": 77.6350, "zone": "South"},
    {"name": "Hulimavu", "lat": 12.8701, "lon": 77.6009, "zone": "South"},
    {"name": "Gottigere", "lat": 12.8826, "lon": 77.5854, "zone": "South"},
    {"name": "Uttarahalli", "lat": 12.9021, "lon": 77.5403, "zone": "South"},
    {"name": "Subramanyapura", "lat": 12.9146, "lon": 77.5403, "zone": "South"},
    {"name": "Girinagar", "lat": 12.9352, "lon": 77.5582, "zone": "South"},
    {"name": "Basavanagudi", "lat": 12.9430, "lon": 77.5744, "zone": "South"},
    {"name": "Hanumanthanagar", "lat": 12.9352, "lon": 77.5697, "zone": "South"},
    {"name": "Wilson Garden", "lat": 12.9430, "lon": 77.5987, "zone": "South"},
    {"name": "Hosur Road", "lat": 12.9173, "lon": 77.6350, "zone": "South"},
    {"name": "Madiwala", "lat": 12.9173, "lon": 77.6213, "zone": "South"},
    {"name": "Koramangala 5th Block", "lat": 12.9352, "lon": 77.6179, "zone": "South"},
    {"name": "Koramangala 6th Block", "lat": 12.9269, "lon": 77.6179, "zone": "South"},
    {"name": "Koramangala 7th Block", "lat": 12.9269, "lon": 77.6277, "zone": "South"},
    {"name": "Koramangala 8th Block", "lat": 12.9186, "lon": 77.6277, "zone": "South"},
]

# Traffic event templates - EXPANDED WITH POSITIVE/NEGATIVE/NEUTRAL
TRAFFIC_EVENTS = [
    # NEGATIVE - Accidents
    {
        "templates": [
            "Major accident on {location} involving {vehicles}",
            "Serious collision at {location} blocking {lanes}",
            "Multi-vehicle accident near {location}",
            "Vehicle breakdown on {location} causing delays",
            "Fatal accident reported on {location}",
            "Bike accident with injuries at {location}",
            "Head-on collision on {location} - emergency services on scene",
            "Overturned truck blocking traffic on {location}",
            "School bus involved in minor accident at {location}",
            "Hit and run case reported at {location}",
        ],
        "type": "traffic",
        "subtype": "accident",
        "severity": ["high", "critical"],
        "sentiment": "negative",
        "vehicles": ["two cars", "bus and car", "truck and auto", "multiple vehicles", "bike and car", "auto and bike"],
        "lanes": ["two lanes", "all lanes", "left lane", "right lanes", "main lane"],
    },
    # NEGATIVE - Heavy Congestion
    {
        "templates": [
            "Heavy traffic jam on {location} due to {reason}",
            "Severe congestion at {location}",
            "Slow moving traffic near {location}",
            "Traffic backed up for kilometers on {location}",
            "Bumper to bumper traffic on {location}",
            "Massive gridlock at {location} junction",
            "Traffic nightmare on {location} - avoid if possible",
            "Standstill traffic reported on {location}",
            "Crawling traffic on {location} for hours",
            "Traffic chaos at {location} due to {reason}",
        ],
        "type": "traffic",
        "subtype": "congestion",
        "severity": ["medium", "high"],
        "sentiment": "negative",
        "reason": ["rush hour", "accident ahead", "road work", "signal malfunction", "heavy rain", "broken down vehicle"],
    },
    # NEGATIVE - Road Closures
    {
        "templates": [
            "{location} closed for {reason}",
            "Road closure on {location} - {reason}",
            "{location} blocked due to {reason}",
            "No entry on {location} - {reason}",
            "Complete shutdown of {location} for {reason}",
            "Emergency road closure at {location}",
            "Unexpected closure of {location}",
            "Police barricade on {location} due to {reason}",
        ],
        "type": "traffic",
        "subtype": "road_closure",
        "severity": ["high", "critical"],
        "sentiment": "negative",
        "reason": ["maintenance work", "VIP movement", "protest", "construction", "waterlogging", "tree fall", "building collapse risk"],
    },
    # NEUTRAL - Construction
    {
        "templates": [
            "Road construction on {location}",
            "BBMP road repair work at {location}",
            "Ongoing construction causing delays on {location}",
            "Metro work in progress near {location}",
            "Road widening project at {location}",
            "Infrastructure development ongoing at {location}",
            "Scheduled maintenance work on {location}",
            "Underground cable laying work at {location}",
        ],
        "type": "traffic",
        "subtype": "construction",
        "severity": ["low", "medium"],
        "sentiment": "neutral",
    },
    # POSITIVE - Smooth Traffic
    {
        "templates": [
            "Traffic flowing smoothly on {location}",
            "Clear roads reported on {location}",
            "No delays on {location} currently",
            "Free flowing traffic at {location}",
            "Easy commute on {location} today",
            "Traffic moving well on {location}",
            "No congestion on {location}",
            "Good traffic conditions at {location}",
        ],
        "type": "traffic",
        "subtype": "smooth_traffic",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # POSITIVE - Traffic Improvements
    {
        "templates": [
            "New signal installed at {location} improving traffic flow",
            "Road repair completed on {location}",
            "Traffic police managing flow efficiently at {location}",
            "New flyover at {location} reducing congestion",
            "Recently widened road at {location} helping commuters",
            "Smart traffic system working well at {location}",
            "Improved road markings at {location}",
            "New parking facility opened near {location}",
        ],
        "type": "traffic",
        "subtype": "improvement",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # NEUTRAL - Minor Issues
    {
        "templates": [
            "Minor traffic delay expected at {location}",
            "Slow traffic during peak hours at {location}",
            "Usual rush hour congestion at {location}",
            "Moderate traffic on {location}",
            "Some delays possible at {location}",
            "Traffic picking up at {location}",
        ],
        "type": "traffic",
        "subtype": "minor_delay",
        "severity": ["low", "medium"],
        "sentiment": "neutral",
    },
]

# Civic event templates - EXPANDED WITH POSITIVE/NEGATIVE/NEUTRAL
CIVIC_EVENTS = [
    # NEGATIVE - Power Issues
    {
        "templates": [
            "Power outage reported in {location} by BESCOM",
            "Electricity supply disrupted in {location}",
            "Major power cut affecting {location}",
            "BESCOM reports power failure in {location}",
            "No electricity in {location} for hours",
            "Frequent power cuts frustrating residents of {location}",
            "Transformer explosion at {location} causing outage",
            "Underground cable fault at {location}",
            "Scheduled power cut extended in {location}",
            "Emergency power shutdown at {location}",
        ],
        "type": "civic",
        "subtype": "power_outage",
        "severity": ["high", "critical"],
        "sentiment": "negative",
    },
    # NEGATIVE - Water Issues
    {
        "templates": [
            "Water supply shortage in {location}",
            "BWSSB reports water scarcity in {location}",
            "No water supply in {location} since morning",
            "Water tankers needed in {location}",
            "Acute water crisis in {location}",
            "Contaminated water reported in {location}",
            "Water pipeline burst at {location}",
            "No water supply for days in {location}",
            "Emergency water shortage at {location}",
            "Residents protesting water scarcity in {location}",
        ],
        "type": "civic",
        "subtype": "water_shortage",
        "severity": ["medium", "high"],
        "sentiment": "negative",
    },
    # NEGATIVE - Garbage Issues
    {
        "templates": [
            "Garbage not collected in {location} for {days} days",
            "Waste accumulation issue at {location}",
            "Overflowing garbage bins in {location}",
            "BBMP garbage collection delayed in {location}",
            "Stray dogs tearing garbage bags at {location}",
            "Foul smell from garbage pile at {location}",
            "Health hazard due to uncollected waste in {location}",
            "Residents complaining about garbage at {location}",
            "Waste segregation not followed in {location}",
            "Illegal dumping reported at {location}",
        ],
        "type": "civic",
        "subtype": "garbage",
        "severity": ["medium", "high"],
        "sentiment": "negative",
        "days": ["3", "5", "7", "10"],
    },
    # NEGATIVE - Road Damage
    {
        "templates": [
            "Large pothole reported on {location}",
            "Road damage causing accidents at {location}",
            "Multiple potholes making {location} dangerous",
            "Crater-like potholes on {location} need urgent repair",
            "Bikes falling due to potholes at {location}",
            "Road completely damaged at {location}",
            "Uneven road surface at {location}",
            "Speed breaker damage at {location}",
            "Road caved in at {location}",
            "Dangerous road conditions at {location}",
        ],
        "type": "civic",
        "subtype": "pothole",
        "severity": ["medium", "high"],
        "sentiment": "negative",
    },
    # NEGATIVE - Drainage Issues
    {
        "templates": [
            "Sewage overflow on {location}",
            "Drainage system blocked at {location}",
            "Water logging due to drainage issue on {location}",
            "Manhole overflowing in {location}",
            "Stormwater drain clogged at {location}",
            "Sewage water on streets of {location}",
            "Open drainage causing problems at {location}",
            "Rainwater accumulation at {location}",
            "Drainage cover missing at {location}",
            "Sewage smell in {location}",
        ],
        "type": "civic",
        "subtype": "drainage",
        "severity": ["high"],
        "sentiment": "negative",
    },
    # POSITIVE - Service Improvements
    {
        "templates": [
            "Regular garbage collection resumed in {location}",
            "BBMP cleans up {location} area",
            "Water supply restored in {location}",
            "Power backup installed in {location}",
            "Street lights working well at {location}",
            "New garbage bins installed in {location}",
            "Pothole filling completed at {location}",
            "BESCOM improves power supply to {location}",
            "BWSSB increases water supply to {location}",
            "Clean streets initiative successful in {location}",
        ],
        "type": "civic",
        "subtype": "service_improvement",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # POSITIVE - Infrastructure Development
    {
        "templates": [
            "New park inaugurated at {location}",
            "Free WiFi zone activated in {location}",
            "Public toilet facility opened at {location}",
            "BBMP beautifies {location}",
            "New bus shelter constructed at {location}",
            "Footpath repair completed at {location}",
            "Tree plantation drive successful at {location}",
            "Community center opened in {location}",
            "Sports facility improved at {location}",
            "Children's playground renovated at {location}",
        ],
        "type": "civic",
        "subtype": "development",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # NEUTRAL - Scheduled Maintenance
    {
        "templates": [
            "Scheduled power maintenance at {location}",
            "Water pipeline maintenance ongoing at {location}",
            "Road cleaning in progress at {location}",
            "Street light repair work at {location}",
            "Drainage cleaning scheduled for {location}",
            "BESCOM meter reading at {location}",
            "BWSSB inspection at {location}",
            "Routine civic maintenance at {location}",
        ],
        "type": "civic",
        "subtype": "maintenance",
        "severity": ["low", "medium"],
        "sentiment": "neutral",
    },
    # NEGATIVE - Air Quality
    {
        "templates": [
            "Poor air quality reported at {location}",
            "High pollution levels in {location}",
            "Smoke from burning waste at {location}",
            "Dust pollution due to construction at {location}",
            "Air quality unhealthy at {location}",
            "Vehicle emissions high at {location}",
        ],
        "type": "civic",
        "subtype": "air_quality",
        "severity": ["medium", "high"],
        "sentiment": "negative",
    },
    # NEGATIVE - Noise Pollution
    {
        "templates": [
            "Excessive noise pollution at {location}",
            "Construction noise disturbing residents of {location}",
            "Loud music complaint from {location}",
            "Traffic noise unbearable at {location}",
            "Generator noise issue in {location}",
        ],
        "type": "civic",
        "subtype": "noise_pollution",
        "severity": ["medium"],
        "sentiment": "negative",
    },
]

# Emergency event templates - EXPANDED
EMERGENCY_EVENTS = [
    # NEGATIVE - Fire Incidents
    {
        "templates": [
            "Fire reported at building in {location}",
            "Major fire breakout near {location}",
            "Smoke seen coming from {location}",
            "Fire brigade rushing to {location}",
            "Electrical fire at {location}",
            "Shop fire reported in {location}",
            "Apartment fire at {location}",
            "Vehicle caught fire at {location}",
            "Garbage dump fire at {location}",
            "Short circuit fire at {location}",
        ],
        "type": "emergency",
        "subtype": "fire",
        "severity": ["critical"],
        "sentiment": "negative",
    },
    # NEGATIVE - Medical Emergencies
    {
        "templates": [
            "Medical emergency - ambulance needed at {location}",
            "Person collapsed at {location} needs immediate help",
            "Ambulance rushing to {location}",
            "Medical assistance required urgently at {location}",
            "Heart attack case at {location}",
            "Accident victim needs immediate help at {location}",
            "Elderly person fell at {location}",
            "Child injured at {location}",
            "Food poisoning cases from {location}",
            "Emergency medical services at {location}",
        ],
        "type": "emergency",
        "subtype": "medical",
        "severity": ["critical", "high"],
        "sentiment": "negative",
    },
    # NEGATIVE - Crime Incidents
    {
        "templates": [
            "Theft reported in {location}",
            "Chain snatching incident at {location}",
            "Robbery at shop in {location}",
            "Police investigation ongoing at {location}",
            "Mobile phone theft at {location}",
            "Vehicle theft reported in {location}",
            "House break-in at {location}",
            "Pickpocketing incident at {location}",
            "ATM theft attempt at {location}",
            "Burglary case in {location}",
        ],
        "type": "emergency",
        "subtype": "crime",
        "severity": ["high", "medium"],
        "sentiment": "negative",
    },
    # NEGATIVE - Safety Concerns
    {
        "templates": [
            "Stray dog menace at {location}",
            "Unsafe conditions at {location}",
            "Woman harassed at {location}",
            "Eve teasing reported at {location}",
            "Suspicious activity at {location}",
            "Poor lighting making {location} unsafe",
            "Stray cattle blocking road at {location}",
            "Drunk driving case at {location}",
        ],
        "type": "emergency",
        "subtype": "safety",
        "severity": ["medium", "high"],
        "sentiment": "negative",
    },
    # POSITIVE - Emergency Services
    {
        "templates": [
            "Quick ambulance service at {location}",
            "Fire brigade successfully controlled fire at {location}",
            "Police patrol increased in {location}",
            "Emergency helpline working well at {location}",
            "Traffic police helping at {location}",
            "First aid center operational at {location}",
        ],
        "type": "emergency",
        "subtype": "service",
        "severity": ["low"],
        "sentiment": "positive",
    },
]

# Social event templates - EXPANDED
SOCIAL_EVENTS = [
    # NEGATIVE - Protests
    {
        "templates": [
            "Protest march on {location} causing disruption",
            "Public demonstration at {location}",
            "Large gathering on {location}",
            "Rally organized near {location}",
            "Strike affecting {location}",
            "Bandh observed at {location}",
            "Road blocked by protesters at {location}",
            "Agitation at {location}",
        ],
        "type": "social",
        "subtype": "protest",
        "severity": ["medium", "high"],
        "sentiment": "negative",
    },
    # POSITIVE - Cultural Events
    {
        "templates": [
            "Festival celebration at {location}",
            "Cultural event organized at {location}",
            "Music concert at {location}",
            "Art exhibition at {location}",
            "Food festival at {location}",
            "Dance performance at {location}",
            "Book fair at {location}",
            "Street art festival at {location}",
            "Yoga day celebration at {location}",
            "Sports event at {location}",
        ],
        "type": "social",
        "subtype": "cultural",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # POSITIVE - Community Activities
    {
        "templates": [
            "Community cleanup drive at {location}",
            "Blood donation camp at {location}",
            "Free health checkup at {location}",
            "Educational workshop at {location}",
            "Charity event organized at {location}",
            "Tree plantation drive at {location}",
            "Senior citizens program at {location}",
            "Children's day celebration at {location}",
            "Women empowerment event at {location}",
            "Skill development workshop at {location}",
        ],
        "type": "social",
        "subtype": "community",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # NEUTRAL - Gatherings
    {
        "templates": [
            "Public gathering expected at {location}",
            "Meeting scheduled at {location}",
            "Conference at {location}",
            "Exhibition at {location}",
            "Seminar organized at {location}",
            "Job fair at {location}",
        ],
        "type": "social",
        "subtype": "gathering",
        "severity": ["low", "medium"],
        "sentiment": "neutral",
    },
    # POSITIVE - Religious/Festive
    {
        "templates": [
            "Ganesh Chaturthi celebration at {location}",
            "Diwali lights decorating {location}",
            "Christmas event at {location}",
            "Ramadan iftar at {location}",
            "Temple festival at {location}",
            "Church fair at {location}",
            "Mosque event at {location}",
            "Ugadi celebration at {location}",
            "Holi colors at {location}",
            "New Year celebration at {location}",
        ],
        "type": "social",
        "subtype": "festival",
        "severity": ["low", "medium"],
        "sentiment": "positive",
    },
]

# Weather-related events - NEW CATEGORY
WEATHER_EVENTS = [
    # NEGATIVE - Severe Weather
    {
        "templates": [
            "Heavy rain causing waterlogging at {location}",
            "Flooding reported at {location}",
            "Storm damage at {location}",
            "Hailstorm at {location}",
            "Strong winds at {location}",
            "Rain disrupting life at {location}",
            "Waterlogged roads at {location}",
        ],
        "type": "weather",
        "subtype": "severe",
        "severity": ["high", "critical"],
        "sentiment": "negative",
    },
    # POSITIVE - Good Weather
    {
        "templates": [
            "Pleasant weather at {location}",
            "Clear skies at {location}",
            "Perfect day at {location}",
            "Beautiful sunrise at {location}",
            "Cool breeze at {location}",
            "Sunny day at {location}",
        ],
        "type": "weather",
        "subtype": "pleasant",
        "severity": ["low"],
        "sentiment": "positive",
    },
    # NEUTRAL - Weather Updates
    {
        "templates": [
            "Light drizzle at {location}",
            "Cloudy weather at {location}",
            "Humidity high at {location}",
            "Temperature rising at {location}",
            "Foggy conditions at {location}",
        ],
        "type": "weather",
        "subtype": "update",
        "severity": ["low"],
        "sentiment": "neutral",
    },
]

# Public Transport events - NEW CATEGORY
TRANSPORT_EVENTS = [
    # NEGATIVE - Issues
    {
        "templates": [
            "Bus breakdown at {location}",
            "BMTC bus delay at {location}",
            "Metro delay reported at {location}",
            "Auto strike affecting {location}",
            "No autos available at {location}",
            "Public transport issue at {location}",
            "Bus route cancelled for {location}",
        ],
        "type": "transport",
        "subtype": "issue",
        "severity": ["medium"],
        "sentiment": "negative",
    },
    # POSITIVE - Improvements
    {
        "templates": [
            "New bus route for {location}",
            "Metro connectivity improved to {location}",
            "Increased bus frequency at {location}",
            "New metro station near {location}",
            "Better public transport at {location}",
            "AC buses now serving {location}",
        ],
        "type": "transport",
        "subtype": "improvement",
        "severity": ["low"],
        "sentiment": "positive",
    },
]

# Data sources
SOURCES = ["twitter", "google_maps", "reddit", "civic_portal", "user_report", "news"]

# Time variations
def get_random_time():
    """Generate random time in the last 24 hours"""
    now = datetime.now()
    hours_ago = random.randint(0, 24)
    minutes_ago = random.randint(0, 59)
    event_time = now - timedelta(hours=hours_ago, minutes=minutes_ago)
    return event_time.isoformat()


def generate_event(template_data: Dict, location: Dict) -> Dict[str, Any]:
    """Generate a single event from template"""
    
    template = random.choice(template_data["templates"])
    
    # Fill in template
    description = template.format(
        location=location["name"],
        vehicles=random.choice(template_data.get("vehicles", [""])),
        lanes=random.choice(template_data.get("lanes", [""])),
        reason=random.choice(template_data.get("reason", [""])),
        days=random.choice(template_data.get("days", [""])),
    ).strip()
    
    # Clean up double spaces
    description = " ".join(description.split())
    
    event = {
        "id": f"{template_data['type']}_{uuid.uuid4().hex[:8]}",
        "type": template_data["type"],
        "description": description,
        "location": location["name"],
        "coordinates": {
            "lat": location["lat"],
            "lon": location["lon"]
        },
        "zone": location["zone"],
        "timestamp": get_random_time(),
        "source": random.choice(SOURCES),
        "severity": random.choice(template_data["severity"]),
        "tags": [template_data["type"], template_data.get("subtype", "")],
        "verified": random.choice([True, False, False]),  # 33% verified
    }
    
    # Add some variation to coordinates (for duplicate detection testing)
    if random.random() < 0.3:  # 30% chance of slight coordinate variation
        event["coordinates"]["lat"] += random.uniform(-0.002, 0.002)
        event["coordinates"]["lon"] += random.uniform(-0.002, 0.002)
    
    return event


def generate_mock_dataset(num_events: int = 100) -> List[Dict[str, Any]]:
    """Generate comprehensive mock dataset with balanced sentiment"""
    
    events = []
    
    # Combine all event types with weights for sentiment balance
    # Aim for: ~40% negative, ~40% neutral, ~20% positive
    all_templates = (
        TRAFFIC_EVENTS * 4 +      # Traffic is common (mix of all sentiments)
        CIVIC_EVENTS * 3 +        # Civic issues moderate (mix of all sentiments)
        EMERGENCY_EVENTS * 2 +    # Emergency events (mostly negative)
        SOCIAL_EVENTS * 2 +       # Social events (mostly positive/neutral)
        WEATHER_EVENTS * 2 +      # Weather events (mix)
        TRANSPORT_EVENTS * 1      # Transport events (mix)
    )
    
    for i in range(num_events):
        template = random.choice(all_templates)
        location = random.choice(BANGALORE_LOCATIONS)
        event = generate_event(template, location)
        
        # Add sentiment field
        event["sentiment"] = template.get("sentiment", "neutral")
        
        events.append(event)
    
    # Add minimal intentional duplicates for testing duplicate detection
    # Reduced from 10% to 3% to get more unique events through
    num_duplicates = int(num_events * 0.03)  # 3% duplicates for testing
    for i in range(num_duplicates):
        original = random.choice(events)
        duplicate = original.copy()
        duplicate["id"] = f"{original['type']}_{uuid.uuid4().hex[:8]}"
        duplicate["source"] = random.choice([s for s in SOURCES if s != original["source"]])
        duplicate["timestamp"] = get_random_time()
        # Keep description mostly the same for actual duplicate detection
        events.append(duplicate)
    
    # Shuffle events
    random.shuffle(events)
    
    return events


def save_to_file(events: List[Dict[str, Any]], filename: str):
    """Save events to JSON file"""
    with open(filename, 'w') as f:
        json.dump(events, f, indent=2)
    print(f"✓ Saved {len(events)} events to {filename}")


def print_statistics(events: List[Dict[str, Any]]):
    """Print dataset statistics"""
    print("\n" + "="*70)
    print("📊 MOCK DATASET STATISTICS")
    print("="*70)
    
    print(f"\nTotal Events: {len(events)}")
    
    # Count by type
    types = {}
    for event in events:
        types[event['type']] = types.get(event['type'], 0) + 1
    
    print("\n📋 By Type:")
    for t, count in sorted(types.items()):
        percentage = (count / len(events)) * 100
        print(f"   {t}: {count} ({percentage:.1f}%)")
    
    # Count by sentiment
    sentiments = {}
    for event in events:
        sent = event.get('sentiment', 'neutral')
        sentiments[sent] = sentiments.get(sent, 0) + 1
    
    print("\n😊 By Sentiment:")
    for s, count in sorted(sentiments.items()):
        percentage = (count / len(events)) * 100
        print(f"   {s}: {count} ({percentage:.1f}%)")
    
    # Count by severity
    severity = {}
    for event in events:
        sev = event.get('severity', 'unknown')
        severity[sev] = severity.get(sev, 0) + 1
    
    print("\n⚠️  By Severity:")
    for s, count in sorted(severity.items()):
        percentage = (count / len(events)) * 100
        print(f"   {s}: {count} ({percentage:.1f}%)")
    
    # Count by source
    sources = {}
    for event in events:
        src = event.get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\n📡 By Source:")
    for s, count in sorted(sources.items()):
        percentage = (count / len(events)) * 100
        print(f"   {s}: {count} ({percentage:.1f}%)")
    
    # Count by zone
    zones = {}
    for event in events:
        zone = event.get('zone', 'unknown')
        zones[zone] = zones.get(zone, 0) + 1
    
    print("\n🗺️  By Zone:")
    for z, count in sorted(zones.items()):
        percentage = (count / len(events)) * 100
        print(f"   {z}: {count} ({percentage:.1f}%)")
    
    # Verified count
    verified = sum(1 for e in events if e.get('verified', False))
    print(f"\n✅ Verified Events: {verified} ({verified/len(events)*100:.1f}%)")
    
    # Unique locations
    unique_locations = len(set(e['location'] for e in events))
    print(f"\n📍 Unique Locations: {unique_locations}")
    
    print("\n" + "="*70)


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🏭 MOCK DATA GENERATOR - Enhanced Version with 1000+ Events")
    print("="*70)
    print()
    
    # Generate different dataset sizes including 1000+ events
    datasets = [
        (100, "data/mock/events_100.json"),
        (200, "data/mock/events_200.json"),
        (500, "data/mock/events_500.json"),
        (1000, "data/mock/events_1000.json"),
        (1200, "data/mock/events_1200.json"),
        (50, "data/mock/events_50_test.json"),
    ]
    
    for num_events, filename in datasets:
        print(f"\n📦 Generating {num_events} events...")
        events = generate_mock_dataset(num_events)
        save_to_file(events, filename)
        
        if num_events == 1000:
            print_statistics(events)
    
    print("\n" + "="*70)
    print("✅ MOCK DATA GENERATION COMPLETE!")
    print("="*70)
    print()
    print("📁 Files created:")
    print("   • data/mock/events_100.json   - Small dataset (100 events)")
    print("   • data/mock/events_200.json   - Medium dataset (200 events)")
    print("   • data/mock/events_500.json   - Large dataset (500 events)")
    print("   • data/mock/events_1000.json  - Extra Large dataset (1000 events) ⭐")
    print("   • data/mock/events_1200.json  - Maximum dataset (1200 events) 🚀")
    print("   • data/mock/events_50_test.json - Test dataset (50 events)")
    print()
    print("🧪 Usage:")
    print("   python3 main.py --mode mock --mock-file data/mock/events_1000.json")
    print()
    print("💡 Tip: Use events_1000.json or events_1200.json for most accurate results!")
    print()


if __name__ == "__main__":
    main()
