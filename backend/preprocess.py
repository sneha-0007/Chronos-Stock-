def preprocess_data(df):
    df["close"] = df["close"].astype(float)
    df.dropna(inplace=True)
    return df
