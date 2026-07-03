import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def load_data(file):
    if file is not None:
        df = pd.read_csv(file)
    else:
        df = pd.read_csv("data/sample_slum_data.csv")
    return df


def clean_data(df):
    df = df.copy()

    numeric_cols = [
        "Population", "Sanitation", "Water", "Education",
        "Healthcare", "Crime", "Electricity"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    df["Area"] = df["Area"].fillna("Unknown Area")

    return df


def normalize_data(df):
    df = df.copy()

    features = [
        "Sanitation", "Water", "Education",
        "Healthcare", "Crime", "Electricity"
    ]

    scaler = MinMaxScaler()
    df[features] = scaler.fit_transform(df[features])

    return df