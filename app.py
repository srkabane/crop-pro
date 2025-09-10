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

@app.route('/pest-disease')
def pest_disease():
    if 'user' not in session:
        return redirect('/login')
    return render_template('pest_disease.html')

@app.route('/soil-health')
def soil_health():
    if 'user' not in session:
        return redirect('/login')
    return render_template('soil_health.html')

@app.route('/weather-prediction')
def weather_prediction():
    if 'user' not in session:
        return redirect('/login')
    return render_template('weather_prediction.html')

if __name__ == '__main__':
    app.run(debug=True)
