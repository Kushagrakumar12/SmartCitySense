'use client';

import dynamic from 'next/dynamic';
import { MapFilters } from '@/components/map/map-filters';
import { EventDetail } from '@/components/map/event-detail';

const MapView = dynamic(() => import('@/components/map/map-view-simple').then(mod => ({ default: mod.MapView })), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center">Loading map...</div>,
});

export default function MapPage() {
  return (
    <div className="relative w-full flex-1 min-h-0">
      <MapView />
      <MapFilters />
      <EventDetail />
    </div>
  );
}
