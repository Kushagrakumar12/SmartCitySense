import { create } from 'zustand';
import type { Event } from '@/types';

interface MapState {
  center: [number, number];
  zoom: number;
  selectedEvent: Event | null;
  filters: {
    categories: string[];
    timeRange: { start: Date; end: Date } | null;
    showClusters: boolean;
  };
  autoRefresh: boolean;
  setCenter: (center: [number, number]) => void;
  setZoom: (zoom: number) => void;
  setSelectedEvent: (event: Event | null) => void;
  setFilters: (filters: Partial<MapState['filters']>) => void;
  toggleAutoRefresh: () => void;
  reset: () => void;
}

const defaultCenter: [number, number] = [
  parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LAT || '12.9716'),
  parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LNG || '77.5946'),
];

const defaultZoom = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_ZOOM || '11');

export const useMapStore = create<MapState>((set) => ({
  center: defaultCenter,
  zoom: defaultZoom,
  selectedEvent: null,
  filters: {
    categories: [],
    timeRange: null,
    showClusters: true,
  },
  autoRefresh: true,
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
  setSelectedEvent: (event) => set({ selectedEvent: event }),
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  toggleAutoRefresh: () => set((state) => ({ autoRefresh: !state.autoRefresh })),
  reset: () =>
    set({
      center: defaultCenter,
      zoom: defaultZoom,
      selectedEvent: null,
      filters: {
        categories: [],
        timeRange: null,
        showClusters: true,
      },
    }),
}));
