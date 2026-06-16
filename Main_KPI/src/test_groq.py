from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """
You are a senior business analyst.

Month: March 2024

KPI Summary:
- Sales: 45000
- Profit: 5000
- Orders: 120
- Margin: 12
- Shipping Days: 6

Root Cause:
- Category: Technology
- Sub-category: Phones
- Region: South
- Segment: Consumer

Give:
1. Reason for KPI drop
2. Root cause explanation
3. 2 actions

Do NOT explain what KPI is.
Be specific and business-focused.
"""

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

print(response.choices[0].message.content)