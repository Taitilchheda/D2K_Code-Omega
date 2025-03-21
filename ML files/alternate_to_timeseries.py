import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
import matplotlib.pyplot as plt

ticket_sales_data = pd.read_csv('ticket_sales_data_large.csv', parse_dates=['date'], index_col='date')

ticket_sales_data['day_of_week'] = ticket_sales_data.index.dayofweek 
ticket_sales_data['month'] = ticket_sales_data.index.month
ticket_sales_data['day_of_year'] = ticket_sales_data.index.dayofyear
ticket_sales_data['is_weekend'] = ticket_sales_data['day_of_week'].apply(lambda x: 1 if x >= 5 else 0) 

ticket_sales_data['month_sin'] = np.sin(2 * np.pi * ticket_sales_data['month'] / 12)
ticket_sales_data['month_cos'] = np.cos(2 * np.pi * ticket_sales_data['month'] / 12)
ticket_sales_data['day_of_year_sin'] = np.sin(2 * np.pi * ticket_sales_data['day_of_year'] / 365)
ticket_sales_data['day_of_year_cos'] = np.cos(2 * np.pi * ticket_sales_data['day_of_year'] / 365)

ticket_sales_data['lag_1'] = ticket_sales_data['sales'].shift(1)
ticket_sales_data['lag_2'] = ticket_sales_data['sales'].shift(2)
ticket_sales_data['lag_3'] = ticket_sales_data['sales'].shift(3)

ticket_sales_data = ticket_sales_data.dropna()

event_sales = ticket_sales_data[ticket_sales_data['event_id'] == 1] 

event_sales = event_sales.resample('D').sum()

event_sales['sales'] = event_sales['sales'].replace(0, 1)

train_data = event_sales[:-30]
test_data = event_sales[-30:]

X_train = train_data[['day_of_week', 'month', 'day_of_year', 'is_weekend', 'month_sin', 'month_cos', 
                      'day_of_year_sin', 'day_of_year_cos', 'lag_1', 'lag_2', 'lag_3']]
y_train = train_data['sales']
X_test = test_data[['day_of_week', 'month', 'day_of_year', 'is_weekend', 'month_sin', 'month_cos', 
                    'day_of_year_sin', 'day_of_year_cos', 'lag_1', 'lag_2', 'lag_3']]
y_test = test_data['sales']

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

best_model = grid_search.best_estimator_

y_pred = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"Mean Absolute Error: {mae}")
print(f"Root Mean Squared Error: {rmse}")

plt.figure(figsize=(10, 6))
plt.plot(test_data.index, y_test, label='Actual Sales')
plt.plot(test_data.index, y_pred, label='Predicted Sales', color='red')
plt.legend()
plt.title('Event Ticket Sales Forecasting with Random Forest Regressor')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.show()
