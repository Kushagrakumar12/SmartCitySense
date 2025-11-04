'use client';

import dynamic from 'next/dynamic';

const MoodMapView = dynamic(() => import('@/components/mood/mood-map-view').then(mod => ({ default: mod.MoodMapView })), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center">Loading mood map...</div>,
});

export default function MoodPage() {
  return (
    <div className="relative h-full">
      <MoodMapView />
    </div>
  );
}
