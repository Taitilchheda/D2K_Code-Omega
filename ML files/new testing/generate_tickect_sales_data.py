import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Function to generate random data
def generate_data(num_entries):
    data = []
    for _ in range(num_entries):
        # Random dates for listing date and actual event date
        listing_date = datetime.today() - timedelta(days=random.randint(30, 180))
        event_date = listing_date + timedelta(days=random.randint(1, 30))  # Event happens 1 to 30 days after listing

        # Random event ID
        event_id = random.randint(1000, 9999)

        # Random values for day, week, month, year based on event_date
        day = event_date.day
        week = event_date.strftime('%U')  # Week number
        month = event_date.month
        year = event_date.year

        # Lag features (previous event data)
        lag1 = random.randint(0, 100)
        lag2 = random.randint(0, 100)
        lag3 = random.randint(0, 100)

        # Random geographic location (latitude, longitude)
        latitude = round(random.uniform(-90, 90), 6)
        longitude = round(random.uniform(-180, 180), 6)

        # Ticket price
        price = round(random.uniform(10, 500), 2)

        # User registration date (random user joined before event)
        user_registration_date = listing_date - timedelta(days=random.randint(0, 180))

        # Sentiment (randomly generated sentiment in text)
        sentiments = ['positive', 'neutral', 'negative']
        sentiment = random.choice(sentiments)

        # Add to data list
        data.append([listing_date, event_date, event_id, day, week, month, year, lag1, lag2, lag3, latitude, longitude, price, user_registration_date, sentiment])

    return data

# Number of entries to generate (1 million rows)
num_entries = 1000000

# Column names for the CSV
columns = ['listing_date', 'event_date', 'event_id', 'day', 'week', 'month', 'year', 'lag1', 'lag2', 'lag3', 'latitude', 'longitude', 'price', 'user_registration_date', 'sentiment']

# Generate data
data = generate_data(num_entries)

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Save to CSV
csv_filename = "ticket_sales_prediction_large.csv"
df.to_csv(csv_filename, index=False)

print(f"CSV file '{csv_filename}' with {num_entries} rows has been generated.")
