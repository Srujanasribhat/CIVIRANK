def calculate_priority_index(df):
    df = df.copy()

    df["Priority_Score"] = (
        (1 - df["Sanitation"]) * 0.25 +
        (1 - df["Water"]) * 0.20 +
        (1 - df["Education"]) * 0.15 +
        (1 - df["Healthcare"]) * 0.20 +
        df["Crime"] * 0.10 +
        (1 - df["Electricity"]) * 0.10
    ) * 100

    df["Priority_Score"] = df["Priority_Score"].round(2)

    df["Rank"] = df["Priority_Score"].rank(
        ascending=False,
        method="dense"
    ).astype(int)

    def risk_level(score):
        if score >= 70:
            return "High Risk"
        elif score >= 40:
            return "Medium Risk"
        else:
            return "Low Risk"

    df["Risk_Level"] = df["Priority_Score"].apply(risk_level)

    return df.sort_values(by="Priority_Score", ascending=False)