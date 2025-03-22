import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import assest1 from '../assets/movies1.jpg'
import assest2 from '../assets/movies2.jpg'
import assest3 from '../assets/movies3.jpg'
import assest4 from '../assets/movies4.jpg'
import assest5 from '../assets/movies5.jpg'
import assest6 from '../assets/movies6.jpg'
import assest7 from '../assets/movies7.jpg'
import assest8 from '../assets/movies8.jpg'

import sport1 from  '../assets/sports1.jpg'
import sport2 from  '../assets/sports2.jpg'
import sport3 from  '../assets/sports3.jpg'
import sport4 from  '../assets/sports4.jpg'
import sport5 from  '../assets/sports5.jpg'
// Types
interface Movie {
  id: string;
  title: string;
  poster: string;
  rating?: number;
  votes?: number;
  likes?: number;
  genres: string[];
  language?: string;
}

interface Event {
  id: string;
  title: string;
  date: string;
  image: string;
  venue?: string;
  location?: string;
}

interface Banner {
  id: string;
  image: string;
  title: string;
  venue?: string;
  date?: string;
}

// Dummy Data
const banners: Banner[] = [
  {
    id: '1',
    image: sport5,
    title: "Andrew Lloyd Webber's Phantom of the Opera",
    venue: "The Grand Theatre, NMACC",
    date: "SHOWS END 30TH MARCH"
  }
];

const recommendedMovies: Movie[] = [
  {
    "id": "1",
    "title": "Phir Aayi Haseen Dillruba",
    "poster": assest1,
    "language": "Hindi",
    "genres": ["Crime", "Drama", "Mystery", "Thriller"],
    "rating": 8.2,
    "votes": 12500
  },
  {
    "id": "2",
    "title": "Kill",
    "poster": assest2,
    "language": "Hindi",
    "genres": ["Action", "Thriller"],
    "rating": 7.8,
    "votes": 8900
  },
  {
    "id": "3",
    "title": "Warning 2",
    "poster":assest3,
    "language": "Punjabi",
    "genres": ["Action", "Crime", "Thriller"],
    "rating": 7.5,
    "votes": 6200
  },
  {
    "id": "4",
    "title": "Sister Midnight",
    "poster": assest4,
    "language": "Hindi",
    "genres": ["Drama", "Comedy"],
    "rating": 8.0,
    "votes": 5600
  },
  {
    "id": "5",
    "title": "Tumko Meri Kasam",
    "poster": assest5,
    "language": "Hindi",
    "genres": ["Romance", "Drama"],
    "rating": 7.6,
    "votes": 7800
  },
];

const sportEvents: Event[] = [
  {
    id: '1',
    title: 'Mumbai Indians - IPL 2025',
    date: 'Mon, 31 Mar onwards',
    image: sport1,
    venue: 'Multiple Venues',
    location: 'Mumbai'
  },
  {
    id: '2',
    title: 'Mumbai Indians vs Gujarat Titans',
    date: 'Tue, 6 May',
    image: sport2,
    venue: 'Wankhede Stadium',
    location: 'Mumbai'
  },
  {
    id: '3',
    title: 'Lucknow Super Giants vs Punjab Kings',
    date: 'Tue, 1 Apr',
    image: sport3,
    venue: 'BRSABV Ekana Cricket Stadium',
    location: 'Lucknow'
  },
  {
    id: '4',
    title: 'Kolkata Knight Riders vs Sunrisers Hyderabad',
    date: 'Thu, 3 Apr',
    image: sport4,
    venue: 'Eden Gardens',
    location: 'Kolkata'
  },
  {
    id: '5',
    title: 'Rajasthan Royals vs Royal Challengers Bangalore',
    date: 'Sun, 13 Apr',
    image: sport5,
    venue: 'Sawai Mansingh Stadium',
    location: 'Jaipur'
  }
];

const premiereMovies: Movie[] = [
  {
    id: '1',
    title: 'Companion (Preview)',
    poster: assest3,
    language: 'English',
    genres: ['Thriller', 'Drama']
  },
  {
    id: '2',
    title: 'The Room Next Door',
    poster: assest7,
    language: 'English',
    genres: ['Drama']
  },
  {
    id: '3',
    title: 'Hide N Seek',
    poster: assest8,
    language: 'Telugu',
    genres: ['Horror', 'Thriller']
  },
  {
    id: '4',
    title: 'The Seed of the Sacred Fig',
    poster: assest1,
    language: 'Persian',
    genres: ['Drama']
  },
  {
    id: '5',
    title: '(Pri)sons',
    poster: assest6,
    language: 'English',
    genres: ['Documentary']
  }
];

// Define film festival event data
const filmFestivalEvent = {
  id: 'film-festival-1',
  title: 'Red Lorry Film Festival 2025 - Take Two, Mumbai',
  date: 'Fri 21 Mar 2025 - Sun 23 Mar 2025',
  image: sport2,
  venue: 'Multiple Venues',
  location: 'Mumbai',
  price: '₹ 750 onwards',
  description: 'Welcome to the Red Lorry Film Festival, where cinematic excellence meets artistic expression and shifted the gears of India\'s film culture in its grand edition.',
  languages: ['Danish', 'English', 'French', 'German', 'Icelandic', 'Italian', 'Norwegian', 'Russian', 'Spanish', 'Swedish', 'Turkish'],
  ageRestriction: '18yrs + | 12hrs',
  category: 'Film Festival'
};

// Featured events array for a new section
const featuredEvents = [
  {
    id: 'film-festival-1',
    title: 'Red Lorry Film Festival 2025 - Take Two, Mumbai',
    date: 'Fri 21 Mar 2025 - Sun 23 Mar 2025',
    image: assest8,
    venue: 'Multiple Venues',
    location: 'Mumbai',
    category: 'Film Festival'
  },
  {
    id: 'comedy-1',
    title: 'Comedy All-Stars - Stand Up Comedy Show',
    date: 'Sat, 29 Mar 2025',
    image: assest3,
    venue: 'Bandra Amphitheatre',
    location: 'Mumbai',
    category: 'Comedy Show'
  },
  {
    id: 'concert-1',
    title: 'Arijit Singh Live in Concert',
    date: 'Sat, 5 Apr 2025',
    image: assest6,
    venue: 'DY Patil Stadium',
    location: 'Navi Mumbai',
    category: 'Music Concert'
  },
  {
    id: 'workshop-1',
    title: 'International Film Writing Workshop',
    date: 'Mon, 24 Mar 2025 - Wed, 26 Mar 2025',
    image: assest1,
    venue: 'The Grand Theatre',
    location: 'Mumbai',
    category: 'Workshop'
  },
  {
    id: 'exhibition-1',
    title: 'Cinema & Culture Exhibition',
    date: 'Fri, 21 Mar 2025 - Sun, 30 Mar 2025',
    image: '/api/placeholder/220/320',
    venue: 'Mumbai Art Gallery',
    location: 'Mumbai',
    category: 'Exhibition'
  }
];

// Components
const Header: React.FC = () => {
  const [city, setCity] = useState('Mumbai');
  
  return (
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
          <span>{city}</span>
          <span>▼</span>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition duration-150">Sign in</button>
        <div className="w-6 h-6 text-purple-800 cursor-pointer">≡</div>
      </div>
    </header>
  );
};

const NavBar: React.FC = () => {
  const navItems = ['Movies', 'Stream', 'Events', 'Plays', 'Sports', 'Activities'];
  const rightNavItems = ['ListYourShow', 'Corporates', 'Offers', 'Gift Cards'];
  
  return (
    <nav className="bg-white py-3 px-4 flex justify-between shadow-sm">
      <ul className="flex gap-6">
        {navItems.map((item, index) => (
          <li key={index} className="text-purple-900 font-medium hover:text-purple-600 cursor-pointer">{item}</li>
        ))}
      </ul>
      <ul className="flex gap-6">
        {rightNavItems.map((item, index) => (
          <li key={index} className="text-purple-700 text-sm hover:text-purple-500 cursor-pointer">{item}</li>
        ))}
      </ul>
    </nav>
  );
};

const Banner: React.FC<{ banner: Banner }> = ({ banner }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate('/event/film-festival-1', { 
      state: { item: filmFestivalEvent }
    });
  };
  
  return (
    <div 
      className="relative w-full h-72 bg-purple-900 overflow-hidden rounded-lg shadow-lg cursor-pointer"
      onClick={handleClick}
    >
      <img 
        src={banner.image} 
        alt={banner.title}
        className="w-full h-full object-cover opacity-80"
      />
      <div className="absolute bottom-0 left-0 w-full p-6 bg-gradient-to-t from-purple-900/90 to-transparent text-white">
        <h2 className="text-3xl font-bold">{banner.title}</h2>
        {banner.venue && <p className="text-purple-100">{banner.venue}</p>}
        {banner.date && <p className="text-xl font-semibold text-purple-200">{banner.date}</p>}
        <button className="mt-4 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-6 rounded-lg transition duration-150">
          Book Now
        </button>
      </div>
    </div>
  );
};

const MovieCard: React.FC<{ movie: Movie; promoted?: boolean }> = ({ movie, promoted }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate(`/movie/${movie.id}`, {
      state: { 
        item: {
          ...movie,
          description: "An exciting cinematic journey that will keep you on the edge of your seat!",
          releaseDate: "March 15, 2025",
          duration: "2h 15m",
          directors: ["Filmmaker One", "Filmmaker Two"],
          cast: ["Actor One", "Actor Two", "Actor Three", "Actor Four"]
        }
      }
    });
  };
  
  return (
    <div 
      className="w-52 overflow-hidden rounded-lg shadow-md hover:shadow-lg transition duration-300 bg-white cursor-pointer"
      onClick={handleClick}
    >
      <div className="relative">
        <img 
          src={movie.poster} 
          alt={movie.title}
          className="w-full h-72 object-cover"
        />
        {promoted && (
          <span className="absolute top-2 left-0 bg-purple-600 text-white px-2 py-0.5 text-xs">
            PROMOTED
          </span>
        )}
      </div>
      <div className="py-2 px-3">
        {movie.rating && (
          <div className="flex items-center gap-2 mb-1">
            <span className="text-purple-500">★</span>
            <span className="font-medium">{movie.rating}/10</span>
            <span className="text-gray-500 text-sm">{movie.votes?.toLocaleString()} Votes</span>
          </div>
        )}
        {movie.likes && (
          <div className="flex items-center gap-2 mb-1">
            <span className="text-green-500">👍</span>
            <span className="font-medium">{movie.likes?.toLocaleString()} Likes</span>
          </div>
        )}
        <h3 className="font-semibold text-lg text-purple-900">{movie.title}</h3>
        <p className="text-purple-700 text-sm">{movie.genres.join('/')}</p>
        {movie.language && <p className="text-purple-600 text-sm">{movie.language}</p>}
      </div>
    </div>
  );
};

const EventCard: React.FC<{ event: Event; promoted?: boolean }> = ({ event, promoted }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    // For film festival event
    if (event.id === 'film-festival-1') {
      navigate(`/event/${event.id}`, { 
        state: { item: filmFestivalEvent }
      });
    } else {
      // For other events
      navigate(`/event/${event.id}`, {
        state: { 
          item: {
            ...event,
            description: "Join us for an unforgettable experience! More details coming soon.",
            price: "₹ 500 onwards",
            languages: ["English", "Hindi"],
            ageRestriction: "All ages"
          }
        }
      });
    }
  };
  
  return (
    <div 
      className="w-52 overflow-hidden rounded-lg shadow-md hover:shadow-lg transition duration-300 bg-white cursor-pointer"
      onClick={handleClick}
    >
      <div className="relative">
        <img 
          src={event.image} 
          alt={event.title}
          className="w-full h-72 object-cover"
        />
        {promoted && (
          <span className="absolute top-2 left-0 bg-purple-600 text-white px-2 py-0.5 text-xs">
            PROMOTED
          </span>
        )}
        <div className="absolute bottom-0 left-0 w-full bg-purple-900/80 text-white p-2">
          <p>{event.date}</p>
        </div>
      </div>
      <div className="py-2 px-3">
        <h3 className="font-semibold text-purple-900">{event.title}</h3>
        {event.venue && <p className="text-purple-700 text-sm">{event.venue}</p>}
        {event.location && <p className="text-purple-600 text-sm">{event.location}</p>}
      </div>
    </div>
  );
};

const FeaturedEventCard: React.FC<{ event: any }> = ({ event }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    // For film festival event
    if (event.id === 'film-festival-1') {
      navigate(`/event/${event.id}`, { 
        state: { item: filmFestivalEvent }
      });
    } else {
      // For other events
      navigate(`/event/${event.id}`, {
        state: { 
          item: {
            ...event,
            description: "Join us for an unforgettable experience! More details coming soon.",
            price: "₹ 500 onwards",
            languages: ["English", "Hindi"],
            ageRestriction: "All ages"
          }
        }
      });
    }
  };
  
  return (
    <div 
      className="flex flex-col md:flex-row w-full bg-white rounded-lg shadow-md hover:shadow-lg transition duration-300 overflow-hidden cursor-pointer"
      onClick={handleClick}
    >
      <div className="w-full md:w-1/4 relative">
        <img 
          src={event.image} 
          alt={event.title}
          className="w-full h-full md:h-48 object-cover"
        />
        {event.category && (
          <span className="absolute top-2 left-0 bg-purple-600 text-white px-2 py-0.5 text-xs">
            {event.category}
          </span>
        )}
      </div>
      <div className="p-4 flex-1">
        <h3 className="font-semibold text-lg text-purple-900 mb-1">{event.title}</h3>
        <p className="text-purple-600 mb-2">{event.date}</p>
        <div className="flex items-center gap-2 text-purple-700 text-sm">
          <span>{event.venue}</span> | <span>{event.location}</span>
        </div>
        <div className="mt-4 flex justify-between items-center">
          <span className="text-gray-500 text-sm">Tickets selling fast!</span>
          <button className="bg-red-500 hover:bg-red-600 text-white px-4 py-1 rounded transition duration-150 text-sm">
            Book Now
          </button>
        </div>
      </div>
    </div>
  );
};

const PremiereCard: React.FC<{ movie: Movie }> = ({ movie }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate(`/movie/${movie.id}`, {
      state: { 
        item: {
          ...movie,
          description: "An exciting premiere screening that will captivate you!",
          releaseDate: "Coming Soon",
          duration: "2h 30m",
          directors: ["Director Name"],
          cast: ["Cast Member One", "Cast Member Two", "Cast Member Three"]
        }
      }
    });
  };
  
  return (
    <div 
      className="w-52 overflow-hidden rounded-lg shadow-md hover:shadow-lg transition duration-300 cursor-pointer"
      onClick={handleClick}
    >
      <div className="relative">
        <img 
          src={movie.poster} 
          alt={movie.title}
          className="w-full h-72 object-cover"
        />
        <div className="absolute bottom-0 left-0 bg-purple-600 text-white px-3 py-1">
          PREMIERE
        </div>
      </div>
      <div className="py-2 bg-purple-900 text-white p-3">
        <h3 className="font-semibold">{movie.title}</h3>
        <p className="text-purple-200 text-sm">{movie.language}</p>
      </div>
    </div>
  );
};

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => {
  return (
    <section className="py-6 px-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-purple-900">{title}</h2>
        <a href="#" className="text-purple-600 hover:text-purple-800 transition duration-150">See All &gt;</a>
      </div>
      <div className="flex overflow-x-auto gap-4 pb-4 hide-scrollbar">
        {children}
      </div>
    </section>
  );
};

const FeaturedSection: React.FC<{ title: string; events: any[] }> = ({ title, events }) => {
  return (
    <section className="py-6 px-4 bg-gray-100">
      <div className="max-w-screen-xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-purple-900">{title}</h2>
            <p className="text-purple-700">Explore upcoming cultural events in your city</p>
          </div>
          <a href="#" className="text-purple-600 hover:text-purple-800 transition duration-150">See All Events &gt;</a>
        </div>
        
        <div className="space-y-4">
          {events.slice(0, 3).map(event => (
            <FeaturedEventCard key={event.id} event={event} />
          ))}
        </div>
      </div>
    </section>
  );
};

const PremiereSection: React.FC<{ movies: Movie[] }> = ({ movies }) => {
  return (
    <section className="py-6 px-4 bg-purple-900 text-white">
      <div className="flex items-center gap-4 mb-6">
        <div className="bg-purple-600 rounded-full p-3">
          <span className="text-2xl">▶</span>
        </div>
        <div>
          <h2 className="text-2xl font-bold">PREMIERES</h2>
          <p className="text-purple-200">Brand new releases every Friday</p>
        </div>
      </div>
      
      <div className="flex justify-between items-center mb-4">
        <a href="#" className="text-purple-300 hover:text-white transition duration-150">See All &gt;</a>
      </div>
      
      <div className="flex overflow-x-auto gap-4 pb-4 hide-scrollbar">
        {movies.map(movie => (
          <PremiereCard key={movie.id} movie={movie} />
        ))}
      </div>
    </section>
  );
};

const FilmFestivalBanner: React.FC = () => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate('/event/film-festival-1', { 
      state: { item: filmFestivalEvent }
    });
  };
  
  return (
    <div 
      className="relative w-full bg-purple-900 rounded-lg shadow-lg overflow-hidden cursor-pointer my-6"
      onClick={handleClick}
    >
      <div className="flex flex-col md:flex-row">
        <div className="w-full md:w-2/3 p-6 text-white">
          <div className="inline-block bg-red-500 px-3 py-1 rounded-full text-sm font-medium mb-4">
            HAPPENING NOW
          </div>
          <h2 className="text-3xl font-bold mb-2">{filmFestivalEvent.title}</h2>
          <p className="text-purple-200 mb-4">{filmFestivalEvent.date}</p>
          <p className="text-white mb-6">{filmFestivalEvent.description}</p>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {filmFestivalEvent.languages.slice(0, 5).map((lang, index) => (
              <span key={index} className="bg-purple-700 px-3 py-1 rounded-full text-xs">
                {lang}
              </span>
            ))}
            {filmFestivalEvent.languages.length > 5 && (
              <span className="bg-purple-700 px-3 py-1 rounded-full text-xs">
                +{filmFestivalEvent.languages.length - 5} more
              </span>
            )}
          </div>
          
          <div className="flex gap-4">
            <button className="bg-red-500 hover:bg-red-600 px-6 py-2 rounded-lg font-medium transition duration-150">
              Book Now
            </button>
            <button className="border border-white hover:bg-white hover:text-purple-900 px-6 py-2 rounded-lg font-medium transition duration-150">
              View Details
            </button>
          </div>
        </div>
        <div className="w-full md:w-1/3">
          <img 
            src="/api/placeholder/400/300" 
            alt={filmFestivalEvent.title}
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>
  );
};

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <NavBar />
      
      <div className="max-w-screen-xl mx-auto">
        <div className="my-4 px-4">
          <Banner banner={banners[0]} />
        </div>
        
        <Section title="Recommended Movies">
          {recommendedMovies.map((movie, index) => (
            <MovieCard 
              key={movie.id} 
              movie={movie} 
              promoted={index === 0}
            />
          ))}
        </Section>
        
        <div className="px-4">
          <FilmFestivalBanner />
        </div>
        
        <FeaturedSection 
          title="Film Festival Events & Workshops" 
          events={featuredEvents}
        />
        
        <Section title="Top Games & Sport Events">
          {sportEvents.map((event, index) => (
            <EventCard 
              key={event.id} 
              event={event} 
              promoted={index === 0}
            />
          ))}
        </Section>
        
        <PremiereSection movies={premiereMovies} />
        
        <Section title="Explore Fun Activities">
          {/* Content for Activities would go here */}
          <div className="flex-1 h-40 bg-white rounded-lg shadow-md flex items-center justify-center">
            <p className="text-purple-700">Activity content would go here</p>
          </div>
        </Section>
      </div>
      
      <footer className="bg-purple-900 text-white py-8 px-4 mt-8">
        <div className="max-w-screen-xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-6">
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

export default HomePage;