def generate_recommendation(row):
    recommendations = []

    if row["Sanitation"] < 0.4:
        recommendations.append("prioritize public toilets, drainage improvement, and waste disposal")

    if row["Water"] < 0.4:
        recommendations.append("increase access to clean drinking water and repair water supply lines")

    if row["Education"] < 0.4:
        recommendations.append("improve school access, learning support, and awareness programs")

    if row["Healthcare"] < 0.4:
        recommendations.append("set up health camps, clinics, and emergency medical support")

    if row["Crime"] > 0.6:
        recommendations.append("improve street lighting, community safety, and police patrolling")

    if row["Electricity"] < 0.4:
        recommendations.append("improve electricity connections and install solar street lights")

    if len(recommendations) == 0:
        return "This area is relatively stable. Continue regular monitoring and maintenance."

    if row["Priority_Score"] >= 70:
        priority = "Immediate action required"
    elif row["Priority_Score"] >= 40:
        priority = "Moderate development attention required"
    else:
        priority = "Low priority improvement recommended"

    return priority + ": " + "; ".join(recommendations) + "."