import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// Types
interface DetailPageProps {
  id?: string;
}

interface MovieDetail {
  id: string;
  title: string;
  poster: string;
  rating?: number;
  votes?: number;
  likes?: number;
  genres: string[];
  language?: string;
  description?: string;
  duration?: string;
  releaseDate?: string;
  directors?: string[];
  cast?: string[];
}

interface EventDetail {
  id: string;
  title: string;
  date: string;
  image: string;
  venue?: string;
  location?: string;
  description?: string;
  price?: string;
  startDate?: string;
  endDate?: string;
  ageRestriction?: string;
  languages?: string[];
  category?: string;
}

type DetailItem = MovieDetail | EventDetail;

// Helper function to determine if item is a movie or event
const isMovie = (item: DetailItem): item is MovieDetail => {
  return 'genres' in item && Array.isArray(item.genres);
};

const EventDetailPage: React.FC<DetailPageProps> = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const item: DetailItem = location.state?.item || {};
  
  // If no item was passed, redirect to home
  React.useEffect(() => {
    if (!item || !item.id) {
      navigate('/');
    }
  }, [item, navigate]);

  if (!item || !item.id) return null;

  const isMovieItem = isMovie(item);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Component Would Go Here */}
      <header className="bg-white py-4 px-4 flex justify-between items-center border-b shadow-sm">
        <div className="flex items-center">
          <div className="mr-6 font-bold text-2xl text-purple-700">Weekend Plan</div>
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search for Movies, Events, Plays, Sports and Activities" 
              className="p-2 pl-10 w-96 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <span className="absolute left-3 top-2.5 text-purple-400">🔍</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-purple-800 font-medium">
            <span>Mumbai</span>
            <span>▼</span>
          </div>
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition duration-150">Sign in</button>
          <div className="w-6 h-6 text-purple-800 cursor-pointer">≡</div>
        </div>
      </header>

      <div className="max-w-screen-xl mx-auto px-4 py-6">
        {/* Main event/movie info section */}
        <div className="bg-gradient-to-r from-purple-900 to-purple-700 text-white p-8 rounded-t-lg">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Left: Image */}
            <div className="w-full md:w-1/4">
              <img 
                src={item.image || item.poster || "/api/placeholder/300/450"} 
                alt={item.title}
                className="w-full h-auto rounded-lg shadow-lg"
              />
            </div>
            
            {/* Right: Details */}
            <div className="w-full md:w-3/4">
              <h1 className="text-3xl font-bold mb-3">{item.title}</h1>
              
              {isMovieItem ? (
                <>
                  {item.rating && (
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-yellow-400 text-xl">★</span>
                      <span className="font-semibold text-lg">{item.rating}/10</span>
                      <span className="text-purple-200">
                        {item.votes?.toLocaleString()} Votes
                      </span>
                    </div>
                  )}
                  
                  <div className="flex flex-wrap gap-4 mb-6">
                    {item.genres.map((genre, index) => (
                      <span key={index} className="bg-purple-600 px-3 py-1 rounded-full text-sm">
                        {genre}
                      </span>
                    ))}
                    {item.language && (
                      <span className="bg-purple-600 px-3 py-1 rounded-full text-sm">
                        {item.language}
                      </span>
                    )}
                    {item.duration && (
                      <span className="bg-purple-600 px-3 py-1 rounded-full text-sm">
                        {item.duration}
                      </span>
                    )}
                  </div>
                  
                  {item.releaseDate && (
                    <div className="mb-4">
                      <span className="text-purple-200">Release Date: </span>
                      <span className="font-medium">{item.releaseDate}</span>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-purple-200">Date:</span>
                      <span className="font-medium">
                        {item.startDate && item.endDate 
                          ? `${item.startDate} - ${item.endDate}`
                          : item.date}
                      </span>
                    </div>
                    
                    {item.venue && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-purple-200">Venue:</span>
                        <span className="font-medium">{item.venue}</span>
                      </div>
                    )}
                    
                    {item.location && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-purple-200">Location:</span>
                        <span className="font-medium">{item.location}</span>
                      </div>
                    )}
                  </div>
                  
                  {item.languages && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {item.languages.map((lang, index) => (
                        <span key={index} className="bg-purple-600 px-3 py-1 rounded-full text-sm">
                          {lang}
                        </span>
                      ))}
                      {item.ageRestriction && (
                        <span className="bg-purple-600 px-3 py-1 rounded-full text-sm">
                          {item.ageRestriction}
                        </span>
                      )}
                    </div>
                  )}
                </>
              )}
              
              <p className="text-purple-100 mb-6">
                {item.description || "Join us for an unforgettable experience! More details coming soon."}
              </p>
              
              <button className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-8 rounded-lg transition duration-200 text-lg">
                Book
              </button>
              
              <div className="mt-6 flex gap-6">
                <button className="flex items-center gap-2">
                  <button className="w-6 h-6 bg-purple-200 rounded-full flex items-center justify-center text-purple-900 hover:bg-white">👍</button>
                  <span>Interested?</span>
                </button>
                
                <button className="flex items-center gap-2">
                  <span className="w-6 h-6 bg-purple-200 rounded-full flex items-center justify-center text-purple-900">➕</span>
                  <span>Share</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Information Tabs & Content */}
        <div className="bg-white rounded-b-lg shadow-md mb-8">
          <div className="border-b border-gray-200">
            <div className="flex overflow-x-auto">
              <button className="px-6 py-4 text-purple-900 font-medium border-b-2 border-purple-600">
                About
              </button>
              <button className="px-6 py-4 text-gray-500 hover:text-purple-600">
                {isMovieItem ? "Cast & Crew" : "Venue Info"}
              </button>
              <button className="px-6 py-4 text-gray-500 hover:text-purple-600">
                Reviews
              </button>
              <button className="px-6 py-4 text-gray-500 hover:text-purple-600">
                {isMovieItem ? "Offers" : "Terms & Conditions"}
              </button>
            </div>
          </div>
          
          <div className="p-6">
            <h2 className="text-xl font-bold text-purple-900 mb-4">
              About {isMovieItem ? "the Movie" : "the Event"}
            </h2>
            
            {isMovieItem ? (
              <div className="prose max-w-none">
                <p>
                  Welcome to the screening of {item.title}, a {item.genres.join(', ')} film 
                  {item.language ? ` in ${item.language}` : ''}. 
                  This cinematic experience brings together exceptional storytelling and artistic expression.
                </p>
                
                {item.directors && item.directors.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-purple-800">Directors</h3>
                    <p>{item.directors.join(', ')}</p>
                  </div>
                )}
                
                {item.cast && item.cast.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-purple-800">Cast</h3>
                    <p>{item.cast.join(', ')}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="prose max-w-none">
                <p>
                  Welcome to {item.title}, where excellence meets artistic expression. 
                  Join us {item.venue ? `at ${item.venue}` : ''} 
                  {item.location ? ` in ${item.location}` : ''} for an unforgettable experience.
                </p>
                
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-purple-800">Why should you attend?</h3>
                  <ul className="list-disc pl-5 mt-2">
                    <li>An event curated by BookMyShow - we live & breathe entertainment!</li>
                    <li>A unique experience where global culture meets local expression.</li>
                    <li>Rub shoulders with the experts in the industry & fellow enthusiasts.</li>
                    {item.category === 'Film Festival' && (
                      <li>Discover cinematic excellence from around the world.</li>
                    )}
                  </ul>
                </div>
              </div>
            )}
            
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mt-6">
              <h3 className="font-bold text-purple-900">NOTE</h3>
              <ul className="list-disc pl-5 mt-2 space-y-2">
                <li>
                  On clicking the Book Now button, you'll be directed to the ticket categories & 
                  their offerings.
                </li>
                <li>
                  Select your preferred category along with the total number of tickets that you
                  want to purchase.
                </li>
                <li>
                  Maximum of 10 tickets can be purchased in one transaction.
                </li>
                <li>
                  After selecting the category and total number of tickets, click on the Proceed
                  button.
                </li>
                <li>
                  Kindly fill in your details in the pop-up window in order to get yourself
                  registered.
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Map Section (for events) */}
        {!isMovieItem && item.venue && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold text-purple-900 mb-4">Location</h2>
            <div className="h-64 bg-gray-200 rounded-lg relative overflow-hidden">
              <img 
                src="/api/placeholder/800/400" 
                alt="Map Location"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-4 right-4">
                <button className="bg-white px-3 py-2 rounded-lg shadow-md text-purple-900 font-medium">
                  View larger map
                </button>
              </div>
            </div>
            <div className="mt-4">
              <p className="font-medium">{item.venue}</p>
              <p className="text-gray-600">{item.location || "Mumbai, Maharashtra"}</p>
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="bg-purple-900 text-white py-8 px-4 mt-8">
        <div className="max-w-screen-xl mx-auto">
          <div className="grid grid-cols-4 gap-8 mb-6">
            <div>
              <h3 className="font-bold mb-3">BookMyShow</h3>
              <ul className="space-y-2 text-purple-200">
                <li>About Us</li>
                <li>Contact Us</li>
                <li>FAQ</li>
                <li>Terms and Conditions</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-3">Movies</h3>
              <ul className="space-y-2 text-purple-200">
                <li>Hindi</li>
                <li>English</li>
                <li>Tamil</li>
                <li>Telugu</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-3">Events</h3>
              <ul className="space-y-2 text-purple-200">
                <li>Concerts</li>
                <li>Comedy Shows</li>
                <li>Sports</li>
                <li>Festivals</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-3">Follow Us</h3>
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-purple-600 rounded-full"></div>
                <div className="w-8 h-8 bg-purple-600 rounded-full"></div>
                <div className="w-8 h-8 bg-purple-600 rounded-full"></div>
                <div className="w-8 h-8 bg-purple-600 rounded-full"></div>
              </div>
            </div>
          </div>
          <div className="border-t border-purple-700 pt-4 text-center text-purple-300">
            © 2025 BookMyShow. All Rights Reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default EventDetailPage;