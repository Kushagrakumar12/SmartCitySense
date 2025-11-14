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
