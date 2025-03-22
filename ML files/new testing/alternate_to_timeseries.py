import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
import matplotlib.pyplot as plt
import pickle

# Load the new dataset
data = pd.read_csv('ticket_sales_prediction_data.csv', parse_dates=['portal_listing_date', 'actual_event_date', 'user_registration_date'])

# Check the date range to ensure there are dates beyond 2025-01-01
print("Min actual_event_date:", data['actual_event_date'].min())
print("Max actual_event_date:", data['actual_event_date'].max())

# Parse necessary date features
data['day_of_week'] = data['actual_event_date'].dt.dayofweek
data['week_of_year'] = data['actual_event_date'].dt.isocalendar().week
data['month'] = data['actual_event_date'].dt.month
data['year'] = data['actual_event_date'].dt.year
data['day_of_year'] = data['actual_event_date'].dt.dayofyear

# Encode some cyclical features
data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)
data['day_of_year_sin'] = np.sin(2 * np.pi * data['day_of_year'] / 365)
data['day_of_year_cos'] = np.cos(2 * np.pi * data['day_of_year'] / 365)

# Handle sales lags (assuming the sales column is present, if not, you'd need to compute or simulate this)
data['lag_1'] = data['lag1_sales']
data['lag_2'] = data['lag2_sales']
data['lag_3'] = data['lag3_sales']

# Drop rows where any sales-related or necessary data is missing
data = data.dropna(subset=['lag_1', 'lag_2', 'lag_3'])

# Prepare features (assuming 'sales' is based on 'lag1_sales', 'lag2_sales', or other columns)
# Here I am assuming 'lag1_sales' represents actual sales to predict
data['sales'] = data['lag_1']  # or you could select another column if relevant

# Feature engineering
X = data[['day_of_week', 'week_of_year', 'month', 'year', 'day_of_year', 'month_sin', 'month_cos', 
          'day_of_year_sin', 'day_of_year_cos', 'lag_1', 'lag_2', 'lag_3', 'latitude', 'longitude', 'ticket_price']]
y = data['sales']

# Adjust the train-test split if needed based on actual event dates
train_data = data[data['actual_event_date'] < '2024-01-01']  # Change date to match your data
test_data = data[data['actual_event_date'] >= '2024-01-01']  # Change date to match your data

# Ensure that the split produces non-empty train and test datasets
print(f"Train data size: {len(train_data)}")
print(f"Test data size: {len(test_data)}")

# If test data is empty, adjust the date range
if len(test_data) == 0:
    print("No test data found! Adjusting date for split.")
    train_data = data[data['actual_event_date'] < '2023-01-01']
    test_data = data[data['actual_event_date'] >= '2023-01-01']

# Train-test split
X_train = train_data[['day_of_week', 'week_of_year', 'month', 'year', 'day_of_year', 'month_sin', 'month_cos', 
                      'day_of_year_sin', 'day_of_year_cos', 'lag_1', 'lag_2', 'lag_3', 'latitude', 'longitude', 'ticket_price']]
y_train = train_data['sales']
X_test = test_data[['day_of_week', 'week_of_year', 'month', 'year', 'day_of_year', 'month_sin', 'month_cos', 
                    'day_of_year_sin', 'day_of_year_cos', 'lag_1', 'lag_2', 'lag_3', 'latitude', 'longitude', 'ticket_price']]
y_test = test_data['sales']

# Hyperparameter tuning for Random Forest
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10], 
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['auto', 'sqrt', 'log2'],
}

grid_search = GridSearchCV(estimator=RandomForestRegressor(random_state=42), 
                           param_grid=param_grid, 
                           cv=3, 
                           scoring='neg_mean_squared_error', 
                           verbose=2, 
                           n_jobs=-1)

grid_search.fit(X_train, y_train)

# Best model from grid search
best_model = grid_search.best_estimator_

# Predict on test set
y_pred = best_model.predict(X_test)

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"Mean Absolute Error: {mae}")
print(f"Root Mean Squared Error: {rmse}")

# Plot actual vs predicted sales
plt.figure(figsize=(10, 6))
plt.plot(test_data['actual_event_date'], y_test, label='Actual Sales')
plt.plot(test_data['actual_event_date'], y_pred, label='Predicted Sales', color='red')
plt.legend()
plt.title('Event Ticket Sales Forecasting with Random Forest Regressor')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.show()

# Save the best model to a file
def save_model(model, filename):
    with open(filename, 'wb') as file:
        pickle.dump(model, file)
    print(f"Model saved to {filename}")

save_model(best_model, 'ticket_sales_random_forest_model_data.pkl')
