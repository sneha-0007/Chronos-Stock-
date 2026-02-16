import pandas as pd


def preprocess_data(df):
    """
    Clean and prepare data for quant model.
    """

    if df is None or df.empty:
        return None

    df = df.sort_values(by="Date")
    df = df.drop_duplicates()

    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df = df.dropna()
    df = df.reset_index(drop=True)

    if len(df) < 20:
        return None

    return df
