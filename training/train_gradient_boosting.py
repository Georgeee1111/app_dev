import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load dataset
df = pd.read_csv('data/retail_store_inventory.csv')

# Extract 3 rows (e.g., the first 3) for later prediction
prediction_samples = df.iloc[:3].copy()

# Remove those 3 rows from the dataset so they are not used in training/testing
df = df.drop(index=prediction_samples.index)

# Features and target
features = [
    'Category', 'Region', 'Inventory Level', 'Units Sold', 'Units Ordered',
    'Demand Forecast', 'Competitor Pricing', 'Weather Condition',
    'Holiday/Promotion', 'Seasonality', 'Discount'  # Added 'Discount' feature
]
target = 'Price'

X = df[features]
y = df[target]

# Define categorical and numerical columns
categorical = ['Category', 'Region', 'Weather Condition', 'Holiday/Promotion', 'Seasonality']
numerical = [col for col in features if col not in categorical]

# Preprocessing: OneHotEncode categorical features and scale numerical features
numerical_transformer = StandardScaler()
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
    ('num', numerical_transformer, numerical)
])

# Create pipeline with GradientBoostingRegressor
model = Pipeline(steps=[
    ('preprocessing', preprocessor),
    ('regressor', GradientBoostingRegressor(random_state=42))
])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter tuning using GridSearchCV
param_grid = {
    'regressor__n_estimators': [100, 200],
    'regressor__learning_rate': [0.05, 0.1],
    'regressor__max_depth': [3, 5],
    'regressor__min_samples_split': [2, 5],
    'regressor__min_samples_leaf': [1, 2]
}

grid_search = GridSearchCV(model, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Print best hyperparameters
print(f"Best hyperparameters: {grid_search.best_params_}")

# Save the best model (after hyperparameter tuning)
best_model = grid_search.best_estimator_
joblib.dump(best_model, 'models/gradient_boosting_model_with_discount.pkl')

print("✅ Gradient Boosting model saved with hyperparameter tuning, including Discount feature.")
