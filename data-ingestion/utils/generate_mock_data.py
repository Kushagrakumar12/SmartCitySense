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

# Bangalore locations with coordinates
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
]

# Traffic event templates
TRAFFIC_EVENTS = [
    {
        "templates": [
            "Major accident on {location} involving {vehicles}",
            "Serious collision at {location} blocking {lanes}",
            "Multi-vehicle accident near {location}",
            "Vehicle breakdown on {location} causing delays",
        ],
        "type": "traffic",
        "subtype": "accident",
        "severity": ["high", "critical"],
        "vehicles": ["two cars", "bus and car", "truck and auto", "multiple vehicles"],
        "lanes": ["two lanes", "all lanes", "left lane", "right lanes"],
    },
    {
        "templates": [
            "Heavy traffic jam on {location} due to {reason}",
            "Severe congestion at {location}",
            "Slow moving traffic near {location}",
            "Traffic backed up for kilometers on {location}",
        ],
        "type": "traffic",
        "subtype": "congestion",
        "severity": ["medium", "high"],
        "reason": ["rush hour", "accident ahead", "road work", "signal malfunction"],
    },
    {
        "templates": [
            "{location} closed for {reason}",
            "Road closure on {location} - {reason}",
            "{location} blocked due to {reason}",
            "No entry on {location} - {reason}",
        ],
        "type": "traffic",
        "subtype": "road_closure",
        "severity": ["high", "critical"],
        "reason": ["maintenance work", "VIP movement", "protest", "construction", "waterlogging"],
    },
    {
        "templates": [
            "Road construction on {location}",
            "BBMP road repair work at {location}",
            "Ongoing construction causing delays on {location}",
            "Metro work in progress near {location}",
        ],
        "type": "traffic",
        "subtype": "construction",
        "severity": ["low", "medium"],
    },
]

# Civic event templates
CIVIC_EVENTS = [
    {
        "templates": [
            "Power outage reported in {location} by BESCOM",
            "Electricity supply disrupted in {location}",
            "Major power cut affecting {location}",
            "BESCOM reports power failure in {location}",
        ],
        "type": "civic",
        "subtype": "power_outage",
        "severity": ["high", "critical"],
    },
    {
        "templates": [
            "Water supply shortage in {location}",
            "BWSSB reports water scarcity in {location}",
            "No water supply in {location} since morning",
            "Water tankers needed in {location}",
        ],
        "type": "civic",
        "subtype": "water_shortage",
        "severity": ["medium", "high"],
    },
    {
        "templates": [
            "Garbage not collected in {location} for {days} days",
            "Waste accumulation issue at {location}",
            "Overflowing garbage bins in {location}",
            "BBMP garbage collection delayed in {location}",
        ],
        "type": "civic",
        "subtype": "garbage",
        "severity": ["medium"],
        "days": ["3", "5", "7", "10"],
    },
    {
        "templates": [
            "Large pothole reported on {location}",
            "Road damage causing accidents at {location}",
            "Multiple potholes making {location} dangerous",
            "Crater-like potholes on {location} need urgent repair",
        ],
        "type": "civic",
        "subtype": "pothole",
        "severity": ["medium", "high"],
    },
    {
        "templates": [
            "Sewage overflow on {location}",
            "Drainage system blocked at {location}",
            "Water logging due to drainage issue on {location}",
            "Manhole overflowing in {location}",
        ],
        "type": "civic",
        "subtype": "drainage",
        "severity": ["high"],
    },
]

# Emergency event templates
EMERGENCY_EVENTS = [
    {
        "templates": [
            "Fire reported at building in {location}",
            "Major fire breakout near {location}",
            "Smoke seen coming from {location}",
            "Fire brigade rushing to {location}",
        ],
        "type": "emergency",
        "subtype": "fire",
        "severity": ["critical"],
    },
    {
        "templates": [
            "Medical emergency - ambulance needed at {location}",
            "Person collapsed at {location} needs immediate help",
            "Ambulance rushing to {location}",
            "Medical assistance required urgently at {location}",
        ],
        "type": "emergency",
        "subtype": "medical",
        "severity": ["critical"],
    },
    {
        "templates": [
            "Theft reported in {location}",
            "Chain snatching incident at {location}",
            "Robbery at shop in {location}",
            "Police investigation ongoing at {location}",
        ],
        "type": "emergency",
        "subtype": "crime",
        "severity": ["high"],
    },
]

# Social event templates
SOCIAL_EVENTS = [
    {
        "templates": [
            "Protest march on {location} causing disruption",
            "Public demonstration at {location}",
            "Large gathering on {location}",
            "Rally organized near {location}",
        ],
        "type": "social",
        "subtype": "protest",
        "severity": ["medium", "high"],
    },
    {
        "templates": [
            "Festival celebration causing crowds at {location}",
            "Cultural event at {location}",
            "Public gathering for event at {location}",
            "Concert crowd at {location}",
        ],
        "type": "social",
        "subtype": "gathering",
        "severity": ["low", "medium"],
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
    """Generate comprehensive mock dataset"""
    
    events = []
    
    # Combine all event types
    all_templates = (
        TRAFFIC_EVENTS * 3 +  # More traffic events
        CIVIC_EVENTS * 2 +    # Moderate civic events
        EMERGENCY_EVENTS +    # Some emergency events
        SOCIAL_EVENTS         # Few social events
    )
    
    for i in range(num_events):
        template = random.choice(all_templates)
        location = random.choice(BANGALORE_LOCATIONS)
        event = generate_event(template, location)
        events.append(event)
    
    # Add some intentional duplicates (same event from multiple sources)
    num_duplicates = int(num_events * 0.15)  # 15% duplicates
    for i in range(num_duplicates):
        original = random.choice(events)
        duplicate = original.copy()
        duplicate["id"] = f"{original['type']}_{uuid.uuid4().hex[:8]}"
        duplicate["source"] = random.choice([s for s in SOURCES if s != original["source"]])
        duplicate["timestamp"] = get_random_time()
        # Slightly modify description
        duplicate["description"] = original["description"].replace("reported", "seen").replace("on", "at")
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
        print(f"   {t}: {count}")
    
    # Count by severity
    severity = {}
    for event in events:
        sev = event.get('severity', 'unknown')
        severity[sev] = severity.get(sev, 0) + 1
    
    print("\n⚠️  By Severity:")
    for s, count in sorted(severity.items()):
        print(f"   {s}: {count}")
    
    # Count by source
    sources = {}
    for event in events:
        src = event.get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\n📡 By Source:")
    for s, count in sorted(sources.items()):
        print(f"   {s}: {count}")
    
    # Count by zone
    zones = {}
    for event in events:
        zone = event.get('zone', 'unknown')
        zones[zone] = zones.get(zone, 0) + 1
    
    print("\n🗺️  By Zone:")
    for z, count in sorted(zones.items()):
        print(f"   {z}: {count}")
    
    # Verified count
    verified = sum(1 for e in events if e.get('verified', False))
    print(f"\n✅ Verified Events: {verified} ({verified/len(events)*100:.1f}%)")
    
    print("\n" + "="*70)


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🏭 MOCK DATA GENERATOR - Enhanced Version")
    print("="*70)
    print()
    
    # Generate different dataset sizes
    datasets = [
        (100, "data/mock/events_100.json"),
        (200, "data/mock/events_200.json"),
        (50, "data/mock/events_50_test.json"),
    ]
    
    for num_events, filename in datasets:
        print(f"\n📦 Generating {num_events} events...")
        events = generate_mock_dataset(num_events)
        save_to_file(events, filename)
        
        if num_events == 100:
            print_statistics(events)
    
    print("\n" + "="*70)
    print("✅ MOCK DATA GENERATION COMPLETE!")
    print("="*70)
    print()
    print("📁 Files created:")
    print("   • data/mock/events_100.json  - Main dataset (100 events)")
    print("   • data/mock/events_200.json  - Large dataset (200 events)")
    print("   • data/mock/events_50_test.json - Test dataset (50 events)")
    print()
    print("🧪 Usage:")
    print("   python3 main.py --mode mock --events 100")
    print()


if __name__ == "__main__":
    main()
