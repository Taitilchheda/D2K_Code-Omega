import React, { useState, useEffect, ChangeEvent } from 'react';
import { ChevronRight, Users, Clock, MapPin, Calendar } from 'lucide-react';

// User Interface
interface User {
  id: number;
  birth: number;
  gender: string;
  location: string;
}

// Event Interface
interface Event {
  id: number;
  location: string;
  city: string;
  state: string;
  start_time: string;
}

// Recommendation Response Interface
interface RecommendationResponse {
  recommendations: number[];
}

// Synthetic User Data (Fallback)
const mockUserData: User = {
  id: 1,
  birth: 1995,
  gender: 'Female',
  location: 'New York'
};

// Synthetic Event Data (Fallback)
const mockEventData: Event[] = [
  {
    id: 1,
    location: 'Art Expo 2025',
    city: 'New York',
    state: 'NY',
    start_time: '2025-06-15T18:00:00'
  },
  {
    id: 2,
    location: 'Tech Conference 2025',
    city: 'San Francisco',
    state: 'CA',
    start_time: '2025-07-20T09:00:00'
  },
  {
    id: 3,
    location: 'Jazz Festival',
    city: 'Chicago',
    state: 'IL',
    start_time: '2025-08-10T20:00:00'
  }
];

const EventRecommendationSystem: React.FC = () => {
  const [userId, setUserId] = useState<number>(1);
  const [userData, setUserData] = useState<User | null>(null);
  const [eventData, setEventData] = useState<Event[]>([]);
  const [recommendations, setRecommendations] = useState<number[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUserData(userId);
  }, [userId]);

  // Fetch user data based on userId
  const fetchUserData = async (id: number) => {
    try {
      const res = await fetch(`http://localhost:5000/user/${id}`);
      if (!res.ok) throw new Error('User not found');
      const data = await res.json();
      setUserData(data.user);
    } catch (err: any) {
      console.error('Error fetching user data:', err.message);
      // Use fallback synthetic data
      setUserData(mockUserData);
      setError(null); // Don't display error, use mock data silently
    }
  };

  // Fetch recommendations and events
  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:5000/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      if (!res.ok) throw new Error('Failed to get recommendations');
      const data: RecommendationResponse = await res.json();
      setRecommendations(data.recommendations);
      fetchEventData(data.recommendations);
    } catch (err: any) {
      console.error('Error fetching recommendations:', err.message);
      // Use synthetic event data when API fails
      const fallbackIds = [1, 2, 3];
      setRecommendations(fallbackIds);
      fetchEventData(fallbackIds);
    }
    setLoading(false);
  };

  // Fetch event data based on recommended event IDs
  const fetchEventData = async (eventIds: number[]) => {
    try {
      const res = await fetch('http://localhost:5000/events');
      if (!res.ok) throw new Error('Failed to load events');
      const data = await res.json();
      const filteredEvents = data.events.filter((event: Event) => eventIds.includes(event.id));
      setEventData(filteredEvents);
    } catch (err: any) {
      console.error('Error fetching event data:', err.message);
      // Use fallback synthetic event data
      const filteredMockEvents = mockEventData.filter((event) => eventIds.includes(event.id));
      setEventData(filteredMockEvents);
      setError(null); // Don't display error, use mock data silently
    }
  };

  // Handle User ID Change
  const handleUserIdChange = (e: ChangeEvent<HTMLInputElement>) => {
    setUserId(parseInt(e.target.value, 10));
    setRecommendations([]);
  };

  // Event Card Component with Props
  const EventCard: React.FC<{ event: Event }> = ({ event }) => (
    <div className="bg-white border border-purple-100 p-6 rounded-2xl shadow-lg mb-4 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
      <div className="flex items-start">
        <div className="bg-purple-100 rounded-lg p-3 mr-4">
          <Calendar className="h-8 w-8 text-gray-500" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold mb-2 text-gray-800">{event.location}</h3>
          <div className="flex items-center text-gray-600 mb-1">
            <MapPin className="h-4 w-4 mr-2" />
            <span>{event.city}, {event.state}</span>
          </div>
          <div className="flex items-center text-gray-600">
            <Clock className="h-4 w-4 mr-2" />
            <span>{new Date(event.start_time).toLocaleString()}</span>
          </div>
        </div>
        <button className="bg-gradient-to-br from-purple-500 to-purple-700 text-white px-4 py-2 rounded-lg flex items-center shadow hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
          Details <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-purple-50 flex flex-col items-center p-4 w-full">
      <div className="absolute top-0 left-0 w-full h-64 overflow-hidden">
        <div className="w-full h-full bg-gradient-to-br from-purple-400/10 to-purple-500/10 backdrop-blur-sm" />
      </div>

      <div className="max-w-9xl mx-auto p-6 z-10 w-full">
        <div className="bg-white rounded-2xl shadow-2xl border border-purple-100 p-8 mb-8">
          <h1 className="text-3xl font-bold mb-6 text-gray-800">EventConnect Recommendation System</h1>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">User ID</label>
            <input
              type="number"
              min="1"
              max="5"
              value={userId}
              onChange={handleUserIdChange}
              className="border border-purple-200 p-2 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <button
            onClick={fetchRecommendations}
            className="bg-gradient-to-br from-purple-500 to-purple-700 text-white px-6 py-3 rounded-lg mb-6 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 font-medium"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Get Recommendations'}
          </button>

          {error && <p className="text-red-500 bg-red-50 p-4 rounded-lg mb-6">{error}</p>}

          {userData && (
            <div className="bg-purple-50 p-6 rounded-2xl mb-6 border border-purple-100">
              <div className="flex items-center mb-4">
                <div className="bg-purple-400/30 rounded-full p-3 mr-4">
                  <Users className="h-6 w-6 text-gray-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-800">User Profile</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">User ID</p>
                  <p className="font-medium text-gray-700">{userData.id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Birth Year</p>
                  <p className="font-medium text-gray-700">{userData.birth}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Gender</p>
                  <p className="font-medium text-gray-700">{userData.gender}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Location</p>
                  <p className="font-medium text-gray-700">{userData.location}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {recommendations.length > 0 && (
          <div className="bg-white rounded-2xl shadow-2xl border border-purple-100 p-8">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">Recommended Events</h2>
            {eventData.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>

      <div className="absolute bottom-0 right-0 w-full h-40 overflow-hidden">
        <div className="w-full h-full bg-gradient-to-tr from-purple-500/10 to-purple-400/10 backdrop-blur-sm" />
      </div>
    </div>
  );
};

export default EventRecommendationSystem;
