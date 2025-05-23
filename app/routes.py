from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app import mysql  
from app.model import load_model, predict_price
import pandas as pd

main = Blueprint('main', __name__)
model = load_model()

@main.route('/', methods=['GET'])
def landing():
    return render_template('landing.html')

@main.route('/home', methods=['GET'])
def home():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('auth.login'))

    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        username = user[0] if user else 'User'

        cursor.execute("""
            SELECT category, region, inventory_level, units_sold, predicted_price, prediction_time
            FROM pricing_predictions
            ORDER BY id DESC
            LIMIT 5
        """)
        recent_predictions = cursor.fetchall()
        cursor.close()
    except Exception as e:
        flash(f"Failed to fetch data: {e}", "danger")
        username = 'User'
        recent_predictions = []

    return render_template('home.html', username=username, prediction=None, recent_predictions=recent_predictions)


@main.route('/analytics')
def analytics():
    if 'user_id' not in session:
        flash('Please log in to view analytics.', 'warning')
        return redirect(url_for('auth.login'))

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        username = user[0] if user else 'User'

        cursor.execute("SELECT COUNT(*) FROM pricing_predictions")
        total_predictions = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(predicted_price) FROM pricing_predictions")
        average_price = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM pricing_predictions
            GROUP BY category
            ORDER BY count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        top_category = result[0] if result else "N/A"

        cursor.execute("""
            SELECT region, COUNT(*) 
            FROM pricing_predictions 
            GROUP BY region
        """)
        region_data = cursor.fetchall()
        region_labels = [row[0] for row in region_data]
        region_counts = [row[1] for row in region_data]

        cursor.execute("""
            SELECT category, COUNT(*)
            FROM pricing_predictions
            GROUP BY category
        """)
        category_data = cursor.fetchall()
        category_labels = [row[0] for row in category_data]
        category_counts = [row[1] for row in category_data]

        cursor.close()

        return render_template(
            'analytics.html',
            username=username,
            total_predictions=total_predictions,
            average_price=average_price,
            top_category=top_category,
            region_labels=region_labels,
            region_counts=region_counts,
            category_labels=category_labels,
            category_counts=category_counts
        )
    except Exception as e:
        print("Error in analytics route:", e)  
        flash(f"Error loading analytics: {e}", "danger")
        return redirect(url_for('main.home'))

@main.route('/home/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

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

        return jsonify({'predicted_price': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main.route('/home/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

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

        return jsonify({'predicted_price': prediction, 'message': 'Saved successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
