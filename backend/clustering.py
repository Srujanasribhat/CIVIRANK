from sklearn.cluster import KMeans


def apply_clustering(df):
    df = df.copy()

    features = [
        "Sanitation", "Water", "Education",
        "Healthcare", "Crime", "Electricity"
    ]

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(df[features])

    return df