import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import csv
from faker import Faker
import uuid

# Initialize Faker for generating realistic text
fake = Faker()

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Define the number of rows to generate
num_rows = 7500  # Adjust as needed within your range of 5000-10000

# Create a function to generate sentiment text
def generate_sentiment():
    sentiments = [
        "Event was amazing! Would definitely go again.",
        "Great atmosphere and perfect organization.",
        "Event was okay, nothing special.",
        "Disappointed with the event, not worth the price.",
        "Had a wonderful time, exceeded my expectations!",
        "The event was good but could use better organization.",
        "Mediocre experience, wouldn't recommend.",
        "Absolutely loved it! Can't wait for the next one.",
        "Not what I expected, slightly underwhelming.",
        "Decent event but overpriced for what it was."
    ]
    return random.choice(sentiments)

# Create data
data = []

# Start date for generating events
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)
total_days = (end_date - start_date).days

# Define some popular locations for events
locations = [
    (40.7128, -74.0060),  # New York
    (34.0522, -118.2437),  # Los Angeles
    (41.8781, -87.6298),   # Chicago
    (29.7604, -95.3698),   # Houston
    (39.9526, -75.1652),   # Philadelphia
    (51.5074, -0.1278),    # London
    (48.8566, 2.3522),     # Paris
    (35.6762, 139.6503),   # Tokyo
    (19.4326, -99.1332),   # Mexico City
    (55.7558, 37.6173)     # Moscow
]

# Generate event IDs in advance to use for lags
event_ids = [str(uuid.uuid4())[:8] for _ in range(num_rows)]

# Generate timestamps and basic event data
events = []
for i in range(num_rows):
    # Generate event date
    random_days = random.randint(0, total_days)
    actual_event_date = start_date + timedelta(days=random_days)
    
    # Portal listing date (typically 1-90 days before the event)
    listing_days_before = random.randint(1, 90)
    portal_listing_date = actual_event_date - timedelta(days=listing_days_before)
    
    # Random location
    lat, lng = random.choice(locations)
    lat += random.uniform(-0.1, 0.1)  # Add some variation
    lng += random.uniform(-0.1, 0.1)  # Add some variation
    
    # Price (between $10 and $250)
    price = round(random.uniform(10, 250), 2)
    
    events.append({
        "event_id": event_ids[i],
        "actual_event_date": actual_event_date,
        "portal_listing_date": portal_listing_date,
        "latitude": round(lat, 4),
        "longitude": round(lng, 4),
        "price": price
    })

# Sort events by date for realistic lag creation
events.sort(key=lambda x: x["actual_event_date"])

# Create final dataset with all features
for i, event in enumerate(events):
    # Calculate day of week, week, month, year
    event_date = event["actual_event_date"]
    day_of_week = event_date.strftime("%A")
    week_of_year = event_date.isocalendar()[1]
    month = event_date.month
    year = event_date.year
    
    # Create lag features (previous sales if available)
    lag1 = random.randint(50, 500) if i > 0 else np.nan
    lag2 = random.randint(40, 450) if i > 1 else np.nan
    lag3 = random.randint(30, 400) if i > 2 else np.nan
    
    # User registration date (between 1-365 days before portal listing)
    reg_days_before = random.randint(1, 365)
    user_reg_date = event["portal_listing_date"] - timedelta(days=reg_days_before)
    
    # Sentiment text
    sentiment = generate_sentiment()
    
    # Add row to data
    data.append({
        "portal_listing_date": event["portal_listing_date"].strftime("%Y-%m-%d"),
        "actual_event_date": event["actual_event_date"].strftime("%Y-%m-%d"),
        "event_id": event["event_id"],
        "day_of_week": day_of_week,
        "week_of_year": week_of_year,
        "month": month,
        "year": year,
        "lag1_sales": lag1,
        "lag2_sales": lag2, 
        "lag3_sales": lag3,
        "latitude": event["latitude"],
        "longitude": event["longitude"],
        "ticket_price": event["price"],
        "user_registration_date": user_reg_date.strftime("%Y-%m-%d"),
        "sentiment": sentiment
    })

# Convert to DataFrame and save to CSV
df = pd.DataFrame(data)

# Write to CSV
csv_filename = "ticket_sales_prediction_data.csv"
df.to_csv(csv_filename, index=False)

print(f"Dataset created with {len(df)} rows and saved to {csv_filename}")
print(f"Sample of the first 5 rows:")
print(df.head())