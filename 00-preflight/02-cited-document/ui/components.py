import streamlit as st
import os

def inject_global_styles():
    """
    Reads the custom stylesheet from ui/styles.css and injects it
    globally into the Streamlit rendering process.
    """
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:

        st.markdown("""
            <style>
                .stApp { background-color: #FAF8F5 !important; }
            </style>
        """, unsafe_allow_html=True)

def render_back_navigation(current_page: str):
    """
    Renders standard premium page header with back routing actions.
    """
    col1, col2 = st.columns([7, 1])
    with col1:
        st.markdown(f"<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    with col2:
        if st.button("Exit ", key="nav_back_land"):
            st.session_state.current_page = "Landing"
            st.rerun()

def render_metric_card(title: str, value: str, subtitle: str = None, color_accent: str = "teal"):
    """
    Renders a premium metric display card with warm colors.
    """
    accent_bar = "#3E6B6B" if color_accent == "teal" else ("#606C5A" if color_accent == "sage" else "#D98A7B")
    
    html = f"""
    <div class="premium-card" style="border-left: 4px solid {accent_bar} !important; margin-bottom: 0.5rem;">
        <div style="font-size: 0.85rem; color: #6B7068; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #2C2F2B; margin: 0.25rem 0; font-family: 'Lora', serif;">{value}</div>
        {"<div style='font-size: 0.8rem; color: #8F9E8B;'>" + subtitle + "</div>" if subtitle else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_pipeline_visualizer(active_step: int = 0):
    """
    Renders an interactive-looking pipeline layout.
    """
    steps = [
        {"name": "Document Ingestion", "desc": "Upload and extract raw text segments."},
        {"name": "Semantic Chunking", "desc": "Divide document into page-aware contexts."},
        {"name": "Vector Embeddings", "desc": "Convert text into high-dimensional signatures."},
        {"name": "Database Storage", "desc": "Store records and build indices in workspace DB."}
    ]
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    for i, step in enumerate(steps):
        status_class = "completed" if i < active_step else ("active" if i == active_step else "")
        title_prefix = "✓ " if i < active_step else ("⚡ " if i == active_step else "○ ")
        
        color = "#606C5A" if i < active_step else ("#3E6B6B" if i == active_step else "#DFDAD0")
        
        st.markdown(f"""
        <div class="pipeline-step {status_class}" style="border-left-color: {color} !important;">
            <div class="pipeline-step-title" style="color: {color} !important;">{title_prefix}{step['name']}</div>
            <div class="pipeline-step-desc">{step['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
