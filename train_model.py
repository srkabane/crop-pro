import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv('crop_recommendation.csv')

# Features and labels
X = df.drop('label', axis=1)
y = df['label']

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
with open('crop_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as crop_model.pkl")
