import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as XGBRegressor
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import warnings
import joblib

# Suppress warnings
warnings.filterwarnings('ignore')

# Download nltk resources (uncomment if needed)
# nltk.download('vader_lexicon')

# Function to load and prepare data
def load_data(file_path):
    try:
        # Try reading with various date formats
        df = pd.read_csv(file_path, parse_dates=['portal_listing_date', 'actual_event_date', 'user_registration_date'])
    except:
        # If automatic parsing fails, try manual conversion
        df = pd.read_csv(file_path)
        
        # Handle different date formats
        date_columns = ['portal_listing_date', 'actual_event_date', 'user_registration_date']
        for col in date_columns:
            if col in df.columns:
                # Try multiple date formats
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    try:
                        df[col] = pd.to_datetime(df[col], format='%d-%m-%Y')
                    except:
                        try:
                            df[col] = pd.to_datetime(df[col], format='%Y-%m-%d')
                        except:
                            print(f"Warning: Could not parse dates in column {col}. Treating as string.")
    
    print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
    return df

# Feature engineering function
def engineer_features(df):
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # Extract temporal features if date columns exist
    if 'portal_listing_date' in df_processed.columns and 'actual_event_date' in df_processed.columns:
        # Time between listing and event
        df_processed['days_until_event'] = (df_processed['actual_event_date'] - df_processed['portal_listing_date']).dt.days
        
        # Is the event on a weekend?
        if 'day_of_week' in df_processed.columns:
            df_processed['is_weekend'] = df_processed['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)
        else:
            df_processed['is_weekend'] = df_processed['actual_event_date'].dt.dayofweek.isin([5, 6]).astype(int)
        
        # Season of event
        df_processed['season'] = df_processed['actual_event_date'].dt.month.apply(
            lambda x: 'Winter' if x in [12, 1, 2] else 
                     'Spring' if x in [3, 4, 5] else
                     'Summer' if x in [6, 7, 8] else 'Fall'
        )
        
        # Is holiday season? (November-December)
        df_processed['is_holiday_season'] = df_processed['actual_event_date'].dt.month.isin([11, 12]).astype(int)
        
        # User registration recency
        if 'user_registration_date' in df_processed.columns:
            df_processed['user_account_age_days'] = (df_processed['portal_listing_date'] - df_processed['user_registration_date']).dt.days
    
    # Add sentiment features if sentiment column exists
    if 'sentiment' in df_processed.columns:
        # Initialize sentiment analyzer
        try:
            sid = SentimentIntensityAnalyzer()
            
            # Extract sentiment scores
            df_processed['sentiment_score'] = df_processed['sentiment'].apply(
                lambda x: sid.polarity_scores(str(x))['compound'] if pd.notnull(x) else 0
            )
            
            # Categorize sentiment
            df_processed['sentiment_category'] = df_processed['sentiment_score'].apply(
                lambda score: 'positive' if score > 0.05 else 'negative' if score < -0.05 else 'neutral'
            )
        except:
            print("Warning: Could not perform sentiment analysis. NLTK Vader might not be installed.")
            # Create a simple sentiment score based on text length as fallback
            df_processed['sentiment_score'] = df_processed['sentiment'].apply(
                lambda x: len(str(x)) / 100 if pd.notnull(x) else 0
            )
    
    # Geographic features if coordinates exist
    if 'latitude' in df_processed.columns and 'longitude' in df_processed.columns:
        # Calculate distance from major cities (simple example)
        major_cities = {
            'New_York': (40.7128, -74.0060),
            'LA': (34.0522, -118.2437),
            'Chicago': (41.8781, -87.6298),
            'London': (51.5074, -0.1278)
        }
        
        for city, (lat, lon) in major_cities.items():
            df_processed[f'distance_to_{city}'] = np.sqrt(
                (df_processed['latitude'] - lat)**2 + (df_processed['longitude'] - lon)**2
            )
    
    # Handle lag features
    lag_columns = [col for col in df_processed.columns if col.startswith('lag')]
    for col in lag_columns:
        # Fill missing lag values with median
        df_processed[col] = df_processed[col].fillna(df_processed[col].median())
    
    # Feature for price category
    if 'ticket_price' in df_processed.columns:
        df_processed['price_category'] = pd.qcut(df_processed['ticket_price'], 5, labels=False)
    
    return df_processed

# Function to prepare data for modeling
def prepare_for_modeling(df, target_column='lag1_sales'):
    # Define feature sets
    if target_column == 'lag1_sales' and 'lag1_sales' in df.columns:
        # If predicting lag1, we can use lag2 and lag3 as features
        possible_target_features = ['lag2_sales', 'lag3_sales']
        target_features = [col for col in possible_target_features if col in df.columns]
    else:
        target_features = []
    
    # Identify categorical and numerical columns
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object' or 
                        col in ['season', 'sentiment_category', 'price_category', 'month', 'year', 'week_of_year']]
    
    # Remove the target and text columns from features
    exclude_cols = [target_column, 'sentiment'] + [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
    categorical_cols = [col for col in categorical_cols if col not in exclude_cols]
    
    # Numeric columns (excluding dates and target)
    numeric_cols = [col for col in df.columns if col not in categorical_cols + exclude_cols and 
                   df[col].dtype in ['int64', 'float64']]
    
    # Include target-specific features
    numeric_cols = target_features + [col for col in numeric_cols if col not in target_features]
    
    # Print selected features
    print(f"Target: {target_column}")
    print(f"Categorical features: {categorical_cols}")
    print(f"Numerical features: {numeric_cols}")
    
    # Create target variable
    y = df[target_column].values
    
    # Create feature set
    X = df[categorical_cols + numeric_cols]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test, categorical_cols, numeric_cols

# Function to build and evaluate multiple models
def build_models(X_train, X_test, y_train, y_test, categorical_cols, numeric_cols):
    # Preprocessing for numerical data
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Preprocessing for categorical data
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])
    
    # Define base models
    models = {
        "RandomForest": RandomForestRegressor(random_state=42),
        "GradientBoosting": GradientBoostingRegressor(random_state=42),
        "XGBoost": XGBRegressor.XGBRegressor(random_state=42),
        "LightGBM": lgb.LGBMRegressor(random_state=42),
        "CatBoost": CatBoostRegressor(random_state=42, verbose=0),
        "ElasticNet": ElasticNet(random_state=42)
    }
    
    # Dictionary to store results
    results = {}
    best_model = None
    best_score = -np.inf
    
    # Train and evaluate each model
    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        
        # Create pipeline with preprocessing and model
        pipe = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Fit model
        pipe.fit(X_train, y_train)
        
        # Make predictions
        y_pred = pipe.predict(X_test)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Store results
        results[model_name] = {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'pipeline': pipe
        }
        
        print(f"{model_name} - RMSE: {rmse:.2f}, MAE: {mae:.2f}, R²: {r2:.4f}")
        
        # Update best model
        if r2 > best_score:
            best_score = r2
            best_model = model_name
    
    print(f"\nBest model: {best_model} with R² score of {best_score:.4f}")
    
    # Return the best model and results
    return results[best_model]['pipeline'], results

# Function to tune the best model
def tune_best_model(best_pipeline, X_train, y_train, categorical_cols, numeric_cols, model_type):
    print(f"\nTuning {model_type} model...")
    
    # Define parameter grid based on model type
    if model_type == "RandomForest":
        param_grid = {
            'model__n_estimators': [100, 200, 300],
            'model__max_depth': [None, 10, 20, 30],
            'model__min_samples_split': [2, 5, 10]
        }
    elif model_type == "GradientBoosting":
        param_grid = {
            'model__n_estimators': [100, 200, 300],
            'model__learning_rate': [0.01, 0.05, 0.1],
            'model__max_depth': [3, 5, 7]
        }
    elif model_type == "XGBoost":
        param_grid = {
            'model__n_estimators': [100, 200, 300],
            'model__learning_rate': [0.01, 0.05, 0.1],
            'model__max_depth': [3, 5, 7]
        }
    elif model_type == "LightGBM":
        param_grid = {
            'model__n_estimators': [100, 200, 300],
            'model__learning_rate': [0.01, 0.05, 0.1],
            'model__num_leaves': [31, 50, 70]
        }
    elif model_type == "CatBoost":
        param_grid = {
            'model__iterations': [100, 200, 300],
            'model__learning_rate': [0.01, 0.05, 0.1],
            'model__depth': [4, 6, 8]
        }
    else:  # ElasticNet
        param_grid = {
            'model__alpha': [0.01, 0.1, 1.0],
            'model__l1_ratio': [0.1, 0.5, 0.9]
        }
    
    # Create grid search
    grid_search = GridSearchCV(
        best_pipeline,
        param_grid,
        cv=5,
        scoring='r2',
        n_jobs=-1
    )
    
    # Fit grid search
    grid_search.fit(X_train, y_train)
    
    # Print best parameters
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

# Function to save model and make predictions
def save_and_predict(model, X_test, y_test, model_filename="ticket_sales_prediction_model.pkl"):
    # Save model
    joblib.dump(model, model_filename)
    print(f"\nModel saved as {model_filename}")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate final metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nFinal model performance:")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"R²: {r2:.4f}")
    
    # Create a scatter plot of actual vs predicted values
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--')
    plt.xlabel('Actual Sales')
    plt.ylabel('Predicted Sales')
    plt.title('Actual vs Predicted Sales')
    plt.tight_layout()
    plt.savefig('sales_prediction_performance.png')
    
    return y_pred, rmse, mae, r2

# Function to extract feature importance
def analyze_feature_importance(model, categorical_cols, numeric_cols):
    try:
        # Get feature names after preprocessing
        preprocessor = model.named_steps['preprocessor']
        model_step = model.named_steps['model']
        
        # Get feature names after one-hot encoding
        feature_names = []
        
        # Get transformed column names for numeric features
        if numeric_cols:
            feature_names.extend(numeric_cols)
        
        # Get transformed column names for categorical features
        if categorical_cols:
            # Get the onehotencoder
            onehotencoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
            # Get the categories
            categories = onehotencoder.categories_
            
            for i, category in enumerate(categories):
                for cat_value in category:
                    feature_names.append(f"{categorical_cols[i]}_{cat_value}")
        
        # Extract feature importances if the model supports it
        if hasattr(model_step, 'feature_importances_'):
            importances = model_step.feature_importances_
            
            # Create a DataFrame of feature importances
            feature_importance_df = pd.DataFrame({
                'Feature': feature_names[:len(importances)],
                'Importance': importances
            })
            
            # Sort by importance
            feature_importance_df = feature_importance_df.sort_values('Importance', ascending=False)
            
            # Plot feature importances
            plt.figure(figsize=(12, 8))
            sns.barplot(x='Importance', y='Feature', data=feature_importance_df.head(20))
            plt.title('Top 20 Feature Importances')
            plt.tight_layout()
            plt.savefig('feature_importance.png')
            
            return feature_importance_df
        else:
            print("Model doesn't support feature importances.")
            return None
    except Exception as e:
        print(f"Error extracting feature importance: {e}")
        return None

# Function to run the prediction system
def run_ticket_sales_prediction(file_path, target_column='lag1_sales'):
    # Load data
    df = load_data(file_path)
    
    # Engineer features
    df_processed = engineer_features(df)
    
    # Prepare data for modeling
    X_train, X_test, y_train, y_test, categorical_cols, numeric_cols = prepare_for_modeling(df_processed, target_column)
    
    # Build and evaluate models
    best_pipeline, results = build_models(X_train, X_test, y_train, y_test, categorical_cols, numeric_cols)
    
    # Get the best model type
    best_model_type = best_pipeline.named_steps['model'].__class__.__name__
    if 'XGB' in best_model_type:
        best_model_type = 'XGBoost'
    elif 'LGBM' in best_model_type:
        best_model_type = 'LightGBM'
    elif 'CatBoost' in best_model_type:
        best_model_type = 'CatBoost'
    
    # Tune the best model
    tuned_model = tune_best_model(best_pipeline, X_train, y_train, categorical_cols, numeric_cols, best_model_type)
    
    # Save model and get predictions
    y_pred, rmse, mae, r2 = save_and_predict(tuned_model, X_test, y_test)
    
    # Analyze feature importance
    feature_importance = analyze_feature_importance(tuned_model, categorical_cols, numeric_cols)
    
    print("\nTicket sales prediction model training complete!")
    print(f"Best model: {best_model_type}")
    
    return tuned_model, feature_importance

# Prediction function for new data
def predict_sales(model, new_data_file):
    # Load new data
    new_df = load_data(new_data_file)
    
    # Apply same feature engineering
    new_df_processed = engineer_features(new_df)
    
    # Make predictions
    predictions = model.predict(new_df_processed)
    
    # Add predictions to the dataframe
    new_df_processed['predicted_sales'] = predictions
    
    return new_df_processed

# Main execution
if __name__ == "__main__":
    # File path to your CSV
    file_path = "ticket_sales_prediction_data.csv"  # Replace with your actual file path
    
    # Run the prediction system
    model, feature_importance = run_ticket_sales_prediction(file_path)
    
    # Print top features
    if feature_importance is not None:
        print("\nTop 10 most important features:")
        print(feature_importance.head(10))