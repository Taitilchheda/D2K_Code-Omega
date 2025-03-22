// components/EventRegistration.tsx
import React, { useState } from 'react';
import { MapPin } from 'lucide-react';

interface EventFormData {
  eventName: string;
  description: string;
  lat: number;
  lng: number;
  words: string;
  startDate: string;
  startTime: string;
}

export const EventRegistration: React.FC = () => {
  const [formData, setFormData] = useState<EventFormData>({
    eventName: '',
    description: '',
    lat: 0,
    lng: 0,
    words: '',
    startDate: '',
    startTime: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ['lat', 'lng'].includes(name) ? parseFloat(value) : value
    }));
  };

  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            lat: position.coords.latitude,
            lng: position.coords.longitude
          }));
          setUseCurrentLocation(true);
        },
        (error) => {
          setMessage({ 
            text: `Unable to retrieve your location: ${error.message}`, 
            type: 'error' 
          });
        }
      );
    } else {
      setMessage({ 
        text: 'Geolocation is not supported by your browser', 
        type: 'error' 
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage({ text: '', type: '' });

    try {
      // Convert date and time to timestamp
      const dateTimeStr = `${formData.startDate}T${formData.startTime}:00`;
      const timestamp = Math.floor(new Date(dateTimeStr).getTime() / 1000);
      
      // Split comma-separated words into array
      const wordsArray = formData.words.split(',').map(word => word.trim());
      
      // Format the data according to the API requirements
      const eventData = {
        eventName: formData.eventName,
        description: formData.description,
        lat: formData.lat,
        lng: formData.lng,
        words: wordsArray,
        start: timestamp
      };

      const response = await fetch('/register_event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData),
      });

      const result = await response.json();
      
      if (response.ok) {
        setMessage({ text: 'Event registered successfully!', type: 'success' });
        // Reset form after successful registration
        setFormData({
          eventName: '',
          description: '',
          lat: 0,
          lng: 0,
          words: '',
          startDate: '',
          startTime: ''
        });
        setUseCurrentLocation(false);
      } else {
        setMessage({ text: result.message || 'Event registration failed', type: 'error' });
      }
    } catch (error) {
      setMessage({ text: 'An error occurred. Please try again.', type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-700">Event Registration</h2>
      
      {message.text && (
        <div className={`p-4 mb-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {message.text}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
            <input
              type="text"
              name="eventName"
              value={formData.eventName}
              onChange={handleChange}
              required
              className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                name="startDate"
                value={formData.startDate}
                onChange={handleChange}
                required
                className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
              <input
                type="time"
                name="startTime"
                value={formData.startTime}
                onChange={handleChange}
                required
                className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags (comma separated)</label>
            <input
              type="text"
              name="words"
              value={formData.words}
              onChange={handleChange}
              placeholder="music, festival, live"
              className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
            />
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <button
                type="button"
                onClick={handleGetCurrentLocation}
                className="text-sm text-gray-600 hover:text-gray-700 flex items-center"
                aria-label="Use current location for event"
              >
                <MapPin size={16} className="mr-1" />
                Use Current Location
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Latitude</label>
                <input
                  type="number"
                  name="lat"
                  value={formData.lat}
                  onChange={handleChange}
                  required
                  step="any"
                  className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                  readOnly={useCurrentLocation}
                />
              </div>
              
              <div>
                <label className="block text-xs text-gray-500 mb-1">Longitude</label>
                <input
                  type="number"
                  name="lng"
                  value={formData.lng}
                  onChange={handleChange}
                  required
                  step="any"
                  className="w-full p-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                  readOnly={useCurrentLocation}
                />
              </div>
            </div>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-md font-medium disabled:opacity-50 transition-colors"
          aria-label="Register event"
        >
          {isSubmitting ? 'Registering...' : 'Register Event'}
        </button>
      </form>
    </div>
  );
};