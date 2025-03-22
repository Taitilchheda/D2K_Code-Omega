import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Function to generate more detailed sentiment text
def generate_sentiment_text(sentiment_type):
    positive_sentiments = [
        "Loved the event! Amazing experience and well organized.",
        "Great atmosphere and perfect venue. Would definitely attend again!",
        "The event exceeded my expectations. Worth every penny!",
        "Fantastic experience! The organizers did an excellent job.",
        "One of the best events I've attended this year. Highly recommend!"
    ]
    
    neutral_sentiments = [
        "Event was okay, nothing special to be honest.",
        "Decent event but could have been better organized.",
        "Average experience, met my basic expectations.",
        "The event was fine, but I expected more for the ticket price.",
        "Not bad, but not great either. Probably wouldn't go again."
    ]
    
    negative_sentiments = [
        "Disappointed with the entire experience. Not worth the money.",
        "Poor organization led to long waiting times and frustration.",
        "The event fell short of what was advertised. Wouldn't recommend.",
        "Waste of time and money. Very underwhelming experience.",
        "Terrible venue choice and lackluster performance. Huge letdown."
    ]
    
    if sentiment_type == 'positive':
        return random.choice(positive_sentiments)
    elif sentiment_type == 'neutral':
        return random.choice(neutral_sentiments)
    else:
        return random.choice(negative_sentiments)

# Define popular event locations with realistic coordinates
event_locations = {
    "New York": {"lat_range": (40.65, 40.85), "long_range": (-74.1, -73.9)},
    "Los Angeles": {"lat_range": (33.9, 34.1), "long_range": (-118.3, -118.1)},
    "Chicago": {"lat_range": (41.75, 41.95), "long_range": (-87.75, -87.55)},
    "London": {"lat_range": (51.4, 51.6), "long_range": (-0.2, 0.0)},
    "Tokyo": {"lat_range": (35.6, 35.8), "long_range": (139.6, 139.8)},
    "Sydney": {"lat_range": (-33.95, -33.8), "long_range": (151.1, 151.3)},
    "Paris": {"lat_range": (48.8, 49.0), "long_range": (2.25, 2.45)},
    "Berlin": {"lat_range": (52.45, 52.55), "long_range": (13.3, 13.5)},
    "Toronto": {"lat_range": (43.6, 43.8), "long_range": (-79.5, -79.3)},
    "Mumbai": {"lat_range": (18.9, 19.1), "long_range": (72.7, 72.9)}
}

# Function to generate random data with improved realism
def generate_data(num_entries):
    data = []
    
    # Create a list of event categories to make price ranges more realistic
    event_categories = [
        {"name": "Concert", "price_range": (50, 500)},
        {"name": "Comedy Show", "price_range": (25, 120)},
        {"name": "Sports Event", "price_range": (30, 450)},
        {"name": "Theater", "price_range": (40, 300)},
        {"name": "Exhibition", "price_range": (15, 80)},
        {"name": "Conference", "price_range": (100, 1000)},
        {"name": "Workshop", "price_range": (30, 200)},
        {"name": "Festival", "price_range": (45, 350)}
    ]
    
    # Generate a sequence of events with realistic scheduling
    end_date = datetime.today()
    start_date = end_date - timedelta(days=730)  # Two years of data
    
    # Create distribution for lead time between listing and event
    # Most events are listed 1-2 months ahead, some earlier, some last minute
    lead_time_weights = [1, 2, 5, 15, 25, 20, 15, 10, 5, 2]  # Distribution across 0-9 months
    
    for _ in range(num_entries):
        # Select random event category
        event_category = random.choice(event_categories)
        
        # Generate realistic listing date within the date range
        days_from_start = random.randint(0, (end_date - start_date).days)
        listing_date = start_date + timedelta(days=days_from_start)
        
        # More realistic lead time between listing and event date
        lead_time_month = random.choices(range(10), weights=lead_time_weights, k=1)[0]
        lead_time_days = lead_time_month * 30 + random.randint(1, 30)
        event_date = listing_date + timedelta(days=lead_time_days)
        
        # Random event ID (with prefix for event type)
        event_id = f"EV-{event_category['name'][:3].upper()}-{random.randint(10000, 99999)}"
        
        # Extract date components
        day = event_date.day
        week = int(event_date.strftime('%U'))  # Week number as integer
        month = event_date.month
        year = event_date.year
        day_of_week = event_date.weekday()  # 0-6 representing Monday-Sunday
        
        # More realistic lag features (previous periods' ticket sales)
        # Higher variance for popular events, lower for niche events
        base_popularity = random.randint(20, 200)
        noise_factor = random.uniform(0.5, 1.5)
        
        # Sales typically increase as the event approaches
        lag3 = int(base_popularity * noise_factor * 0.3)  # Earliest period has fewer sales
        lag2 = int(base_popularity * noise_factor * 0.6)  # Middle period
        lag1 = int(base_popularity * noise_factor)        # Latest period has most sales
        
        # Select a location and get realistic coordinates
        location_name = random.choice(list(event_locations.keys()))
        location = event_locations[location_name]
        latitude = round(random.uniform(location["lat_range"][0], location["lat_range"][1]), 6)
        longitude = round(random.uniform(location["long_range"][0], location["long_range"][1]), 6)
        
        # More realistic ticket price based on event category
        price = round(random.uniform(event_category["price_range"][0], event_category["price_range"][1]), 2)
        
        # User registration date (users typically register well before buying tickets)
        max_reg_days_before = min(365 * 5, (listing_date - datetime(2015, 1, 1)).days)  # Cap at 5 years or platform start
        user_registration_date = listing_date - timedelta(days=random.randint(1, max_reg_days_before))
        
        # More realistic sentiment distribution (positive skew but with some negativity)
        sentiment_types = ['positive', 'neutral', 'negative']
        sentiment_weights = [0.6, 0.3, 0.1]  # Most people leave positive reviews
        sentiment_type = random.choices(sentiment_types, weights=sentiment_weights, k=1)[0]
        sentiment_text = generate_sentiment_text(sentiment_type)
        
        # Add event category for more context
        category = event_category["name"]
        
        # Weather condition can affect attendance (will be correlated with location and month)
        weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Hot", "Cold"]
        weather_weights = generate_weather_weights(month, location_name)
        weather = random.choices(weather_conditions, weights=weather_weights, k=1)[0]
        
        # Calculate days until event from listing date
        days_until_event = (event_date - listing_date).days
        
        # Add to data list with all fields
        data.append([
            listing_date, event_date, event_id, day, week, month, year, day_of_week,
            lag1, lag2, lag3, latitude, longitude, price, user_registration_date,
            sentiment_text, sentiment_type, category, location_name, weather, days_until_event
        ])

    return data

# Helper function to generate weather weights based on month and location
def generate_weather_weights(month, location):
    # Default weights
    weights = [0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1]  # Sunny, Cloudy, Rainy, Snowy, Windy, Hot, Cold
    
    # Northern hemisphere seasonal adjustments
    northern = ["New York", "Los Angeles", "Chicago", "London", "Paris", "Berlin", "Tokyo"]
    southern = ["Sydney", "Mumbai"]  # Southern hemisphere has opposite seasons
    
    if location in northern:
        if month in [12, 1, 2]:  # Winter
            weights = [0.1, 0.2, 0.1, 0.3, 0.1, 0.0, 0.2]
        elif month in [3, 4, 5]:  # Spring
            weights = [0.3, 0.3, 0.2, 0.05, 0.1, 0.05, 0.0]
        elif month in [6, 7, 8]:  # Summer
            weights = [0.4, 0.2, 0.1, 0.0, 0.1, 0.2, 0.0]
        else:  # Fall
            weights = [0.2, 0.3, 0.3, 0.0, 0.1, 0.0, 0.1]
    
    elif location in southern:
        if month in [12, 1, 2]:  # Summer in southern hemisphere
            weights = [0.4, 0.2, 0.1, 0.0, 0.1, 0.2, 0.0]
        elif month in [3, 4, 5]:  # Fall
            weights = [0.2, 0.3, 0.3, 0.0, 0.1, 0.0, 0.1]
        elif month in [6, 7, 8]:  # Winter
            weights = [0.1, 0.2, 0.3, 0.0, 0.1, 0.0, 0.3]  # Less snow in Sydney
        else:  # Spring
            weights = [0.3, 0.3, 0.2, 0.0, 0.1, 0.1, 0.0]
    
    # Special case for Mumbai - monsoon season (June-September)
    if location == "Mumbai" and month in [6, 7, 8, 9]:
        weights = [0.1, 0.2, 0.5, 0.0, 0.1, 0.1, 0.0]  # More rain
        
    return weights

# Number of entries to generate
num_entries = 10000

# Enhanced column names for the CSV
columns = [
    'listing_date', 'event_date', 'event_id', 'day', 'week', 'month', 'year', 'day_of_week',
    'lag1', 'lag2', 'lag3', 'latitude', 'longitude', 'price', 'user_registration_date',
    'sentiment_text', 'sentiment_type', 'event_category', 'location', 'weather', 'days_until_event'
]

# Generate data
data = generate_data(num_entries)

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Save to CSV
csv_filename = "ticket_sales_prediction_10000_enhanced.csv"
df.to_csv(csv_filename, index=False)

print(f"CSV file '{csv_filename}' with {num_entries} rows has been generated.")
print("\nSample data (first 5 rows):")
print(df.head())