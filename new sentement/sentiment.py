import os
import pickle

# Get absolute path of current file (important for Streamlit Cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define file paths
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

# Load model and vectorizer safely
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

try:
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Vectorizer file not found at {VECTORIZER_PATH}")


# Prediction function
def analyze_sentiment(text):
    if not text or not isinstance(text, str):
        return "Invalid input"

    # Transform text using vectorizer
    text_vector = vectorizer.transform([text])

    # Predict sentiment
    prediction = model.predict(text_vector)[0]

    # Convert prediction to readable output
    if prediction == 1:
        return "Positive 😊"
    elif prediction == 0:
        return "Negative 😞"
    else:
        return "Neutral 😐"
