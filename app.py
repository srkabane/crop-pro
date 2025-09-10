from flask import Flask, render_template, request, redirect, session, url_for, flash
import pickle
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load ML model once at startup
with open('crop_model.pkl', 'rb') as f:
    model = pickle.load(f)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email_or_phone TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---

@app.route('/')
def home():
    user = session.get('user', 'Guest')
    return render_template('home.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']   # Email or Phone
        pwd = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email_or_phone = ?", (identifier,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == pwd:
            session['user'] = identifier
            return redirect('/crop-form')
        else:
            return render_template('login.html', message='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        identifier = request.form['identifier']  # Email or Phone
        pwd = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email_or_phone = ?", (identifier,))
        if cursor.fetchone():
            conn.close()
            return render_template('signup.html', message='User already exists')
        cursor.execute("INSERT INTO users (email_or_phone, password) VALUES (?, ?)", (identifier, pwd))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        identifier = request.form['identifier']  # Email or Phone
        new_pwd = request.form['new_password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email_or_phone = ?", (identifier,))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password = ? WHERE email_or_phone = ?", (new_pwd, identifier))
            conn.commit()
            conn.close()
            return redirect('/login')
        else:
            conn.close()
            return render_template('forgot_password.html', message='User does not exist')
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect('/login')

@app.route('/crop-form', methods=['GET', 'POST'])
def crop_form():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']

    if request.method == 'POST':
        try:
            # Validate inputs and convert to floats
            features = []
            for key in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
                value = request.form.get(key)
                if not value or value.strip() == '':
                    raise ValueError(f"Missing input for {key}")
                features.append(float(value))

            prediction = model.predict([features])[0]
            image_path = url_for('static', filename=f"images/{prediction.lower()}.jpg")  # ← MODIFIED HERE
            return render_template('crop_form.html', crop=prediction, image=image_path, username=username)
        except ValueError as ve:
            return render_template('crop_form.html', message=str(ve), username=username)
        except Exception as e:
            print("Prediction Error:", e)
            return render_template('crop_form.html', message="Please enter valid numeric values.", username=username)

    return render_template('crop_form.html', username=username)

PEST_DISEASE_DATA = {
    'apple': [{'name': 'Apple Scab', 'description': 'A common disease of apples.', 'image': 'apple.jpg'}, {'name': 'Codling Moth', 'description': 'A common pest of apples.', 'image': 'apple.jpg'}],
    'banana': [{'name': 'Panama Disease', 'description': 'A fungal disease that affects banana plants.', 'image': 'banana.jpg'}],
    'blackgram': [{'name': 'Yellow Mosaic Virus', 'description': 'A viral disease that affects blackgram.', 'image': 'blackgram.jpg'}],
    'chickpea': [{'name': 'Ascochyta Blight', 'description': 'A fungal disease that affects chickpeas.', 'image': 'chickpea.jpg'}],
    'coconut': [{'name': 'Root Wilt Disease', 'description': 'A disease of coconut palms.', 'image': 'coconut.jpg'}],
    'coffee': [{'name': 'Coffee Leaf Rust', 'description': 'A fungal disease that affects coffee plants.', 'image': 'coffee.jpg'}],
    'cotton': [{'name': 'Bollworm', 'description': 'A major pest of cotton.', 'image': 'cotton.jpg'}],
    'grapes': [{'name': 'Downy Mildew', 'description': 'A fungal disease that affects grapes.', 'image': 'grapes.jpg'}],
    'jute': [{'name': 'Jute Stem Weevil', 'description': 'A pest that affects jute plants.', 'image': 'jute.jpeg'}],
    'kidneybeans': [{'name': 'Bean Rust', 'description': 'A fungal disease that affects kidney beans.', 'image': 'kidneybeans.jpg'}],
    'lentil': [{'name': 'Lentil Rust', 'description': 'A fungal disease that affects lentils.', 'image': 'lentil.jpg'}],
    'maize': [{'name': 'Maize Stalk Borer', 'description': 'A pest that affects maize plants.', 'image': 'maize.jpg'}],
    'mango': [{'name': 'Anthracnose', 'description': 'A fungal disease that affects mangoes.', 'image': 'mango.jpeg'}],
    'mothbeans': [{'name': 'Yellow Mosaic Virus', 'description': 'A viral disease that affects mothbeans.', 'image': 'mothbeans.jpg'}],
    'mungbean': [{'name': 'Yellow Mosaic Virus', 'description': 'A viral disease that affects mungbeans.', 'image': 'mungbean.jpg'}],
    'muskmelon': [{'name': 'Powdery Mildew', 'description': 'A fungal disease that affects muskmelons.', 'image': 'muskmelon.jpg'}],
    'orange': [{'name': 'Citrus Canker', 'description': 'A bacterial disease that affects oranges.', 'image': 'orange.jpg'}],
    'papaya': [{'name': 'Papaya Ringspot Virus', 'description': 'A viral disease that affects papaya plants.', 'image': 'papaya.jpeg'}],
    'pigeonpeas': [{'name': 'Pod Borer', 'description': 'A pest that affects pigeonpeas.', 'image': 'pigeonpeas.jpeg'}],
    'pomegranate': [{'name': 'Bacterial Blight', 'description': 'A bacterial disease that affects pomegranates.', 'image': 'pomegranate.jpg'}],
    'rice': [{'name': 'Rice Blast', 'description': 'A fungal disease that affects rice plants.', 'image': 'rice.jpg'}],
    'watermelon': [{'name': 'Anthracnose', 'description': 'A fungal disease that affects watermelons.', 'image': 'watermelon.jpeg'}],
}

@app.route('/pest-disease', methods=['GET', 'POST'])
def pest_disease():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    if request.method == 'POST':
        crop = request.form.get('crop')
        if not crop:
            return render_template('pest_disease.html', message="Please select a crop.", username=username)

        pest_data = PEST_DISEASE_DATA.get(crop.lower(), [])

        if not pest_data:
            return render_template('pest_disease.html', message=f"No pest/disease information found for {crop}.", username=username, crop=crop)

        results = []
        for item in pest_data:
            results.append({
                'name': item['name'],
                'description': item['description'],
                'image': url_for('static', filename=f"images/{item['image']}")
            })

        return render_template('pest_disease.html', pests_diseases=results, crop=crop, username=username)

    return render_template('pest_disease.html', username=username)

def analyze_soil(n, p, k, ph, organic_matter):
    recommendations = []

    # Simple rule-based analysis
    if not (50 <= n <= 150):
        recommendations.append("Adjust Nitrogen levels to be between 50-150 kg/ha.")
    if not (20 <= p <= 50):
        recommendations.append("Adjust Phosphorus levels to be between 20-50 kg/ha.")
    if not (30 <= k <= 100):
        recommendations.append("Adjust Potassium levels to be between 30-100 kg/ha.")
    if not (6.0 <= ph <= 7.5):
        recommendations.append("Adjust pH to be between 6.0 and 7.5 for optimal nutrient availability.")
    if not (2.0 <= organic_matter <= 5.0):
        recommendations.append("Improve soil organic matter to be between 2-5%.")

    if not recommendations:
        health = "Good"
        recommendations.append("Your soil is in good condition.")
    else:
        health = "Needs Improvement"

    return {"health": health, "recommendations": recommendations}

@app.route('/soil-health', methods=['GET', 'POST'])
def soil_health():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    if request.method == 'POST':
        try:
            n = float(request.form['N'])
            p = float(request.form['P'])
            k = float(request.form['K'])
            ph = float(request.form['ph'])
            organic_matter = float(request.form['organic_matter'])

            result = analyze_soil(n, p, k, ph, organic_matter)
            return render_template('soil_health.html', result=result, username=username)
        except ValueError:
            return render_template('soil_health.html', message="Please enter valid numeric values.", username=username)
        except Exception as e:
            print("Analysis Error:", e)
            return render_template('soil_health.html', message="An error occurred during analysis.", username=username)

    return render_template('soil_health.html', username=username)

@app.route('/weather-prediction', methods=['GET', 'POST'])
def weather_prediction():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    if request.method == 'POST':
        try:
            N = float(request.form['N'])
            P = float(request.form['P'])
            K = float(request.form['K'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])

            features = [N, P, K, temperature, humidity, ph, rainfall]

            prediction = model.predict([features])[0]
            image_path = url_for('static', filename=f"images/{prediction.lower()}.jpg")
            return render_template('weather_prediction.html', crop=prediction, image=image_path, username=username)
        except ValueError:
            return render_template('weather_prediction.html', message="Please enter valid numeric values.", username=username)
        except Exception as e:
            print("Prediction Error:", e)
            return render_template('weather_prediction.html', message="An error occurred during prediction.", username=username)

    return render_template('weather_prediction.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
