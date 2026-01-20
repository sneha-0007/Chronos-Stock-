import numpy as np

def predict_prices(df):
    closes = df["Close"].values

    predicted = np.roll(closes, -1)
    predicted[-1] = closes[-1]

    return {
        "actual": closes.tolist(),
        "predicted": predicted.tolist(),
        "timestamps": df["Datetime"].astype(str).tolist()
    }
