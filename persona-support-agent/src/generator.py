import os
from dotenv import load_dotenv
import google.generativeai as genai

from src.prompts import (
    TECHNICAL_PROMPT,
    FRUSTRATED_PROMPT,
    EXECUTIVE_PROMPT
)
from src.rag_pipeline import retrieve_chunks

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def get_persona_prompt(persona):
    if persona == "Technical Expert":
        return TECHNICAL_PROMPT
    elif persona == "Frustrated User":
        return FRUSTRATED_PROMPT
    else:
        return EXECUTIVE_PROMPT


def fallback_response(persona, user_query, retrieved_chunks):
    context = "\n".join([chunk["text"][:300] for chunk in retrieved_chunks]) if retrieved_chunks else "No relevant documents available."

    if persona == "Technical Expert":
        return f"""
I understand you're facing a technical issue.

Based on the available documentation:

{context}

Recommended actions:
1. Verify request parameters and configuration.
2. Check logs for error traces.
3. Validate API/database integration settings.
4. Retry after applying fixes.

If the issue persists, human technical support is recommended.
"""

    elif persona == "Frustrated User":
        return f"""
I understand how frustrating this situation is, and I’m sorry for the inconvenience.

Based on the available support information:

{context}

Please try these steps:
1. Restart the application or browser.
2. Clear cache and cookies.
3. Check your internet connection.
4. Retry after a few minutes.

If the issue continues, please contact human support for immediate assistance.
"""

    else:
        return f"""
Here is a concise summary based on available support knowledge:

{context}

Business Impact:
- Operational delays may affect customer experience.
- Resolution time depends on issue severity.

Recommended action:
Escalate to support team for priority resolution and timeline estimation.
"""


def generate_response(user_query, persona_data):
    print("NEW GENERATOR RUNNING")
    persona = persona_data["persona"]

    try:
        print("RETRIEVING CHUNKS")
        retrieved_chunks = retrieve_chunks(user_query)

        context = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])

        prompt = f"""
{get_persona_prompt(persona)}

Knowledge Base Context:
{context}

User Query:
{user_query}

Rules:
- Only answer using context.
- Do not hallucinate.
- If information is missing, clearly mention human support may be required.
"""

        print("TRY BLOCK RUNNING")
        response = model.generate_content(prompt)
        response_text = response.text

    except Exception as e:
        print("EXCEPTION BLOCK HIT")
        print("ERROR:", e)

        if "retrieved_chunks" not in locals():
            retrieved_chunks = []

        response_text = fallback_response(
            persona,
            user_query,
            retrieved_chunks
        )

        print("FALLBACK RESPONSE GENERATED")

    return {
        "persona": persona,
        "confidence": persona_data["confidence"],
        "retrieved_chunks": retrieved_chunks,
        "response": response_text
    }