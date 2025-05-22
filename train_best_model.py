import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from prettytable import PrettyTable

# Load dataset
df = pd.read_csv('data/retail_store_inventory.csv')

# Feature and target columns
features = [
    'Category', 'Region', 'Inventory Level', 'Units Sold', 'Units Ordered',
    'Demand Forecast', 'Competitor Pricing', 'Weather Condition',
    'Holiday/Promotion', 'Seasonality', 'Discount'
]
target = 'Price'

X = df[features]
y = df[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load models
models = {
    "Linear Regression": joblib.load('models/linear_regression_model_with_discount.pkl'),
    "Random Forest": joblib.load('models/random_forest_model.pkl'),
    "Gradient Boosting": joblib.load('models/gradient_boosting_model_with_discount.pkl')
}

# Initialize table
table = PrettyTable()
table.field_names = ["Model", "RMSE", "MAE", "R²"]

# Function to evaluate model
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    
    # Regression metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return rmse, mae, r2

# Evaluate all models
performance = {}
for name, model in models.items():
    rmse, mae, r2 = evaluate_model(model, X_test, y_test)
    
    performance[name] = {
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
    }

    # Add to table
    table.add_row([
        name, 
        f"{rmse:.4f}", 
        f"{mae:.4f}", 
        f"{r2:.4f}"
    ])

# Print table
print(table)

# Save best model (based on lowest RMSE)
best_model_name = min(performance, key=lambda x: performance[x]['RMSE'])
best_model = models[best_model_name]
joblib.dump(best_model, 'models/price_predictor.pkl')
print(f"\n✅ Best model: {best_model_name} saved as 'models/price_predictor.pkl'")
