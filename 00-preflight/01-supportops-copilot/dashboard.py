import json
import streamlit as st
from extract import analyze_ticket
from prompts import DETAILED_PROMPT

st.set_page_config(
    page_title="SupportOps Copilot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SupportOps Copilot")

st.write(
    "Analyze customer support tickets using an LLM."
)

st.divider()

ticket = st.text_area(
    "Paste Customer Ticket",
    height=220
)

if st.button("Analyze Ticket"):

    if ticket.strip() == "":
        st.warning("Please enter a ticket.")
        st.stop()

    with st.spinner("Analyzing..."):

        result = analyze_ticket(
            DETAILED_PROMPT,
            ticket
        )

    if result is None:

        st.error("Analysis failed.")

    else:

        st.success("Analysis Complete")

        st.subheader("Prediction")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Category",
                result.category
            )

            st.metric(
                "Priority",
                result.priority
            )

        with col2:

            st.metric(
                "Sentiment",
                result.sentiment
            )

            st.metric(
                "SLA Risk",
                result.sla_risk
            )

        st.divider()

        st.subheader("JSON Output")

        st.json(
            result.model_dump()
        )