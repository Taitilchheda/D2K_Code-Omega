// App.tsx - Main component with improved styling
import React, { useState } from 'react';
import { UserRegistration } from './UserRegistration';
import { EventRegistration } from './EventRegistration';
import { CalendarDays, Users, ArrowLeft } from 'lucide-react';

type UserType = 'none' | 'organizer' | 'user';

const App: React.FC = () => {
  const [userType, setUserType] = useState<UserType>('none');

  const resetSelection = () => {
    setUserType('none');
  };

  return (
    <div className="min-h-screen bg-purple-50 flex flex-col items-center justify-center p-4 w-full">
      {/* <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-r from-purple-500 to-purple-600 transform -skew-y-2" />
       */}
      <div className="absolute top-0 left-0 w-full h-64 overflow-hidden">
        <div className="w-full h-full bg-gradient-to-br from-purple-400/10 to-purple-500/10 backdrop-blur-sm" />
      </div>
      
      {userType === 'none' ? (
        <div className="w-full max-w-5xl z-10 px-4 py-8">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4 text-purple-800 drop-shadow-sm">Welcome to EventConnect</h1>
            <p className="text-xl text-purple-700 max-w-2xl mx-auto">Please select your role to continue your journey</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
            {/* Event Organizer Button */}
            <button
              onClick={() => setUserType('organizer')}
              className="bg-gradient-to-br from-purple-500 to-purple-700 text-white rounded-2xl p-10 transition-all duration-300 
                        flex flex-col items-center shadow-xl hover:shadow-2xl transform hover:-translate-y-1 group w-full"
              aria-label="Continue as Event Organizer"
            >
              <div className="bg-purple-400/30 p-6 rounded-full mb-6 group-hover:bg-purple-400/40 transition-all">
                <CalendarDays size={64} className="text-white" aria-hidden="true" />
              </div>
              <span className="text-3xl font-semibold mb-2">Event Organizer</span>
              <p className="text-purple-100">Create and manage incredible events</p>
            </button>
            
            {/* User Button */}
            <button
              onClick={() => setUserType('user')}
              className="bg-gradient-to-br from-purple-500 to-purple-700 text-white rounded-2xl p-10 transition-all duration-300 
                        flex flex-col items-center shadow-xl hover:shadow-2xl transform hover:-translate-y-1 group w-full"
              aria-label="Continue as User"
            >
              <div className="bg-purple-400/30 p-6 rounded-full mb-6 group-hover:bg-purple-400/40 transition-all">
                <Users size={64} className="text-white" aria-hidden="true" />
              </div>
              <span className="text-3xl font-semibold mb-2">User</span>
              <p className="text-purple-100">Discover and attend amazing events</p>
            </button>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-3xl bg-white p-8 md:p-10 rounded-2xl shadow-2xl z-10 mx-4 border border-purple-100">
          <button 
            onClick={resetSelection}
            className="mb-8 text-purple-600 hover:text-purple-800 flex items-center transition-colors font-medium"
            aria-label="Back to role selection"
          >
            <ArrowLeft className="mr-2" size={20} />
            Back to selection
          </button>
          
          {userType === 'organizer' ? (
            <div className="relative">
              <div className="absolute -top-6 -left-6 w-20 h-20 rounded-full bg-purple-600 opacity-10" />
              <div className="absolute -bottom-6 -right-6 w-32 h-32 rounded-full bg-purple-600 opacity-5" />
              <EventRegistration />
            </div>
          ) : (
            <div className="relative">
              <div className="absolute -top-6 -left-6 w-20 h-20 rounded-full bg-purple-600 opacity-10" />
              <div className="absolute -bottom-6 -right-6 w-32 h-32 rounded-full bg-purple-600 opacity-5" />
              <UserRegistration />
            </div>
          )}
        </div>
      )}
      
      <div className="absolute bottom-0 right-0 w-full h-40 overflow-hidden">
        <div className="w-full h-full bg-gradient-to-tr from-purple-500/10 to-purple-400/10 backdrop-blur-sm" />
      </div>
    </div>
  );
};

export default App;