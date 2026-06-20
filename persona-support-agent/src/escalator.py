def check_escalation(query, persona_data, retrieved_docs):
    query_lower = query.lower()

    sensitive_keywords = [
        "refund",
        "duplicate charge",
        "duplicate charges",
        "billing",
        "payment dispute",
        "chargeback",
        "legal",
        "lawsuit",
        "account access",
        "account locked"
    ]

    for keyword in sensitive_keywords:
        if keyword in query_lower:
            return True, f"Sensitive issue detected: {keyword}"

    if not retrieved_docs:
        return True, "No relevant documents found."

    if persona_data["confidence"] < 0.65:
        return True, "Low confidence classification."

    return False, "No escalation needed."

def generate_handoff_summary(query, persona_data, retrieved_docs):
    documents_used = list(set([doc["source"] for doc in retrieved_docs]))

    summary = {
        "persona": persona_data["persona"],
        "confidence": persona_data["confidence"],
        "issue": query,
        "documents_used": documents_used,
        "attempted_steps": [
            "Knowledge base retrieval",
            "AI response generation"
        ],
        "recommendation": "Human support needed"
    }

    return summary


if __name__ == "__main__":
    sample_persona = {
        "persona": "Frustrated User",
        "confidence": 0.9
    }

    sample_docs = [{"source": "billing_policy.txt"}]

    escalated, reason = check_escalation(
        "I need refund for duplicate payment",
        sample_persona,
        sample_docs
    )

    print("Escalated:", escalated)
    print("Reason:", reason)

    if escalated:
        summary = generate_handoff_summary(
            "I need refund for duplicate payment",
            sample_persona,
            sample_docs
        )
        print(summary)