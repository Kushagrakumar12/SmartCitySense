'use client';

import { useMapStore } from '@/store/map';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Filter, X } from 'lucide-react';
import { useState } from 'react';

const categories = [
  { value: 'Traffic', label: 'Traffic' },
  { value: 'Emergency', label: 'Emergency' },
  { value: 'Civic Issue', label: 'Civic Issue' },
  { value: 'Cultural', label: 'Cultural' },
  { value: 'Weather', label: 'Weather' },
];

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
                  <label key={cat.value} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={filters.categories.includes(cat.value)}
                      onChange={(e) => {
                        const newCats = e.target.checked
                          ? [...filters.categories, cat.value]
                          : filters.categories.filter((c) => c !== cat.value);
                        setFilters({ categories: newCats });
                      }}
                    />
                    <span className="text-sm">{cat.label}</span>
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
