import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Calendar, ChevronDown, Filter, Plus, Search, Settings } from 'lucide-react';

// Types
interface Event {
  id: string;
  name: string;
  type: string;
  date: string;
  day: string;
  month: string;
  season: string;
  location: string;
  engagementScore: number;
  trend: number[];
}

interface TopEvent {
  id: string;
  name: string;
  type: string;
  engagementScore: number;
  trend: number[];
  change: number;
}

// Sample Data
const topEvents: TopEvent[] = [
  {
    id: '1',
    name: 'Summer Music Festival',
    type: 'Concert',
    engagementScore: 17.68,
    trend: [45, 49, 53, 47, 52, 56, 58, 62, 65, 68, 72, 75],
    change: 4.2,
  },
  {
    id: '2',
    name: 'Tech Conference',
    type: 'Conference',
    engagementScore: 12.45,
    trend: [30, 32, 35, 38, 40, 39, 42, 45, 48, 47, 50, 53],
    change: 3.8,
  },
  {
    id: '3',
    name: 'Food & Wine Expo',
    type: 'Exhibition',
    engagementScore: 9.72,
    trend: [25, 28, 30, 29, 31, 30, 33, 35, 38, 40, 39, 42],
    change: -1.3,
  }
];

const currentEvent: Event = {
  id: '1',
  name: 'Summer Music Festival',
  type: 'Concert',
  date: '2025-07-15',
  day: 'Saturday',
  month: 'July',
  season: 'Summer',
  location: 'Central Park, New York',
  engagementScore: 17.68,
  trend: [45, 49, 53, 47, 52, 56, 58, 62, 65, 68, 72, 75]
};

const seasonalData = [
  { name: 'Jan', score: 45 },
  { name: 'Feb', score: 49 },
  { name: 'Mar', score: 53 },
  { name: 'Apr', score: 47 },
  { name: 'May', score: 52 },
  { name: 'Jun', score: 56 },
  { name: 'Jul', score: 58 },
  { name: 'Aug', score: 62 },
  { name: 'Sep', score: 65 },
  { name: 'Oct', score: 68 },
  { name: 'Nov', score: 72 },
  { name: 'Dec', score: 75 },
];

const EventDiscoveryDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('recommended');
  const [selectedPeriod, setSelectedPeriod] = useState('12 months');
  const [expandedEvent, setExpandedEvent] = useState<string | null>('1');

  return (
    <div className="bg-gray-900 text-white min-h-screen p-6">
      {/* Header Bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <div className="bg-purple-600 rounded-lg p-2 mr-3">
            <Calendar className="h-5 w-5" />
          </div>
          <span className="font-bold text-lg">Evento™</span>
          <span className="text-gray-400 text-xs ml-2">Discovering events</span>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="bg-gray-800 rounded-full px-3 py-1 flex items-center">
            <span className="mr-2">Deploy</span>
            <ChevronDown className="h-4 w-4" />
          </div>
          
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center mr-2">
              <span className="text-sm font-bold">RC</span>
            </div>
            <span>Ryan Cleveland</span>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="grid grid-cols-4 gap-4">
        {/* Sidebar */}
        <div className="col-span-1">
          <div className="bg-gray-800 rounded-lg p-4 mb-4">
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium text-gray-400">Menu</h3>
              </div>
              
              <ul className="space-y-2">
                <li className="flex items-center text-white bg-gray-700 rounded-lg p-2">
                  <div className="mr-3">
                    <div className="bg-purple-600 rounded p-1">
                      <Calendar className="h-4 w-4" />
                    </div>
                  </div>
                  <span>Dashboard</span>
                </li>
                
                <li className="flex items-center text-gray-400 p-2">
                  <div className="mr-3">
                    <Calendar className="h-4 w-4" />
                  </div>
                  <span>Events</span>
                </li>
                
                <li className="flex items-center text-gray-400 p-2">
                  <div className="mr-3">
                    <Filter className="h-4 w-4" />
                  </div>
                  <span>Categories</span>
                </li>
                
                <li className="flex items-center text-gray-400 p-2">
                  <div className="mr-3">
                    <Settings className="h-4 w-4" />
                  </div>
                  <span>Event Calculator</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-400 mb-4">Your Events</h3>
              <ul className="space-y-3">
                <li className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-purple-600 mr-2 flex items-center justify-center">S</div>
                    <span className="text-sm">Summer Music Festival</span>
                  </div>
                  <span className="text-xs text-white bg-purple-600 rounded px-2 py-0.5">Live</span>
                </li>
                
                <li className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-yellow-600 mr-2 flex items-center justify-center">T</div>
                    <span className="text-sm">Tech Conference</span>
                  </div>
                  <span className="text-xs text-gray-800 bg-gray-300 rounded px-2 py-0.5">Draft</span>
                </li>
                
                <li className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full bg-red-600 mr-2 flex items-center justify-center">F</div>
                    <span className="text-sm">Food & Wine Expo</span>
                  </div>
                  <span className="text-xs text-white bg-purple-600 rounded px-2 py-0.5">Live</span>
                </li>
              </ul>
              
              <button className="mt-4 w-full bg-gray-700 rounded-lg p-2 text-sm flex items-center justify-center">
                <Plus className="h-4 w-4 mr-2" />
                <span>Create Event</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Main Dashboard */}
        <div className="col-span-3">
          {/* Tabs */}
          <div className="flex mb-4">
            <div className="flex space-x-4 items-center">
              <button 
                className={`px-4 py-2 rounded-lg ${activeTab === 'recommended' ? 'bg-gray-700' : ''}`}
                onClick={() => setActiveTab('recommended')}
              >
                Recommended events for next 30 days
              </button>
              <button 
                className={`px-4 py-2 rounded-lg ${activeTab === '6months' ? 'bg-gray-700' : ''}`}
                onClick={() => setActiveTab('6months')}
              >
                6 months
              </button>
            </div>
          </div>
          
          {/* Top Trending Events */}
          <h2 className="text-xl font-bold mb-4">Top Trending Events</h2>
          <div className="grid grid-cols-3 gap-4 mb-6">
            {topEvents.map(event => (
              <div key={event.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <p className="text-gray-400 text-xs">Type of Event</p>
                    <p className="text-sm">{event.type}</p>
                  </div>
                  <button className="text-gray-400">
                    <div className="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center">
                      <ChevronDown className="h-4 w-4" />
                    </div>
                  </button>
                </div>
                
                <div className="mb-2">
                  <h3 className="font-bold text-xl">{event.engagementScore}%</h3>
                  <div className="flex items-center">
                    <span className={`text-xs ${event.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {event.change >= 0 ? '+' : ''}{event.change}%
                    </span>
                  </div>
                </div>
                
                <div className="h-16">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={seasonalData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                      <Line 
                        type="monotone" 
                        dataKey="score" 
                        stroke={
                          event.id === '1' ? '#8884d8' : 
                          event.id === '2' ? '#82ca9d' : 
                          '#ff8042'
                        } 
                        strokeWidth={2} 
                        dot={false} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ))}
          </div>
          
          {/* Current Active Event */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Your active events</h3>
              
              <div className="flex space-x-2">
                <button className="rounded-full w-8 h-8 flex items-center justify-center bg-gray-700">
                  <Search className="h-4 w-4" />
                </button>
                <button className="rounded-full w-8 h-8 flex items-center justify-center bg-gray-700">
                  <Filter className="h-4 w-4" />
                </button>
                <button className="rounded-full w-8 h-8 flex items-center justify-center bg-gray-700">
                  <Settings className="h-4 w-4" />
                </button>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <div className="bg-purple-600 rounded p-1 mr-3">
                    <Calendar className="h-4 w-4" />
                  </div>
                  <h4 className="font-semibold">Event: {currentEvent.name} [{currentEvent.type}]</h4>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button className="bg-gray-700 rounded p-2 text-xs">View Profile</button>
                  <button className="bg-purple-600 rounded p-2 text-xs">Update</button>
                </div>
              </div>
              
              <div className="text-4xl font-bold my-6">
                {currentEvent.engagementScore.toFixed(5)}
              </div>
              
              <div className="grid grid-cols-4 gap-4">
                <div>
                  <h5 className="text-gray-400 mb-2">Momentum</h5>
                  <div className="flex items-center justify-between">
                    <p>Growth Momentum</p>
                    <div className="text-xl font-semibold">+1.75%</div>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-gray-400 mb-2">Seasonal</h5>
                  <div className="flex items-center justify-between">
                    <p>Peak Season</p>
                    <div className="text-xl font-semibold">{currentEvent.season}</div>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-gray-400 mb-2">Risk</h5>
                  <div className="flex items-center justify-between">
                    <p>Risk assessment</p>
                    <div className="text-xl font-semibold">25.6%</div>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-gray-400 mb-2">Reward</h5>
                  <div className="flex items-center justify-between">
                    <p>Expected profit</p>
                    <div className="text-xl font-semibold">$21.99</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Seasonal Trend */}
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Seasonal Trend Analysis</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={seasonalData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis dataKey="name" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#333', border: 'none' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#8884d8" 
                      strokeWidth={2} 
                      dot={{ r: 4 }} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Event Period</h3>
              <p className="text-gray-400 text-sm mb-4">When does your event get maximum engagement</p>
              
              <div className="flex justify-between items-center mb-4">
                <button className="bg-gray-700 rounded-lg px-3 py-1 text-sm">
                  {selectedPeriod}
                </button>
                <button className="bg-purple-600 rounded-lg px-3 py-1 text-sm">
                  Apply
                </button>
              </div>
              
              <div className="mb-6">
                <div className="h-4 bg-gray-700 rounded-full mb-2">
                  <div 
                    className="h-full bg-purple-600 rounded-full" 
                    style={{ width: '75%' }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-400">
                  <span>Jan</span>
                  <span>Dec</span>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Current Peak</span>
                  <span className="font-bold">July</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Peak Season</span>
                  <span className="font-bold">Summer</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Growth Rate</span>
                  <span className="font-bold text-green-500">+3.25% YoY</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Location Factor</span>
                  <span className="font-bold">+0.84x</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Create New Event Button (Floating) */}
          <button className="fixed bottom-8 right-8 bg-purple-600 text-white rounded-full p-4 shadow-lg flex items-center justify-center">
            <Plus className="h-6 w-6 mr-2" />
            <span className="font-semibold">Create New Event</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EventDiscoveryDashboard;