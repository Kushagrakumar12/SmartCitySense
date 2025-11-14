'use client';

import { useState } from 'react';
import { useUIStore } from '@/store/ui';
import { useCreateReport } from '@/hooks/useApi';
import { X, Upload, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';

export function ReportForm() {
  const { reportFormOpen, toggleReportForm } = useUIStore();
  const createReport = useCreateReport();
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'civic',
    location: {
      latitude: 0,
      longitude: 0,
      address: '',
    },
  });

  const [useCurrentLocation, setUseCurrentLocation] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);

  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by your browser');
      return;
    }

    setUseCurrentLocation(true);
    toast.loading('Getting your location...');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setFormData(prev => ({
          ...prev,
          location: {
            ...prev.location,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          },
        }));
        toast.dismiss();
        toast.success('Location obtained!');
        setUseCurrentLocation(false);
      },
      (error) => {
        toast.dismiss();
        toast.error('Unable to get location: ' + error.message);
        setUseCurrentLocation(false);
      }
    );
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const newFiles = Array.from(files);
    
    // Limit to 5 photos
    if (selectedFiles.length + newFiles.length > 5) {
      toast.error('Maximum 5 photos allowed');
      return;
    }

    // Check file sizes (max 5MB each)
    for (const file of newFiles) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error(`${file.name} is too large. Maximum size is 5MB`);
        return;
      }
      if (!file.type.startsWith('image/')) {
        toast.error(`${file.name} is not an image file`);
        return;
      }
    }

    // Add files and create preview URLs
    setSelectedFiles(prev => [...prev, ...newFiles]);
    
    const newPreviewUrls = newFiles.map(file => URL.createObjectURL(file));
    setPreviewUrls(prev => [...prev, ...newPreviewUrls]);
  };

  const removeFile = (index: number) => {
    // Revoke the URL to free memory
    URL.revokeObjectURL(previewUrls[index]);
    
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviewUrls(prev => prev.filter((_, i) => i !== index));
  };

  // Map form values to backend enum values
  const categoryMap: Record<string, string> = {
    'civic': 'Civic Issue',
    'traffic': 'Traffic',
    'emergency': 'Emergency',
    'cultural': 'Cultural',
    'weather': 'Weather',
    'power': 'Power Outage',
    'water': 'Water Supply',
    'protest': 'Protest',
    'construction': 'Construction',
    'other': 'Other'
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (formData.location.latitude === 0 || formData.location.longitude === 0) {
      toast.error('Please provide a location');
      return;
    }

    try {
      const reportFormData = new FormData();
      reportFormData.append('title', formData.title);
      reportFormData.append('description', formData.description);
      reportFormData.append('category', categoryMap[formData.category] || formData.category);
      reportFormData.append('latitude', formData.location.latitude.toString());
      reportFormData.append('longitude', formData.location.longitude.toString());
      reportFormData.append('address', formData.location.address);

      // Add photos to FormData
      selectedFiles.forEach((file, index) => {
        reportFormData.append('photos', file);
      });

      await createReport.mutateAsync(reportFormData);
      
      toast.success('Report submitted successfully!');
      toggleReportForm();
      
      // Clean up preview URLs
      previewUrls.forEach(url => URL.revokeObjectURL(url));
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        category: 'civic',
        location: {
          latitude: 0,
          longitude: 0,
          address: '',
        },
      });
      setSelectedFiles([]);
      setPreviewUrls([]);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to submit report');
    }
  };

  if (!reportFormOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold">Submit a Report</h2>
          <button
            onClick={toggleReportForm}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-700"
              placeholder="Brief summary of the issue"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-700"
              placeholder="Detailed description of the issue"
              rows={4}
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-700"
              required
            >
              <option value="civic">Civic Issue</option>
              <option value="traffic">Traffic</option>
              <option value="emergency">Emergency</option>
              <option value="cultural">Cultural</option>
              <option value="weather">Weather</option>
              <option value="power">Power Outage</option>
              <option value="water">Water Supply</option>
              <option value="protest">Protest</option>
              <option value="construction">Construction</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Location <span className="text-red-500">*</span>
            </label>
            <div className="space-y-3">
              <button
                type="button"
                onClick={handleGetLocation}
                disabled={useCurrentLocation}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <MapPin className="h-4 w-4" />
                {useCurrentLocation ? 'Getting location...' : 'Use Current Location'}
              </button>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={formData.location.latitude || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      location: { ...formData.location, latitude: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 text-sm"
                    placeholder="0.0"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={formData.location.longitude || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      location: { ...formData.location, longitude: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 text-sm"
                    placeholder="0.0"
                    required
                  />
                </div>
              </div>

              <input
                type="text"
                value={formData.location.address}
                onChange={(e) => setFormData({
                  ...formData,
                  location: { ...formData.location, address: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-700"
                placeholder="Address or landmark (optional)"
              />
            </div>
          </div>

          {/* Photo Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Photos (optional)
            </label>
            
            {/* File Input (hidden) */}
            <input
              type="file"
              id="photo-upload"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              className="hidden"
            />
            
            {/* Upload Button */}
            <label
              htmlFor="photo-upload"
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-primary hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors block"
            >
              <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Click to upload photos
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                PNG, JPG up to 5MB each (max 5 photos)
              </p>
            </label>

            {/* Preview Images */}
            {selectedFiles.length > 0 && (
              <div className="mt-4 grid grid-cols-3 gap-3">
                {previewUrls.map((url, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={url}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-24 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="h-4 w-4" />
                    </button>
                    <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-1 rounded-b-lg truncate">
                      {selectedFiles[index].name}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={toggleReportForm}
              className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createReport.isPending}
              className="flex-1 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createReport.isPending ? 'Submitting...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
