
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import joblib
import os

BASE_PATH = os.path.dirname(__file__)

def create_sequences(data, window_size):
    return np.array([data[i:i+window_size] for i in range(len(data) - window_size)])

def predict_anomalies(df: pd.DataFrame, window_size=3):
    df_sorted = df.sort_values(["conector_id", "data_ultimo_carregamento"])
    series = df_sorted["dias_sem_uso"].values.reshape(-1, 1)

    scaler = joblib.load(os.path.join(BASE_PATH, "scaler.pkl"))
    series_scaled = scaler.transform(series)

    X = create_sequences(series_scaled, window_size)

    model = load_model(os.path.join(BASE_PATH, "model.h5"))
    threshold = joblib.load(os.path.join(BASE_PATH, "threshold.json"))

    X_pred = model.predict(X)
    mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2))

    anomaly_flags = np.zeros(len(series))
    anomaly_flags[window_size:] = (mse > threshold).astype(int)

    df_sorted["anomaly"] = anomaly_flags
    return df_sorted
