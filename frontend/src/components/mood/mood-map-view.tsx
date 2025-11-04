'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Smile, Frown, Meh } from 'lucide-react';
import { useSentiments } from '@/hooks/useApi';

export interface MoodData {
  location: string;
  mood: 'positive' | 'negative' | 'neutral';
  count: number;
  lat: number;
  lng: number;
}

export function MoodMapView() {
  const [moodData, setMoodData] = useState<MoodData[]>([]);
  const { data: sentiments, isLoading } = useSentiments({ limit: 100 });

  useEffect(() => {
    if (!sentiments || !sentiments.sentiments) return;

    // Group sentiments by area/city
    const areaMap = new Map<string, { sentiments: any[], lats: number[], lngs: number[] }>();
    
    sentiments.sentiments.forEach((sentiment: any) => {
      const area = sentiment.location?.area || sentiment.location?.city || 'Unknown';
      const lat = sentiment.location?.latitude || sentiment.location?.lat;
      const lng = sentiment.location?.longitude || sentiment.location?.lng;
      
      if (!areaMap.has(area)) {
        areaMap.set(area, { sentiments: [], lats: [], lngs: [] });
      }
      
      const areaData = areaMap.get(area)!;
      areaData.sentiments.push(sentiment);
      if (lat && lng) {
        areaData.lats.push(lat);
        areaData.lngs.push(lng);
      }
    });

    // Calculate mood for each area
    const processedData: MoodData[] = [];
    areaMap.forEach((data, area) => {
      if (data.sentiments.length === 0) return;
      
      const avgSentiment = data.sentiments.reduce((sum, s) => sum + (s.sentiment_score || 0.5), 0) / data.sentiments.length;
      const avgLat = data.lats.length > 0 ? data.lats.reduce((a, b) => a + b, 0) / data.lats.length : 0;
      const avgLng = data.lngs.length > 0 ? data.lngs.reduce((a, b) => a + b, 0) / data.lngs.length : 0;
      
      let mood: 'positive' | 'negative' | 'neutral';
      if (avgSentiment > 0.6) mood = 'positive';
      else if (avgSentiment < 0.4) mood = 'negative';
      else mood = 'neutral';
      
      processedData.push({
        location: area,
        mood,
        count: data.sentiments.length,
        lat: avgLat,
        lng: avgLng,
      });
    });

    setMoodData(processedData.sort((a, b) => b.count - a.count));
  }, [sentiments]);

  const getMoodIcon = (mood: MoodData['mood']) => {
    switch (mood) {
      case 'positive':
        return <Smile className="h-8 w-8 text-green-500" />;
      case 'negative':
        return <Frown className="h-8 w-8 text-red-500" />;
      case 'neutral':
        return <Meh className="h-8 w-8 text-yellow-500" />;
    }
  };

  const getMoodColor = (mood: MoodData['mood']) => {
    switch (mood) {
      case 'positive':
        return 'bg-green-100 border-green-300';
      case 'negative':
        return 'bg-red-100 border-red-300';
      case 'neutral':
        return 'bg-yellow-100 border-yellow-300';
    }
  };

  if (isLoading) {
    return <div className="h-full flex items-center justify-center">Loading mood data...</div>;
  }

  return (
    <div className="h-full p-6 space-y-6 overflow-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Mood Map</h1>
        <p className="text-muted-foreground">
          Real-time sentiment analysis across different areas
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Positive Areas</CardTitle>
            <Smile className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{moodData.filter(d => d.mood === 'positive').length}</div>
            <p className="text-xs text-muted-foreground">
              {moodData.filter(d => d.mood === 'positive').reduce((sum, d) => sum + d.count, 0)} events
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Neutral Areas</CardTitle>
            <Meh className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{moodData.filter(d => d.mood === 'neutral').length}</div>
            <p className="text-xs text-muted-foreground">
              {moodData.filter(d => d.mood === 'neutral').reduce((sum, d) => sum + d.count, 0)} events
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Negative Areas</CardTitle>
            <Frown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{moodData.filter(d => d.mood === 'negative').length}</div>
            <p className="text-xs text-muted-foreground">
              {moodData.filter(d => d.mood === 'negative').reduce((sum, d) => sum + d.count, 0)} events
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{moodData.reduce((sum, d) => sum + d.count, 0)}</div>
            <p className="text-xs text-muted-foreground">Across all areas</p>
          </CardContent>
        </Card>
      </div>

      {moodData.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No sentiment data available yet. Sentiment data is derived from event descriptions and social media analysis.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Area Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {moodData.map((area) => (
                <div
                  key={area.location}
                  className={`p-4 rounded-lg border-2 flex items-center justify-between ${getMoodColor(area.mood)}`}
                >
                  <div className="flex items-center gap-4">
                    {getMoodIcon(area.mood)}
                    <div>
                      <h3 className="font-semibold">{area.location}</h3>
                      <p className="text-sm text-muted-foreground">
                        {area.count} events • {area.mood} sentiment
                      </p>
                    </div>
                  </div>
                  {area.lat !== 0 && area.lng !== 0 && (
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">
                        {area.lat.toFixed(4)}, {area.lng.toFixed(4)}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <p className="text-sm text-blue-900">
            <strong>Note:</strong> This is a visualization of sentiment analysis from city events. 
            The mood data is derived from AI/ML sentiment analysis of event descriptions and social media data.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
