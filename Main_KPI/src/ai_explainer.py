#Template-Based Natural Language Generation algorithm, 
#supported by rule-based classification and random sentence selection

#If API fails (network, quota, error)

import random

class AIExplainer:

    def __init__(self):
        pass

    def explain_drop(self, kpi_summary, root_result, drops):

        # ✅ Safe extraction
        drop_month = str(drops.iloc[-1]["year_month"]) if hasattr(drops, "empty") and not drops.empty else "recent period"
        category = root_result.get("category", "overall performance")
        sub_category = root_result.get("sub_category", "")
        region = root_result.get("region", "key regions")
        segment = root_result.get("segment", "customer segment")

        # ✅ Detect change magnitude
        change_text = ""
        if isinstance(kpi_summary, dict):
            change = kpi_summary.get("change")
            if change:
                try:
                    val = float(str(change).replace("%", ""))
                    if val < -20:
                        change_text = "a sharp decline"
                    elif val < -10:
                        change_text = "a noticeable drop"
                    elif val < 0:
                        change_text = "a slight decrease"
                except:
                    change_text = "a decline"

        if not change_text:
            change_text = "a decline"

        # ✅ Sentence variations
        openings = [
            f"In {drop_month}, the KPI recorded {change_text}",
            f"The KPI showed {change_text} during {drop_month}",
            f"A performance dip was observed in {drop_month}",
            f"{drop_month} saw a downturn in KPI performance"
        ]

        category_phrases = [
            f"primarily driven by the {category} category",
            f"largely influenced by performance in {category}",
            f"with major impact coming from {category}",
            f"mainly due to issues in {category}"
        ]

        subcategory_phrases = [
            f", especially within {sub_category}",
            f", particularly in {sub_category}",
            f", with notable weakness in {sub_category}",
            ""
        ]

        region_phrases = [
            f"across {region}",
            f"in the {region} region",
            f"particularly impacting {region}",
            f"with strong effects seen in {region}"
        ]

        reasons = [
            "reduced customer demand",
            "lower engagement levels",
            "operational inefficiencies",
            "market slowdown",
            "seasonal fluctuations",
            "increased competition"
        ]

        impact_phrases = [
            f"affecting the {segment} segment",
            f"impacting {segment} customers",
            f"within the {segment} business segment",
            f"across {segment} operations"
        ]

        actions = [
            "focus on improving customer engagement strategies",
            "optimize operational efficiency",
            "analyze customer behavior for insights",
            "revisit pricing and promotional strategies",
            "strengthen marketing efforts in weak areas",
            "monitor performance closely and take corrective actions"
        ]

        endings = [
            "to stabilize and improve future performance.",
            "to recover and drive growth.",
            "to prevent further decline and regain momentum.",
            "to enhance overall business outcomes."
        ]

        # ✅ Build explanation dynamically
        explanation = random.choice(openings) + " "

        explanation += random.choice(category_phrases)

        if sub_category and sub_category != "unknown":
            explanation += random.choice(subcategory_phrases)

        explanation += " " + random.choice(region_phrases) + ". "

        explanation += f"This trend is likely due to {random.choice(reasons)}, "

        explanation += random.choice(impact_phrases) + ". "

        explanation += f"The business should {random.choice(actions)} "

        explanation += random.choice(endings)

        return explanation.strip()