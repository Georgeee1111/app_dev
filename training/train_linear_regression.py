import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load data
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

# Categorical and numerical columns
categorical = ['Category', 'Region', 'Weather Condition', 'Holiday/Promotion', 'Seasonality']
numerical = [col for col in features if col not in categorical]

# Preprocessing: One-hot encode categorical, scale numerical
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
    ('num', StandardScaler(), numerical)
])

# Use Ridge (regularized linear regression)
pipeline = Pipeline(steps=[
    ('preprocessing', preprocessor),
    ('regressor', Ridge())
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter tuning
param_grid = {
    'regressor__alpha': [0.01, 0.1, 1.0, 10.0, 100.0]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Print best hyperparameters
print(f"Best hyperparameters: {grid_search.best_params_}")

# Save best model
best_model = grid_search.best_estimator_
joblib.dump(best_model, 'models/linear_regression_model_with_discount.pkl')
print("✅ Ridge Regression model saved with hyperparameter tuning, including Discount.")
