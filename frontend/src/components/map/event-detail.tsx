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
