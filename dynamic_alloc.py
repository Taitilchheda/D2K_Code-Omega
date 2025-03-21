import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

# 1. Generate Synthetic Custom Data (You can replace this with your actual data)
def generate_synthetic_data(num_entries=100):
    data = []
    for _ in range(num_entries):
        event_date = pd.Timestamp.now() + pd.Timedelta(days=np.random.randint(1, 90))  # Random future dates
        ticket_type = np.random.choice(['Regular', 'VIP'], p=[0.8, 0.2])
        seats_available = np.random.randint(100, 500)
        demand = np.random.uniform(0.1, 0.9)  # Demand percentage (e.g., 70% of tickets sold)
        time_remaining = (event_date - pd.Timestamp.now()).days
        base_price = 100  # A base price for simplicity
        
        # Apply dynamic pricing logic (you can modify this part)
        dynamic_price = base_price * (1 + 1.5 * (1 - demand))  # Example simple formula
        dynamic_price *= (1 + 0.5 * (30 - time_remaining) / 30)  # As time decreases, price increases
        dynamic_price *= (1 + 2.0 * (1 - seats_available / 500))  # As seats decrease, price increases
        
        data.append([event_date, ticket_type, seats_available, demand, time_remaining, dynamic_price])
    return pd.DataFrame(data, columns=['Event Date', 'Ticket Type', 'Seats Available', 'Demand', 'Time Remaining', 'Dynamic Price'])

# 2. Load custom data (you can load your CSV by using pd.read_csv('your_file.csv'))
df_custom = generate_synthetic_data()

# Display the first few rows of the dataset
print(df_custom.head())

# 3. Preprocess the Data
# Encode the categorical 'Ticket Type' column into numerical values
label_encoder = LabelEncoder()
df_custom['Ticket Type'] = label_encoder.fit_transform(df_custom['Ticket Type'])

# Features (independent variables) and Target (dependent variable)
X = df_custom[['Seats Available', 'Demand', 'Time Remaining', 'Ticket Type']]  # Features
y = df_custom['Dynamic Price']  # Target variable

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train a Linear Regression Model
model = LinearRegression()
model.fit(X_train, y_train)

# 5. Evaluate the Model
# Predict the prices for the test set
y_pred = model.predict(X_test)

# Calculate the mean squared error (MSE) for evaluation
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# 6. Make Predictions for New Data
# Example: Predicting the dynamic price for a new event
new_data = pd.DataFrame({
    'Seats Available': [150],
    'Demand': [0.4],
    'Time Remaining': [25],
    'Ticket Type': [label_encoder.transform(['VIP'])[0]]  # Encoding 'VIP' as numeric
})

# Predict the dynamic price for the new event
predicted_price = model.predict(new_data)
print("Predicted Dynamic Price for New Event:", predicted_price[0])

# 7. Optionally, Show the Predicted Prices for the Test Set
# You can compare the actual prices to the predicted ones
predicted_vs_actual = pd.DataFrame({
    'Actual Price': y_test,
    'Predicted Price': y_pred
})

print(predicted_vs_actual.head())
