#!/bin/bash

# Part 2: Map Components and Dashboard Pages

FRONTEND_DIR="/Users/kushagrakumar/Desktop/citypulseAI/frontend/src"

echo "🗺️  Generating Map Components..."

# ====================
# MAIN MAP COMPONENT
# ====================
cat > "$FRONTEND_DIR/components/map/map-view.tsx" << 'EOFILE'
'use client';

import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useMapStore } from '@/store/map';
import { useEvents } from '@/hooks/useApi';
import { Event } from '@/types';
import { getCategoryColor } from '@/lib/utils';
import SuperCluster from 'supercluster';

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

export function MapView() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  
  const { center, zoom, setCenter, setZoom, setSelectedEvent, filters } = useMapStore();
  const { data: events } = useEvents({
    category: filters.categories.length > 0 ? filters.categories.join(',') : undefined,
  });

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [center[1], center[0]],
      zoom: zoom,
    });

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    map.current.on('move', () => {
      if (map.current) {
        const center = map.current.getCenter();
        const zoom = map.current.getZoom();
        setCenter([center.lat, center.lng]);
        setZoom(zoom);
      }
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add geolocate control
    map.current.addControl(
      new mapboxgl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true,
        },
        trackUserLocation: true,
      }),
      'top-right'
    );

    return () => {
      map.current?.remove();
    };
  }, []);

  // Update markers when events change
  useEffect(() => {
    if (!map.current || !mapLoaded || !events) return;

    // Remove existing markers
    const existingMarkers = document.querySelectorAll('.event-marker');
    existingMarkers.forEach(marker => marker.remove());

    // Create clustering
    if (filters.showClusters && events.length > 50) {
      const cluster = new SuperCluster({
        radius: 60,
        maxZoom: 14,
      });

      const points = events.map((event) => ({
        type: 'Feature' as const,
        properties: { cluster: false, event },
        geometry: {
          type: 'Point' as const,
          coordinates: [event.location.lng, event.location.lat],
        },
      }));

      cluster.load(points);

      const bounds = map.current!.getBounds();
      const zoom = map.current!.getZoom();
      
      const clusters = cluster.getClusters(
        [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()],
        Math.floor(zoom)
      );

      clusters.forEach((feature) => {
        const [lng, lat] = feature.geometry.coordinates;

        if (feature.properties.cluster) {
          // Cluster marker
          const el = document.createElement('div');
          el.className = 'event-marker cluster-marker';
          el.innerHTML = `
            <div class="cluster-marker-inner" style="
              width: 40px;
              height: 40px;
              background: hsl(var(--primary));
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-center;
              color: white;
              font-weight: bold;
              cursor: pointer;
              border: 3px solid white;
              box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            ">
              ${feature.properties.point_count}
            </div>
          `;

          const marker = new mapboxgl.Marker(el)
            .setLngLat([lng, lat])
            .addTo(map.current!);

          el.addEventListener('click', () => {
            map.current!.flyTo({ center: [lng, lat], zoom: zoom + 2 });
          });
        } else {
          // Individual event marker
          const event = feature.properties.event as Event;
          createEventMarker(event);
        }
      });
    } else {
      // Show all markers without clustering
      events.forEach((event) => {
        createEventMarker(event);
      });
    }
  }, [events, mapLoaded, filters]);

  function createEventMarker(event: Event) {
    if (!map.current) return;

    const el = document.createElement('div');
    el.className = 'event-marker';
    el.style.cssText = `
      width: 30px;
      height: 30px;
      background-color: ${getCategoryColor(event.category)};
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      cursor: pointer;
      transition: transform 0.2s;
    `;

    el.addEventListener('mouseenter', () => {
      el.style.transform = 'scale(1.2)';
    });

    el.addEventListener('mouseleave', () => {
      el.style.transform = 'scale(1)';
    });

    const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
      <div style="padding: 8px; min-width: 200px;">
        <h3 style="font-weight: 600; margin-bottom: 4px;">${event.title}</h3>
        <p style="font-size: 12px; color: #666; margin-bottom: 8px;">${event.description.slice(0, 100)}...</p>
        <div style="font-size: 11px; color: #999;">
          <div>${event.category} • ${new Date(event.timestamp).toLocaleTimeString()}</div>
        </div>
      </div>
    `);

    const marker = new mapboxgl.Marker(el)
      .setLngLat([event.location.lng, event.location.lat])
      .setPopup(popup)
      .addTo(map.current);

    el.addEventListener('click', () => {
      setSelectedEvent(event);
    });
  }

  return (
    <div ref={mapContainer} className="absolute inset-0 w-full h-full" />
  );
}
EOFILE

echo "✅ Created MapView component"

# ====================
# DASHBOARD MAIN PAGE
# ====================
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/page.tsx" << 'EOFILE'
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCityStats, useEvents, useAlerts } from '@/hooks/useApi';
import { Activity, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';

export default function DashboardPage() {
  const { data: stats } = useCityStats();
  const { data: events } = useEvents();
  const { data: alerts } = useAlerts({ active: true });

  const recentEvents = events?.slice(0, 5) || [];
  const activeAlerts = alerts?.slice(0, 3) || [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time overview of city events and alerts
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Events</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_events || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active city events
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_alerts || 0}</div>
            <p className="text-xs text-muted-foreground">
              Requires attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Sentiment</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats ? `${(stats.average_sentiment * 100).toFixed(0)}%` : '0%'}
            </div>
            <p className="text-xs text-muted-foreground">
              Public mood score
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved Issues</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.resolved_issues || 0}</div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Events */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentEvents.length === 0 ? (
                <p className="text-sm text-muted-foreground">No recent events</p>
              ) : (
                recentEvents.map((event) => (
                  <div key={event.id} className="flex items-start space-x-3">
                    <div
                      className="w-2 h-2 mt-2 rounded-full"
                      style={{ backgroundColor: '#3b82f6' }}
                    />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {event.title}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {event.category} • {formatTimestamp(event.timestamp)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Active Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>Active Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeAlerts.length === 0 ? (
                <p className="text-sm text-muted-foreground">No active alerts</p>
              ) : (
                activeAlerts.map((alert) => (
                  <div key={alert.id} className="flex items-start space-x-3">
                    <AlertTriangle className="h-4 w-4 mt-1 text-orange-500" />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {alert.title}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {alert.severity} • {formatTimestamp(alert.timestamp)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
EOFILE

echo "✅ Created Dashboard page"

# ====================
# MAP PAGE
# ====================
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/map/page.tsx" << 'EOFILE'
'use client';

import dynamic from 'next/dynamic';
import { MapFilters } from '@/components/map/map-filters';
import { EventDetail } from '@/components/map/event-detail';

const MapView = dynamic(() => import('@/components/map/map-view').then(mod => ({ default: mod.MapView })), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center">Loading map...</div>,
});

export default function MapPage() {
  return (
    <div className="relative h-full">
      <MapView />
      <MapFilters />
      <EventDetail />
    </div>
  );
}
EOFILE

echo "✅ Created Map page"

echo ""
echo "🎉 Map components and dashboard pages generated!"
