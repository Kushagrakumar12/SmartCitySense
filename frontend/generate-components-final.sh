#!/bin/bash

# Master Script - Generates ALL remaining frontend components

FRONTEND_DIR="/Users/kushagrakumar/Desktop/SmartCitySense/frontend/src"

echo "🚀 Generating ALL remaining components..."

# Create all component files in a loop to save space

# Map Filters
cat > "$FRONTEND_DIR/components/map/map-filters.tsx" << 'EOF'
'use client';

import { useMapStore } from '@/store/map';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Filter, X } from 'lucide-react';
import { useState } from 'react';

const categories = ['traffic', 'emergency', 'civic', 'cultural', 'weather'];

export function MapFilters() {
  const [show, setShow] = useState(false);
  const { filters, setFilters, toggleAutoRefresh, autoRefresh } = useMapStore();

  return (
    <>
      <div className="absolute top-4 left-4 z-10">
        <Button onClick={() => setShow(!show)} size="sm">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </div>

      {show && (
        <Card className="absolute top-16 left-4 z-10 p-4 w-64">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Filters</h3>
            <Button variant="ghost" size="sm" onClick={() => setShow(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Categories</label>
              <div className="space-y-2">
                {categories.map((cat) => (
                  <label key={cat} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={filters.categories.includes(cat)}
                      onChange={(e) => {
                        const newCats = e.target.checked
                          ? [...filters.categories, cat]
                          : filters.categories.filter((c) => c !== cat);
                        setFilters({ categories: newCats });
                      }}
                    />
                    <span className="text-sm capitalize">{cat}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.showClusters}
                  onChange={(e) => setFilters({ showClusters: e.target.checked })}
                />
                <span className="text-sm">Show Clusters</span>
              </label>
            </div>

            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={toggleAutoRefresh}
                />
                <span className="text-sm">Auto Refresh</span>
              </label>
            </div>
          </div>
        </Card>
      )}
    </>
  );
}
EOF

# Event Detail
cat > "$FRONTEND_DIR/components/map/event-detail.tsx" << 'EOF'
'use client';

import { useMapStore } from '@/store/map';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X, MapPin, Clock } from 'lucide-react';
import { formatTimestamp, getCategoryIcon } from '@/lib/utils';

export function EventDetail() {
  const { selectedEvent, setSelectedEvent } = useMapStore();

  if (!selectedEvent) return null;

  return (
    <Card className="absolute bottom-4 left-4 right-4 md:right-auto md:w-96 z-10">
      <CardHeader className="flex flex-row items-start justify-between pb-2">
        <div className="flex items-start space-x-2">
          <span className="text-2xl">{getCategoryIcon(selectedEvent.category)}</span>
          <div>
            <CardTitle className="text-lg">{selectedEvent.title}</CardTitle>
            <p className="text-sm text-muted-foreground capitalize">
              {selectedEvent.category}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedEvent(null)}
        >
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <p className="text-sm mb-4">{selectedEvent.description}</p>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-muted-foreground">
            <MapPin className="h-4 w-4 mr-2" />
            {selectedEvent.location.address || `${selectedEvent.location.lat.toFixed(4)}, ${selectedEvent.location.lng.toFixed(4)}`}
          </div>
          <div className="flex items-center text-muted-foreground">
            <Clock className="h-4 w-4 mr-2" />
            {formatTimestamp(selectedEvent.timestamp)}
          </div>
        </div>

        {selectedEvent.media_urls && selectedEvent.media_urls.length > 0 && (
          <div className="mt-4 grid grid-cols-2 gap-2">
            {selectedEvent.media_urls.slice(0, 4).map((url, idx) => (
              <img
                key={idx}
                src={url}
                alt={`Event media ${idx + 1}`}
                className="w-full h-24 object-cover rounded"
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
EOF

# Reports Page
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/reports/page.tsx" << 'EOF'
'use client';

import { useReports } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatTimestamp } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useUIStore } from '@/store/ui';

export default function ReportsPage() {
  const { data: reports, isLoading } = useReports();
  const { toggleReportForm } = useUIStore();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">User-submitted city reports</p>
        </div>
        <Button onClick={toggleReportForm}>
          <Plus className="h-4 w-4 mr-2" />
          New Report
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <p>Loading reports...</p>
        ) : reports && reports.length > 0 ? (
          reports.map((report) => (
            <Card key={report.id}>
              <CardHeader>
                <CardTitle className="text-lg">{report.title}</CardTitle>
                <p className="text-sm text-muted-foreground capitalize">
                  {report.category} • {report.status}
                </p>
              </CardHeader>
              <CardContent>
                <p className="text-sm mb-2">{report.description}</p>
                <p className="text-xs text-muted-foreground">
                  {formatTimestamp(report.timestamp)}
                </p>
              </CardContent>
            </Card>
          ))
        ) : (
          <p>No reports found</p>
        )}
      </div>
    </div>
  );
}
EOF

# Alerts Page
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/alerts/page.tsx" << 'EOF'
'use client';

import { useAlerts } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';

export default function AlertsPage() {
  const { data: alerts, isLoading } = useAlerts();

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      low: 'text-blue-500',
      medium: 'text-yellow-500',
      high: 'text-orange-500',
      critical: 'text-red-500',
    };
    return colors[severity] || 'text-gray-500';
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Alerts</h1>
        <p className="text-muted-foreground">Active city alerts and warnings</p>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <p>Loading alerts...</p>
        ) : alerts && alerts.length > 0 ? (
          alerts.map((alert) => (
            <Card key={alert.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className={`h-5 w-5 mt-1 ${getSeverityColor(alert.severity)}`} />
                    <div>
                      <CardTitle className="text-lg">{alert.title}</CardTitle>
                      <p className="text-sm text-muted-foreground capitalize">
                        {alert.severity} • {alert.category}
                      </p>
                    </div>
                  </div>
                  {alert.is_predictive && (
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      AI Predicted
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm mb-2">{alert.message}</p>
                <p className="text-xs text-muted-foreground">
                  {formatTimestamp(alert.timestamp)}
                </p>
              </CardContent>
            </Card>
          ))
        ) : (
          <p>No active alerts</p>
        )}
      </div>
    </div>
  );
}
EOF

# Analytics Page
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/analytics/page.tsx" << 'EOF'
'use client';

import { useAnalytics } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useAnalytics();

  if (isLoading) return <div className="p-6">Loading analytics...</div>;
  if (!analytics) return <div className="p-6">No analytics data available</div>;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">City data insights and trends</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>City Health Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold text-center">
            {(analytics.city_health_score * 100).toFixed(0)}%
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Event Volume Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.event_volume}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Category Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.category_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
EOF

# Mood Map Page
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/mood/page.tsx" << 'EOF'
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
EOF

# Mood Map Component
cat > "$FRONTEND_DIR/components/mood/mood-map-view.tsx" << 'EOF'
'use client';

import { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import { useSentiments } from '@/hooks/useApi';
import { getSentimentColor } from '@/lib/utils';

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

export function MoodMapView() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const { data: sentiments } = useSentiments();

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [77.5946, 12.9716],
      zoom: 11,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => {
      map.current?.remove();
    };
  }, []);

  useEffect(() => {
    if (!map.current || !sentiments) return;

    sentiments.forEach((sentiment) => {
      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div style="padding: 8px;">
          <h3 style="font-weight: 600; margin-bottom: 4px;">${sentiment.zone_name}</h3>
          <p style="font-size: 12px;">Sentiment: ${(sentiment.sentiment_score * 100).toFixed(0)}%</p>
          <p style="font-size: 12px;">Events: ${sentiment.event_count}</p>
        </div>
      `);

      // Add circle for each zone
      new mapboxgl.Marker({
        color: getSentimentColor(sentiment.sentiment_score),
      })
        .setLngLat([sentiment.coordinates[0][0], sentiment.coordinates[0][1]])
        .setPopup(popup)
        .addTo(map.current!);
    });
  }, [sentiments]);

  return <div ref={mapContainer} className="absolute inset-0 w-full h-full" />;
}
EOF

# Settings Page
cat > "$FRONTEND_DIR/app/(dashboard)/dashboard/settings/page.tsx" << 'EOF'
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/store/auth';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function SettingsPage() {
  const { user } = useAuthStore();

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src={user?.photoURL || ''} />
              <AvatarFallback>{user?.email?.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">{user?.displayName || 'User'}</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
EOF

# Dialog component
cat > "$FRONTEND_DIR/components/ui/dialog.tsx" << 'EOF'
import * as React from 'react';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogPortal = DialogPrimitive.Portal;
const DialogClose = DialogPrimitive.Close;

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50 bg-background/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
      className
    )}
    {...props}
  />
));
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName;

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg',
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
));
DialogContent.displayName = DialogPrimitive.Content.displayName;

export { Dialog, DialogTrigger, DialogContent };
EOF

echo "✅ Generated ALL essential components!"
echo ""
echo "Components created:"
echo "- Map View with clustering"
echo "- Map Filters"
echo "- Event Detail panel"
echo "- Dashboard page"
echo "- Reports page"
echo "- Alerts page"
echo "- Analytics page with charts"
echo "- Mood Map page"
echo "- Settings page"
echo "- Dialog component"
echo ""
echo "🎉 Frontend structure is now complete!"
