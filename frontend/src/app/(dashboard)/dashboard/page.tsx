'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCityStats, useEvents, useAlerts } from '@/hooks/useApi';
import { Activity, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useCityStats();
  const { data: events, isLoading: eventsLoading, error: eventsError } = useEvents();
  const { data: alerts, isLoading: alertsLoading, error: alertsError } = useAlerts({ active: true });

  const recentEvents = events?.slice(0, 5) || [];
  const activeAlerts = alerts?.slice(0, 3) || [];

  // Debug logging
  if (typeof window !== 'undefined') {
    console.log('[Dashboard] Stats:', stats, 'Loading:', statsLoading, 'Error:', statsError);
    console.log('[Dashboard] Events:', events?.length, 'Loading:', eventsLoading, 'Error:', eventsError);
    console.log('[Dashboard] Alerts:', alerts?.length, 'Loading:', alertsLoading, 'Error:', alertsError);
  }

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
