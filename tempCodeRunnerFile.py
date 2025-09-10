from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

with open('crop_model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def index():
    return render_template('crop_form.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        features = [float(request.form[key]) for key in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
        prediction = model.predict([features])[0]
        return render_template('result.html', crop=prediction)
    except:
        return render_template('error.html', message="Please enter valid numeric values.")

if __name__ == '__main__':
    app.run(debug=True)
