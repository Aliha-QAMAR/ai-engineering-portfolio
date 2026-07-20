import streamlit as st
import os

# Set page configuration early
st.set_page_config(
    page_title="Cited Document Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core imports
from core.vector_db import LiteVectorDB
from core.embeddings import EmbeddingManager
from ui.components import inject_global_styles
from ui.pages.landing import show_landing_page
from ui.pages.dashboard import show_dashboard_page
from ui.pages.upload import show_upload_page
from ui.pages.library import show_library_page
from ui.pages.chat import show_chat_page
from ui.pages.explorer import show_explorer_page
from ui.pages.history import show_history_page
from ui.pages.evaluation import show_evaluation_page
from ui.pages.about import show_about_page

# 1. Initialize DB and Embeddings Managers in Session State
if "vector_db" not in st.session_state:
    st.session_state.vector_db = LiteVectorDB(db_path="workspace.db")
if "embedding_manager" not in st.session_state:
    st.session_state.embedding_manager = EmbeddingManager()
if "current_page" not in st.session_state:
    st.session_state.current_page = "Landing"

# 2. Inject global CSS style overrides
inject_global_styles()

# 3. Routing Controller
current_page = st.session_state.current_page

if current_page == "Landing":
    # Render full-width landing page, collapse/hide sidebar
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    show_landing_page()
else:
    # Render app with sidebar navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">Workspace Admin</div>', unsafe_allow_html=True)
        
        # Navigation buttons styled to look like sleek SaaS links
        # We track navigation using session state
        nav_options = [
            ("Dashboard", "Dashboard"),
            ("Upload Documents", "Upload"),
            ("Document Library", "Documents"),
            ("Chat Assistant", "Chat Workspace"),
            ("Retrieval Explorer", "Retrieval Explorer"),
            ("History", "Conversations Log"),
            ("Evaluation", "Analytics & Stats"),
            ("About Pipeline", "Pipeline Architecture"),
            ("Settings", "Workspace Settings")
        ]
        
        for page_name, display_label in nav_options:
            is_active = current_page == page_name
            # Render a custom sidebar button style
            style_class = "button-active" if is_active else "button-inactive"
            
            # Using custom container to inject specific background/colors for active button
            if is_active:
                st.markdown(f"""
                    <style>
                        div.stButton > button[key="nav_btn_{page_name}"] {{
                            background-color: #606C5A !important;
                            border-color: #606C5A !important;
                            color: #ffffff !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)
                
            if st.button(display_label, key=f"nav_btn_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
                
        st.markdown("<hr style='border:0; border-top:1px solid #DFDAD0; margin:2rem 0 1rem 0;'>", unsafe_allow_html=True)
        if st.button("← Exit Workspace", key="exit_workspace_btn", use_container_width=True):
            st.session_state.current_page = "Landing"
            st.rerun()

    # Route Sub-Pages
    vector_db = st.session_state.vector_db
    embedding_manager = st.session_state.embedding_manager
    
    if current_page == "Dashboard":
        show_dashboard_page(vector_db, embedding_manager)
        
    elif current_page == "Upload Documents":
        show_upload_page(vector_db, embedding_manager)
        
    elif current_page == "Document Library":
        show_library_page(vector_db, embedding_manager)
        
    elif current_page == "Chat Assistant":
        show_chat_page(vector_db, embedding_manager)
        
    elif current_page == "Retrieval Explorer":
        show_explorer_page(vector_db, embedding_manager)
        
    elif current_page == "History":
        show_history_page(vector_db)
        
    elif current_page == "Evaluation":
        show_evaluation_page(vector_db)
        
    elif current_page == "About Pipeline":
        show_about_page()
        
    elif current_page == "Settings":
        st.markdown("<h1>Workspace Settings</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6B7068;'>Manage API integrations and reset database state.</p>", unsafe_allow_html=True)
        
        # Reset DB Action
        st.subheader("Database Operations")
        st.markdown("<p style='font-size:0.85rem; color:#6B7068;'>Clears all document collections, embeddings, and workspace indexes. This action is irreversible.</p>", unsafe_allow_html=True)
        st.markdown("<div class='button-warning'>", unsafe_allow_html=True)
        if st.button("Reset Vector Database Index", key="btn_reset_db"):
            vector_db.clear_database()
            # Clear chat history too
            st.session_state.chat_sessions = [{"id": 0, "title": "New Conversation", "messages": []}]
            st.success("Workspace database and chat sessions successfully cleared.")
            time.sleep(0.8)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Simulated API Settings
        st.subheader("Model Integrations")
        st.markdown("<p style='font-size:0.85rem; color:#6B7068;'>Configure external LLM providers. By default, workspace operates local extractive synthesis.</p>", unsafe_allow_html=True)
        st.text_input("OpenAI API Key (Optional)", type="password", placeholder="sk-...")
        st.text_input("Gemini API Key (Optional)", type="password", placeholder="AIzaSy...")

import time
