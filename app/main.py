from flask import Flask, request, jsonify
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import json

app = Flask(__name__)

MODEL_PATH = "./model.pkl"
model = joblib.load(MODEL_PATH)


# Function to handle the POST request and make predictions
def handle_post_request(request_data):
    data = pd.DataFrame([request_data])

    label_encoder = LabelEncoder()

    for column in data.columns:
        if data[column].dtype == 'object':
            data[column] = data[column].str.replace(',', '.').astype(float, errors='ignore')
            data[column] = label_encoder.fit_transform(data[column])

    X_input = data.drop(columns=["Status"], errors='ignore')
    prediction = model.predict(X_input)

    prediction_labels = {0: "Dead", 1: "Alive"}
    prediction_label = prediction[0]

    result = {
        "prediction": prediction_labels.get(prediction_label, "Unknown")
    }

    return result


@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()
        result = handle_post_request(input_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
