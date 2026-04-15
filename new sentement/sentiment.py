import pickle

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

def analyze_sentiment(text):
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]

    if prediction == 1:
        return "Good 😊"
    elif prediction == 0:
        return "Bad 😠"
    else:
        return "Neutral 😐"