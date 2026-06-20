import streamlit as st

from src.classifier import classify_persona
from src.generator import generate_response
from src.escalator import check_escalation, generate_handoff_summary

# Page Configuration
st.set_page_config(
    page_title="Persona Support Agent",
    page_icon="🤖",
    layout="wide"
)

# Sidebar
st.sidebar.title("Persona Support Agent")
st.sidebar.markdown("---")

st.sidebar.markdown("## Product Overview")
st.sidebar.write(
    "AI-powered customer support system with persona-aware responses, "
    "knowledge retrieval, and escalation workflows."
)

st.sidebar.markdown("---")

st.sidebar.markdown("## Core Features")
st.sidebar.markdown("""
- Persona Detection  
- Knowledge Retrieval (RAG)  
- Adaptive Responses  
- Escalation Logic  
- Human Handoff Summary  
""")

st.sidebar.markdown("---")

st.sidebar.markdown("## Supported Personas")
st.sidebar.markdown("""
**Technical Expert**  
Detailed technical responses  

**Frustrated User**  
Empathetic and simple responses  

**Business Executive**  
Concise business-focused responses  
""")

st.sidebar.markdown("---")

with st.sidebar.expander("Example Queries"):
    st.write("API authentication failure with error logs")
    st.write("I am frustrated with login issues")
    st.write("How will this impact business operations?")
    st.write("I need refund for duplicate payment")

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Gemini + ChromaDB + Streamlit")

# Main UI
st.title("🤖 AI Persona-Adaptive Customer Support Agent")
st.caption("Delivering personalized customer support through AI")

query = st.text_area(
    "Enter your support query",
    height=150,
    placeholder="Describe your issue here..."
)

submit = st.button("Submit Query", use_container_width=True)

if submit and query:
    try:
        with st.spinner("Analyzing query and generating response..."):

            # Persona Detection (Run only once)
            persona_data = classify_persona(query)

            # Response Generation
            result = generate_response(query, persona_data)

            persona = result["persona"]
            confidence = result["confidence"]
            retrieved_docs = result["retrieved_chunks"]
            response = result["response"]

            # Escalation Logic
            escalated, reason = check_escalation(
                query,
                persona_data,
                retrieved_docs
            )

        st.markdown("---")

        # Persona + Escalation
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Detected Persona")
            st.success(persona)
            st.caption(f"Confidence Score: {confidence}")
            st.caption(f"Reasoning: {persona_data['reasoning']}")

        with col2:
            st.subheader("Escalation Status")
            if escalated:
                st.error(f"Escalated to Human Support")
                st.caption(f"Reason: {reason}")
            else:
                st.success("No Escalation Required")

        st.markdown("---")

        # Retrieved Sources
        st.subheader("Retrieved Sources")
        if retrieved_docs:
            unique_sources = list(set([doc["source"] for doc in retrieved_docs]))
            for source in unique_sources:
                st.write(f"• {source}")
        else:
            st.warning("No relevant documents found.")

        st.markdown("---")

        # Response
        st.subheader("AI Response")
        st.markdown(response)

        # Human Handoff Summary
        if escalated:
            st.markdown("---")
            st.subheader("Human Handoff Summary")

            summary = generate_handoff_summary(
                query,
                persona_data,
                retrieved_docs
            )

            st.json(summary)

    except Exception as e:
        st.error(f"Application Error: {str(e)}")

st.markdown("---")
st.caption("© 2026 Persona Support Agent")