import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load dataset
df = pd.read_csv('data/retail_store_inventory.csv')

# Extract 3 rows for later prediction
prediction_samples = df.iloc[:3].copy()
df = df.drop(index=prediction_samples.index)

# Define features and target
features = [
    'Category', 'Region', 'Inventory Level', 'Units Sold', 'Units Ordered',
    'Demand Forecast', 'Competitor Pricing', 'Weather Condition',
    'Holiday/Promotion', 'Seasonality', 'Discount'  
]
target = 'Price'

X = df[features]
y = df[target]

# Define categorical and numerical columns
categorical = ['Category', 'Region', 'Weather Condition', 'Holiday/Promotion', 'Seasonality']
numerical = [col for col in features if col not in categorical]

# Preprocessing: One-hot encode categorical features
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
], remainder='passthrough')

# Create pipeline
pipeline = Pipeline(steps=[
    ('preprocessing', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter grid for Random Forest
param_grid = {
    'regressor__n_estimators': [100, 200],
    'regressor__max_depth': [None, 10, 20],
    'regressor__min_samples_split': [2, 5],
    'regressor__min_samples_leaf': [1, 2],
    'regressor__max_features': ['sqrt', 'log2', None]
}

# Grid search
grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Best model
print(f"Best hyperparameters: {grid_search.best_params_}")
best_model = grid_search.best_estimator_

# Save model
joblib.dump(best_model, 'models/random_forest_model.pkl')
print("✅ Random Forest model saved with hyperparameter tuning.")
