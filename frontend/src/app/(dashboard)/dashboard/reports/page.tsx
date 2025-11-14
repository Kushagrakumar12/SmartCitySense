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
