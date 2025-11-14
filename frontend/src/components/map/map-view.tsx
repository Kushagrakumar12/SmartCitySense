'use client';

import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useMapStore } from '@/store/map';
import { useEvents } from '@/hooks/useApi';
import { Event } from '@/types';
import { getCategoryColor } from '@/lib/utils';
import SuperCluster from 'supercluster';

// Set token directly
mapboxgl.accessToken = 'pk.eyJ1Ijoia3VzaGFncmFrMjMiLCJhIjoiY21oYWZvNzY5MDdraTJsc2Q5N3J5eDhmbyJ9.MUAdUvj1elY_H338TIyKzA';

export function MapView() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const mapStore = useMapStore();
  const { center = [12.9716, 77.5946], zoom = 11, setCenter, setZoom, setSelectedEvent, filters } = mapStore || {};
  
  const eventsQuery = useEvents({
    category: filters?.categories?.length ? filters.categories.join(',') : undefined,
  });
  
  const events = eventsQuery?.data;
  const isLoading = eventsQuery?.isLoading ?? true;
  const apiError = eventsQuery?.error;

  // Log API status
  useEffect(() => {
    try {
      console.log('MapView - Events data:', events ? `${events.length} events` : 'No events');
      console.log('MapView - Loading:', isLoading);
      console.log('MapView - API Error:', apiError);
      if (apiError) {
        const errorMessage = apiError instanceof Error ? apiError.message : String(apiError);
        setError(`Failed to load events: ${errorMessage}`);
      }
    } catch (err) {
      console.error('Error in log effect:', err);
    }
  }, [events, isLoading, apiError]);

  // Check for Mapbox token
  useEffect(() => {
    if (!mapboxgl.accessToken) {
      setError('Mapbox token is not configured');
      console.error('NEXT_PUBLIC_MAPBOX_TOKEN is not set');
    } else {
      console.log('Mapbox token is configured:', mapboxgl.accessToken.substring(0, 20) + '...');
    }
  }, []);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;
    
    console.log('MapContainer ref:', mapContainer.current);
    console.log('Container dimensions:', {
      width: mapContainer.current.offsetWidth,
      height: mapContainer.current.offsetHeight,
      clientWidth: mapContainer.current.clientWidth,
      clientHeight: mapContainer.current.clientHeight
    });
    
    // Don't initialize if container has no dimensions
    if (mapContainer.current.offsetHeight === 0 || mapContainer.current.offsetWidth === 0) {
      console.warn('Map container has no dimensions, waiting...');
      return;
    }
    
    console.log('Attempting to initialize map...');

    console.log('Initializing map with center:', [center[1], center[0]], 'zoom:', zoom);
    console.log('Mapbox token:', mapboxgl.accessToken ? 'Set' : 'Missing');

    try {
      console.log('Creating Mapbox Map instance...');
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/streets-v12',
        center: [center[1], center[0]], // Mapbox expects [lng, lat]
        zoom: zoom,
      });
      
      console.log('Map instance created, waiting for load event...');

      // Set a timeout to detect if load event never fires
      const loadTimeout = setTimeout(() => {
        if (!mapLoaded) {
          console.error('❌ Map load event never fired after 15 seconds');
          setError('Unable to load map. Please check your internet connection or try again later.');
          setMapLoaded(true); // Stop showing loading spinner
        }
      }, 15000);

      map.current.on('load', () => {
        console.log('🎉 Map loaded successfully!');
        clearTimeout(loadTimeout);
        setMapLoaded(true);
      });

      map.current.on('error', (e) => {
        console.error('❌ Map error:', e);
        clearTimeout(loadTimeout);
        setError('Map failed to load: ' + (e.error?.message || 'Unknown error'));
        setMapLoaded(true); // Stop showing loading spinner
      });
      
      map.current.on('style.load', () => {
        console.log('📍 Map style loaded');
      });
      
      map.current.on('data', (e) => {
        if (e.dataType === 'source' && e.isSourceLoaded) {
          console.log('📊 Map data loaded');
        }
      });
    } catch (error: any) {
      console.error('Map initialization error:', error);
      setError('Failed to initialize map: ' + error.message);
    }

    if (!map.current) return;

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
    console.log('Marker effect triggered:', { 
      hasMap: !!map.current, 
      mapLoaded, 
      eventsCount: events?.length || 0 
    });
    
    if (!map.current || !mapLoaded || !events) return;

    // Remove existing markers
    const existingMarkers = document.querySelectorAll('.event-marker');
    existingMarkers.forEach(marker => marker.remove());

    console.log(`🗺️ Rendering ${events.length} events on map`);

    // Create clustering
    if (filters.showClusters && events.length > 50) {
      const cluster = new SuperCluster({
        radius: 60,
        maxZoom: 14,
      });

      const points = events
        .filter(event => {
          const lng = event.location.longitude || event.location.lng;
          const lat = event.location.latitude || event.location.lat;
          return lng && lat && lng !== 0 && lat !== 0;
        })
        .map((event) => ({
          type: 'Feature' as const,
          properties: { cluster: false, event },
          geometry: {
            type: 'Point' as const,
            coordinates: [
              event.location.longitude || event.location.lng || 0,
              event.location.latitude || event.location.lat || 0
            ],
          },
        }));

      cluster.load(points);

      const bounds = map.current!.getBounds();
      const zoom = map.current!.getZoom();
      
      if (bounds) {
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
      }
    } else {
      // Show all markers without clustering
      events.forEach((event) => {
        createEventMarker(event);
      });
    }
  }, [events, mapLoaded, filters]);

  function createEventMarker(event: Event) {
    if (!map.current) return;

    const lng = event.location.longitude || event.location.lng || 0;
    const lat = event.location.latitude || event.location.lat || 0;

    if (lng === 0 || lat === 0) return; // Skip events without valid coordinates

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
      .setLngLat([lng, lat])
      .setPopup(popup)
      .addTo(map.current);

    el.addEventListener('click', () => {
      setSelectedEvent(event);
    });
  }

  return (
    <div className="absolute inset-0" style={{ minHeight: '400px' }}>
      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg">
          {error}
        </div>
      )}
      {(isLoading || !mapLoaded) && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-900 z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">
              {isLoading ? 'Loading events...' : 'Loading map...'}
            </p>
          </div>
        </div>
      )}
      <div ref={mapContainer} className="absolute inset-0 w-full h-full" style={{ minHeight: '400px' }} />
    </div>
  );
}
