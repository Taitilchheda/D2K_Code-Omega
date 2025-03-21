import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load the pricing data
pricing_data = pd.read_csv('event_pricing_data.csv')

# Define the features (demand, time_to_event, competitor_price, event_popularity) 
# and the target variable (base_price)
X = pricing_data[['demand', 'time_to_event', 'competitor_price', 'event_popularity']]  # Features

# Target variable: The base price
y = pricing_data['base_price']  # Price column (target)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build and train a linear regression model
regressor = LinearRegression()
regressor.fit(X_train, y_train)

# Predict the prices on the test set
y_pred = regressor.predict(X_test)

# Calculate the RMSE (Root Mean Squared Error)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"RMSE: {rmse}")

# Function to predict dynamic price for a new event
def predict_dynamic_price(demand, time_to_event, competitor_price, event_popularity):
    price = regressor.predict([[demand, time_to_event, competitor_price, event_popularity]])
    return price[0]

# Example: Predict the price for an event with 500 demand, 30 days until the event, 
# a competitor price of $80, and event popularity score of 0.7
predicted_price = predict_dynamic_price(500, 30, 80, 0.7)
print(f"Predicted Dynamic Price: ₹{predicted_price:.2f}")
