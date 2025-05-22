import joblib

def load_model():
    # Load the trained model pipeline (model + transformation)
    model_pipeline = joblib.load('models/price_predictor.pkl')
    return model_pipeline

def predict_price(model_pipeline, input_data):
    # Make prediction using the model pipeline
    prediction = model_pipeline.predict(input_data)[0]
    return round(prediction, 2)