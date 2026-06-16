import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMExplainer:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found")

        self.client = Groq(api_key=api_key)

    def build_prompt(self, kpi_summary, root_result, drops):

        drop_month = str(drops.iloc[-1]["year_month"]) if hasattr(drops, "empty") and not drops.empty else "recent period"

        return f"""
You are a senior business analyst.

Analyze the KPI drop using the given data and provide a REAL business insight.

DATA:
Month: {drop_month}

KPI Summary:
- Sales: {kpi_summary.get('latest_sales')}
- Profit: {kpi_summary.get('latest_profit')}
- Orders: {kpi_summary.get('latest_orders')}
- Margin: {kpi_summary.get('latest_margin')}
- Shipping Days: {kpi_summary.get('latest_shipping_days')}

Root Cause Analysis:
- Category: {root_result.get('category')}
- Sub-category: {root_result.get('sub_category')}
- Region: {root_result.get('region')}
- Segment: {root_result.get('segment')}

INSTRUCTIONS:
- Do NOT explain what KPI is
- Do NOT give generic definitions
- Focus ONLY on this business data
- Give specific insights

OUTPUT FORMAT:
1. Reason for KPI drop (based on data)
2. Root cause explanation (connect category, region, etc.)
3. 2-3 actionable business recommendations

Keep it concise, professional, and data-driven.
"""

    def explain(self, kpi_summary, root_result, drops):

        prompt = self.build_prompt(kpi_summary, root_result, drops)

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",   # ✅ FIXED MODEL
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )

                print("✅ RAW RESPONSE:", response)

                if response and response.choices:
                    content = response.choices[0].message.content

                    if content:
                        return content.strip()

                return "⚠️ Empty response from AI."

            except Exception as e:
                print(f"❌ Attempt {attempt+1} failed:", str(e))

                if attempt == 2:
                    raise e

                time.sleep(1)