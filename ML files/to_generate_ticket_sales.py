import pandas as pd
import numpy as np

# Set the date range from 2010 to 2024
date_range = pd.date_range(start='2010-01-01', end='2024-12-31', freq='D')

# Generate synthetic ticket sales data (random sales with some seasonal pattern)
np.random.seed(42)
sales = np.random.poisson(lam=50, size=len(date_range)) + np.sin(2 * np.pi * date_range.dayofyear / 365) * 20 + 50

# Simulate event_id to have values like 1 for events (randomly assigned for demonstration)
event_id = np.random.choice([1, 2], size=len(date_range), p=[0.5, 0.5])

# Create the DataFrame
ticket_sales_data = pd.DataFrame({
    'date': date_range,
    'sales': sales,
    'event_id': event_id
})

# Feature engineering
ticket_sales_data['day_of_week'] = ticket_sales_data['date'].dt.dayofweek
ticket_sales_data['month'] = ticket_sales_data['date'].dt.month
ticket_sales_data['day_of_year'] = ticket_sales_data['date'].dt.dayofyear
ticket_sales_data['is_weekend'] = ticket_sales_data['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

# Adding seasonal features
ticket_sales_data['month_sin'] = np.sin(2 * np.pi * ticket_sales_data['month'] / 12)
ticket_sales_data['month_cos'] = np.cos(2 * np.pi * ticket_sales_data['month'] / 12)
ticket_sales_data['day_of_year_sin'] = np.sin(2 * np.pi * ticket_sales_data['day_of_year'] / 365)
ticket_sales_data['day_of_year_cos'] = np.cos(2 * np.pi * ticket_sales_data['day_of_year'] / 365)

# Adding lag features
ticket_sales_data['lag_1'] = ticket_sales_data['sales'].shift(1)
ticket_sales_data['lag_2'] = ticket_sales_data['sales'].shift(2)
ticket_sales_data['lag_3'] = ticket_sales_data['sales'].shift(3)

# Drop rows with NaN values from lag columns
ticket_sales_data = ticket_sales_data.dropna()

# Set 'date' as the index
ticket_sales_data.set_index('date', inplace=True)

# Save the data to a CSV file
ticket_sales_data.to_csv('ticket_sales_data_large.csv')

print("Data saved to 'ticket_sales_data_large.csv'.")
