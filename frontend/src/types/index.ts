export interface Event {
  id: string;
  title: string;
  description: string;
  category: string;
  severity?: string;
  location: {
    latitude?: number;
    longitude?: number;
    lat?: number;
    lng?: number;
    address?: string;
    area?: string;
    city?: string;
  };
  sentiment_score?: number | null;
  sentiment_label?: string;
  timestamp: string;
  source: string;
  status?: string;
  media_urls?: string[];
  affected_count?: number;
  upvotes?: number;
  report_count?: number;
  tags?: string[];
  reported_by?: string | null;
  updated_at?: string | null;
}

export interface Report {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category: 'traffic' | 'emergency' | 'civic' | 'cultural' | 'weather';
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  media_urls?: string[];
  timestamp: string;
  status: 'pending' | 'verified' | 'resolved';
  ai_summary?: string;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  location: {
    lat: number;
    lng: number;
    radius: number;
  };
  timestamp: string;
  expires_at?: string;
  is_predictive: boolean;
}

export interface Sentiment {
  zone_id: string;
  zone_name: string;
  coordinates: number[][];
  sentiment_score: number;
  dominant_emotion: 'positive' | 'neutral' | 'negative';
  event_count: number;
  timestamp: string;
}

export interface User {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  subscriptions: Subscription[];
}

export interface Subscription {
  id: string;
  user_id: string;
  area: {
    type: 'circle' | 'polygon';
    coordinates: number[] | number[][];
    radius?: number;
  };
  categories: string[];
  keywords: string[];
  notification_channels: ('push' | 'email')[];
  created_at: string;
}

export interface CityStats {
  total_events: number;
  active_alerts: number;
  average_sentiment: number;
  traffic_intensity: number;
  resolved_issues: number;
}

export interface EventCluster {
  id: string;
  latitude: number;
  longitude: number;
  point_count: number;
  events: Event[];
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  category?: string;
}

export interface AnalyticsData {
  event_volume: TimeSeriesData[];
  sentiment_trend: TimeSeriesData[];
  category_distribution: { category: string; count: number }[];
  top_areas: { area: string; count: number; lat: number; lng: number }[];
  city_health_score: number;
}
