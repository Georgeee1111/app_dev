from flask import Blueprint, render_template, request
from app import mysql  
from app.model import load_model, predict_price
from flask import session, redirect, url_for, flash
import pandas as pd

main = Blueprint('main', __name__)

model = load_model()

@main.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')

@main.route('/home', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('auth.login'))
    prediction = None
    if request.method == 'POST':
        try:
            input_data = {
                'Category': request.form['category'],
                'Region': request.form['region'],
                'Inventory Level': float(request.form['inventory']),
                'Units Sold': float(request.form['units_sold']),
                'Units Ordered': float(request.form['units_ordered']),
                'Demand Forecast': float(request.form['demand']),
                'Competitor Pricing': float(request.form['competition']),
                'Weather Condition': request.form['weather'],
                'Holiday/Promotion': request.form['holiday'],
                'Seasonality': request.form['seasonality'],
                'Discount': float(request.form['discount'])  
            }

            input_df = pd.DataFrame([input_data])
            prediction = predict_price(model, input_df)

            cursor = mysql.connection.cursor()
            insert_query = """
                INSERT INTO pricing_predictions (
                    category, region, inventory_level, units_sold, units_ordered,
                    demand_forecast, competitor_pricing, weather_condition,
                    holiday_promotion, seasonality, discount, predicted_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                input_data['Category'],
                input_data['Region'],
                input_data['Inventory Level'],
                input_data['Units Sold'],
                input_data['Units Ordered'],
                input_data['Demand Forecast'],
                input_data['Competitor Pricing'],
                input_data['Weather Condition'],
                input_data['Holiday/Promotion'],
                input_data['Seasonality'],
                input_data['Discount'],
                prediction
            ))
            mysql.connection.commit()
            cursor.close()

        except Exception as e:
            prediction = f"Error: {e}"

    return render_template('home.html', prediction=prediction)
