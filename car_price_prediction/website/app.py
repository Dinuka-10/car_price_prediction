from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

print("Loading model and columns...")
with open("model.pkl", "rb") as file:
    model = pickle.load(file)

with open("x_train_columns.pkl", "rb") as file:
    training_columns = pickle.load(file)
print("Model and columns loaded successfully!")

def create_feature_dict(km_driven, mileage, engine, max_power, seats, car_age, 
                       fuel, seller_type, transmission, owner, brand, model_name):
    """Convert input features to one-hot encoded dictionary"""
    
    feature_dict = {
        'km_driven': float(km_driven),
        'mileage(km/ltr/kg)': float(mileage),
        'engine': float(engine),
        'max_power': float(max_power),
        'seats': float(seats),
        'car_age': int(car_age),
    }
    
    feature_dict['fuel_Diesel'] = 1 if fuel == 'Diesel' else 0
    feature_dict['fuel_Petrol'] = 1 if fuel == 'Petrol' else 0
    
    feature_dict['seller_type_Individual'] = 1 if seller_type == 'Individual' else 0
    
    feature_dict['transmission_Manual'] = 1 if transmission == 'Manual' else 0
    
    owners = ['First Owner', 'Second Owner', 'Third Owner', 'Test Drive Car']
    for owner_type in owners:
        feature_dict[f'owner_{owner_type}'] = 1 if owner == owner_type else 0
    
    brands = ['Maruti', 'Hyundai', 'Mahindra', 'Tata', 'Toyota', 'Honda', 'Ford', 
              'Chevrolet', 'Renault', 'Volkswagen', 'BMW', 'Skoda', 'Nissan', 
              'Jaguar', 'Volvo', 'Datsun', 'Mercedes-Benz', 'Fiat', 'Audi', 
              'Lexus', 'Other', 'Jeep', 'Mitsubishi']
    
    for brand_item in brands:
        feature_dict[f'brand_{brand_item}'] = 1 if brand == brand_item else 0
    
    models = ['Swift', 'Alto', 'Other', 'i20', 'Wagon', 'Innova', 'Bolero', 'Verna',
              'Grand', 'City', 'Scorpio', 'Figo', 'Indica', 'Ertiga', 'XUV500',
              'Indigo', 'i10', 'Santro', 'EON', 'Baleno', 'Etios', 'KWID', 'Amaze',
              '800', 'Creta', 'Vitara', 'Xcent', 'EcoSport', 'Ritz', 'Polo', 'Duster',
              'Jazz', 'Tiago', 'Ciaz', 'Rapid', 'Beat', 'Safari', 'Zen', 'Celerio',
              'X4', 'Vento', 'Fiesta', 'TUV', 'Manza', 'Eeco', 'New', 'Omni', 'Xylo',
              'SX4', 'Fortuner', 'KUV', 'Zest', 'Spark', 'XF', 'GO', 'Nexon', 
              'Corolla', 'Camry', 'ES', 'Sumo', 'Accent', 'XC40', 'Elite', 'XE', 
              'V40', 'Sail', 'Ameo', 'Tigor', 'Sunny', 'Ignis', 'Micra', 'Brio',
              'Ecosport', 'RediGO', 'Tavera', 'Compass', 'Terrano', 'Thar', 'Nano',
              'Enjoy', 'WR-V', 'Verito', 'Hexa', 'Endeavour', '3', 'S-Cross', 
              'Grande', 'A-Star', 'Cruze', 'Octavia', 'Civic', '5', 'E-Class',
              'Freestyle', 'Mobilio', 'Linea', 'Elantra', 'Getz', 'Lodgy', 'Marazzo',
              'Jetta', 'Aspire', 'Esteem', 'CR-V', 'Optra', 'X1', 'Fabia', 'Q5',
              'XUV300', 'Ikon']
    
    for model_item in models:
        feature_dict[f'model_{model_item}'] = 1 if model_name == model_item else 0
    
    return feature_dict

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request"""
    try:
        data = request.json
        
        km_driven = data.get('km_driven')
        mileage = data.get('mileage')
        engine = data.get('engine')
        max_power = data.get('max_power')
        seats = data.get('seats')
        car_age = data.get('car_age')
        fuel = data.get('fuel')
        seller_type = data.get('seller_type')
        transmission = data.get('transmission')
        owner = data.get('owner')
        brand = data.get('brand')
        model_name = data.get('model')
        
        if not all([km_driven, mileage, engine, max_power, car_age, brand, model_name]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        feature_dict = create_feature_dict(
            km_driven, mileage, engine, max_power, seats, car_age,
            fuel, seller_type, transmission, owner, brand, model_name
        )
        
        input_df = pd.DataFrame([feature_dict])
        
        for col in training_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        input_df = input_df[training_columns]
        
        prediction = model.predict(input_df)[0]
        
        return jsonify({
            'success': True,
            'predicted_price': float(prediction),
            'formatted_price': f"Rs.{prediction:,.2f}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/brands', methods=['GET'])
def get_brands():
    """Return list of available brands"""
    brands = ['Maruti', 'Hyundai', 'Mahindra', 'Tata', 'Toyota', 'Honda', 'Ford', 
              'Chevrolet', 'Renault', 'Volkswagen', 'BMW', 'Skoda', 'Nissan', 
              'Jaguar', 'Volvo', 'Datsun', 'Mercedes-Benz', 'Fiat', 'Audi', 
              'Lexus', 'Other', 'Jeep', 'Mitsubishi']
    return jsonify({'brands': sorted(brands)})

@app.route('/models', methods=['GET'])
def get_models():
    """Return list of available models"""
    models = ['Swift', 'Alto', 'i20', 'Wagon', 'Innova', 'Bolero', 'Verna',
              'Grand', 'City', 'Scorpio', 'Figo', 'Indica', 'Ertiga', 'XUV500',
              'Indigo', 'i10', 'Santro', 'EON', 'Baleno', 'Etios', 'KWID', 'Amaze',
              '800', 'Creta', 'Vitara', 'Xcent', 'EcoSport', 'Ritz', 'Polo', 'Duster',
              'Jazz', 'Tiago', 'Ciaz', 'Rapid', 'Other']
    return jsonify({'models': sorted(models)})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)