'use client';

import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useMapStore } from '@/store/map';
import { useEvents } from '@/hooks/useApi';
import { Event } from '@/types';
import { getCategoryColor } from '@/lib/utils';

// Set token directly - matching the working test
mapboxgl.accessToken = 'pk.eyJ1Ijoia3VzaGFncmFrMjMiLCJhIjoiY21oYWZvNzY5MDdraTJsc2Q5N3J5eDhmbyJ9.MUAdUvj1elY_H338TIyKzA';

export function MapView() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const initializedRef = useRef(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { center = [12.9716, 77.5946], zoom = 11, setCenter, setZoom, setSelectedEvent, filters } = useMapStore();
  
  const { data: events, isLoading } = useEvents({
    category: filters?.categories?.length ? filters.categories.join(',') : undefined,
  });

  // Initialize map once
  useEffect(() => {
    if (!mapContainer.current || initializedRef.current) return;

    console.log('🗺️ Initializing map...');
    initializedRef.current = true;

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/streets-v12',
        center: [center[1], center[0]], // lng, lat
        zoom: zoom,
      });

      console.log('Map instance created');

      map.current.on('load', () => {
        console.log('✅ Map loaded!');
        setMapLoaded(true);
      });

      map.current.on('error', (e) => {
        console.error('❌ Map error:', e);
        setError(`Map error: ${e.error?.message || 'Unknown'}`);
      });

      // Add controls
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
      map.current.addControl(
        new mapboxgl.GeolocateControl({
          positionOptions: { enableHighAccuracy: true },
          trackUserLocation: true,
        }),
        'top-right'
      );

      // Update store on map movement
      map.current.on('move', () => {
        if (map.current) {
          const c = map.current.getCenter();
          const z = map.current.getZoom();
          setCenter([c.lat, c.lng]);
          setZoom(z);
        }
      });

    } catch (err: any) {
      console.error('Init error:', err);
      setError(`Failed to init: ${err.message}`);
    }
  }, []);

  // Add event markers when map loads and events are available
  useEffect(() => {
    if (!map.current || !mapLoaded || !events || events.length === 0) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    console.log(`Adding ${events.length} markers to map`);

    events.forEach((event: Event) => {
      if (!event.location) return;

      // Get coordinates - handle different formats
      const lat = event.location.latitude || event.location.lat;
      const lng = event.location.longitude || event.location.lng;
      
      if (!lat || !lng || isNaN(lat) || isNaN(lng)) return;

      // Create marker element
      const el = document.createElement('div');
      el.className = 'event-marker';
      el.style.cssText = `
        width: 24px;
        height: 24px;
        background-color: ${getCategoryColor(event.category)};
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        cursor: pointer;
      `;

      // Create popup
      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div style="padding: 8px; min-width: 200px;">
          <h3 style="font-weight: 600; margin-bottom: 4px;">${event.title}</h3>
          <p style="font-size: 12px; color: #666; margin-bottom: 8px;">
            ${event.description.slice(0, 100)}...
          </p>
          <div style="font-size: 11px; color: #999;">
            ${event.category} • ${new Date(event.timestamp).toLocaleTimeString()}
          </div>
        </div>
      `);

      // Add marker
      const marker = new mapboxgl.Marker(el)
        .setLngLat([lng, lat])
        .setPopup(popup)
        .addTo(map.current!);

      el.addEventListener('click', () => {
        setSelectedEvent(event);
      });

      markersRef.current.push(marker);
    });

  }, [mapLoaded, events]);

  // Show error
  if (error) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-red-50">
        <div className="text-center p-6 bg-white rounded-lg shadow-lg max-w-md">
          <p className="text-red-600 font-bold text-xl mb-2">❌ Map Error</p>
          <p className="text-sm text-gray-700 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="absolute inset-0">
      {/* Map container - always rendered */}
      <div ref={mapContainer} className="absolute inset-0 w-full h-full" />
      
      {/* Loading overlay */}
      {(isLoading || !mapLoaded) && (
        <div className="absolute inset-0 flex items-center justify-center bg-blue-50/90 z-10">
          <div className="text-center p-6 bg-white rounded-lg shadow-lg">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-700 font-semibold">Loading map...</p>
            <p className="text-xs text-gray-500 mt-2">
              {isLoading ? 'Fetching events...' : 'Initializing map...'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
