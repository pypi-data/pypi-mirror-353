
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os
import json

# Carregar modelo treinado e artefatos
dir_path = os.path.dirname(__file__)
model = load_model(os.path.join(dir_path, "model.h5"), compile=False)
scaler = joblib.load(os.path.join(dir_path, "scaler.pkl"))
with open(os.path.join(dir_path, "threshold.json"), "r") as f:
    #threshold = float(f.read())    
    threshold = json.load(f)["threshold"]

def create_sequences(data, window_size):
    return np.array([data[i:i+window_size] for i in range(len(data) - window_size)])

def predict_anomalies(df):
    df_sorted = df.sort_values(["conector_id", "data_ultimo_carregamento"])
    series = df_sorted["dias_sem_uso"].values.reshape(-1, 1)
    series_scaled = scaler.transform(series)
    window_size = 3
    X = create_sequences(series_scaled, window_size)
    X_pred = model.predict(X)
    mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2))
    anomalies = mse > threshold

    # Preencher resultados no DataFrame original
    result_df = df_sorted.copy()
    result_df = result_df.iloc[window_size:].copy()
    result_df["reconstruction_error"] = mse
    result_df["is_anomaly"] = anomalies.astype(int)
    return result_df
