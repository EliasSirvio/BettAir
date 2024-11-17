def get_recommendations(risk_category):
    """
    Provides recommendations based on the risk category.

    Parameters:
    - risk_category (str): The risk level ("Low", "Medium", "High")

    Returns:
    - recommendations (list): A list of recommendations.
    """
    if risk_category == "Low":
        return [
            "Maintain current environmental practices.",
            "Promote green spaces to sustain the low risk level."
        ]
    elif risk_category == "Medium":
        return [
            "Increase urban green spaces (parks, trees).",
            "Implement policies to reduce air pollution sources.",
            "Encourage green roofs and vertical gardens."
        ]
    elif risk_category == "High":
        return [
            "Urgent need to expand vegetation cover.",
            "Reduce building density where possible.",
            "Implement strict air pollution control measures.",
            "Encourage use of public transportation."
        ]
    else:
        return ["No recommendations available."]
