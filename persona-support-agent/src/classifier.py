import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def classify_persona(user_message: str) -> dict:
    query = user_message.lower()

    # Rule-based classification first
    technical_keywords = [
        "api", "token", "header", "auth",
        "database", "integration", "logs",
        "http", "debug", "internal errors"
    ]

    business_keywords = [
        "uptime", "operational", "timeline",
        "business", "roi", "revenue", "impact"
    ]

    frustrated_keywords = [
        "frustrated", "angry", "terrible",
        "nothing is loading", "hour", "refund",
        "duplicate charges", "demand", "immediate"
    ]

    tech_score = sum(1 for word in technical_keywords if word in query)
    business_score = sum(1 for word in business_keywords if word in query)
    frustrated_score = sum(1 for word in frustrated_keywords if word in query)

    # Strong rule-based classification
    if tech_score >= max(business_score, frustrated_score) and tech_score > 0:
        return {
            "persona": "Technical Expert",
            "confidence": 0.95,
            "reasoning": "Detected technical terminology."
        }

    if business_score >= max(tech_score, frustrated_score) and business_score > 0:
        return {
            "persona": "Business Executive",
            "confidence": 0.95,
            "reasoning": "Detected business-oriented language."
        }

    if frustrated_score > 0:
        return {
            "persona": "Frustrated User",
            "confidence": 0.95,
            "reasoning": "Detected emotional/frustration signals."
        }

    # Gemini fallback for ambiguous cases
    prompt = f"""
Classify the user message into exactly one:
- Technical Expert
- Frustrated User
- Business Executive

Return JSON:
{{
 "persona": "...",
 "confidence": 0.9,
 "reasoning": "..."
}}

Message: {user_message}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    except Exception as e:
        print("Classifier Error:", e)
        return {
            "persona": "Frustrated User",
            "confidence": 0.5,
            "reasoning": "Fallback classification due to API error."
        }