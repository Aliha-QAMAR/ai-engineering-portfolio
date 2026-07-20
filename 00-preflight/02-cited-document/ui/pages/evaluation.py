import streamlit as st
from ui.components import render_back_navigation, render_metric_card
from core.evaluation import RAGEvaluator
import pandas as pd

def show_evaluation_page(vector_db):
    """
    Renders the RAG pipeline evaluation dashboard.
    """
    render_back_navigation("Evaluation Metrics")

    st.markdown("<h1>Evaluation & Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Telemetry analysis, automated pipeline benchmarking, and configuration comparison dashboard.</p>", unsafe_allow_html=True)

    # 1. Gather history for evaluation
    chat_history = st.session_state.get("chat_sessions", [])
    metrics = RAGEvaluator.get_evaluation_metrics(chat_history)
    
    # 2. Main KPI Metrics Row 1
    st.markdown("<h3>Pipeline Reliability Metrics</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Retrieval Hit Rate", f"{metrics['hit_rate']}%", "Top-K context matching", color_accent="teal")
    with col2:
        render_metric_card("Answer Accuracy", f"{metrics['answer_accuracy']}%", "Faithfulness index", color_accent="sage")
    with col3:
        render_metric_card("Citation Presence", f"{metrics['citation_presence']}%", "Reference verification", color_accent="sage")
    with col4:
        render_metric_card("Refusal Accuracy", f"{metrics['refusal_accuracy']}%", "Hallucination block rate", color_accent="teal")

    # KPI Row 2
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        render_metric_card("Average Latency", f"{metrics['avg_latency_ms']} ms", "Total vector + search search delay")
    with col6:
        render_metric_card("Average Cost", f"${metrics['avg_cost_usd']:.5f}", "Calculated API token cost")
    with col7:
        render_metric_card("Hallucination Rate", f"{metrics['hallucination_rate']}%", "Grounding rule compliance", color_accent="coral")
    with col8:
        eval_count = metrics.get("total_queries_evaluated", 0)
        render_metric_card("Telemetry Samples", str(eval_count), "Total workspace queries run")

    st.markdown("<hr style='border:0; border-top:1px solid #DFDAD0; margin:2rem 0;'>", unsafe_allow_html=True)

    # 3. Parameter sweeps charts
    st.markdown("<h3>Ingestion Parameter Comparison Sweeps</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068; font-size: 0.85rem;'>Simulated benchmark curves detailing the trade-offs of chunk size and Top-K thresholds on retrieval accuracy, cost, and retrieval delays.</p>", unsafe_allow_html=True)

    sweep_data = RAGEvaluator.get_parameter_comparison_data()
    
    col_chart_left, col_chart_right = st.columns(2)
    
    with col_chart_left:
        st.markdown("<h4>Chunk Size Impact Sweep</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.75rem; color:#6B7068;'>Smaller chunk sizes isolate precise paragraphs and improve Hit Rates, but can slightly decrease broad contextual reasoning.</p>", unsafe_allow_html=True)
        
        # Prepare pandas dataframe for line chart
        chunk_df = pd.DataFrame({
            "Chunk Size": sweep_data["chunk_sweep"]["chunk_sizes"],
            "Hit Rate (%)": sweep_data["chunk_sweep"]["hit_rates"],
            "Search Latency (ms)": sweep_data["chunk_sweep"]["latencies_ms"]
        })
        
        # Display line chart
        st.line_chart(chunk_df, x="Chunk Size", y=["Hit Rate (%)", "Search Latency (ms)"])
        
    with col_chart_right:
        st.markdown("<h4>Top-K Context Count Sweep</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.75rem; color:#6B7068;'>Higher Top-K values guarantee that relevant chunks are retrieved, but linearly scale token usage, costs, and LLM processing times.</p>", unsafe_allow_html=True)
        
        topk_df = pd.DataFrame({
            "Top-K Value": sweep_data["top_k_sweep"]["top_k_values"],
            "Hit Rate (%)": sweep_data["top_k_sweep"]["hit_rates"],
            "Estimated Cost ($/100)": [v * 1000 for v in sweep_data["top_k_sweep"]["costs_usd"]] # Scale for display
        })
        
        st.line_chart(topk_df, x="Top-K Value", y=["Hit Rate (%)", "Estimated Cost ($/100)"])
