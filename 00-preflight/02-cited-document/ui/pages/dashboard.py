import streamlit as st
from ui.components import render_metric_card
import time

def show_dashboard_page(vector_db, embedding_manager):
    """
    Renders the primary workspace dashboard.
    """
    st.markdown("<h1>Workspace Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Workspace administration, database indexing status, and systems metrics dashboard.</p>", unsafe_allow_html=True)
    
    stats = vector_db.get_stats()
    docs = vector_db.get_all_documents()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Total Documents", str(stats["document_count"]), "Active workspace files", color_accent="teal")
    with col2:
        render_metric_card("Chunks Indexed", str(stats["chunk_count"]), "Vector index records", color_accent="sage")
    with col3:
        render_metric_card("Total Tokens (Est.)", f"{int(stats['total_characters'] / 4):,}", "Ingested document size")
    with col4:
        render_metric_card("Avg. Chunk Length", f"{stats['average_chunk_length']} ch", "Text partition bounds")

    col_left, col_right = st.columns([5, 3])
    
    with col_left:
        st.subheader("Workspace Files")
        if not docs:
            st.markdown("""
                <div class="premium-card" style="text-align: center; padding: 3rem 1rem; border-style: dashed !important;">
                    <div style="color: #6B7068; margin-bottom: 1rem; font-size: 0.95rem;">No documents ingested yet in this workspace.</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Configure & Upload Files", key="dash_go_upload"):
                st.session_state.current_page = "Upload Documents"
                st.rerun()
        else:
            for doc in docs[:4]:
                st.markdown(f"""
                    <div style="background-color: #ffffff; border: 1px solid #DFDAD0; border-radius: 8px; padding: 0.85rem 1.25rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #2C2F2B; font-size: 0.95rem;">{doc['filename']}</div>
                            <div style="font-size: 0.75rem; color: #6B7068;">Uploaded: {doc['upload_date']} • {doc['pages']} pages • Model: {doc['embedding_model']}</div>
                        </div>
                        <div style="font-size: 0.8rem; font-weight: 500; background-color: #F3EFE9; padding: 0.25rem 0.6rem; border-radius: 4px; color: #3E6B6B;">
                            {doc['chunk_count']} Chunks
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if len(docs) > 4:
                st.markdown(f"<p style='font-size:0.85rem; color:#6B7068; text-align:right; margin-top:0.25rem;'>+ {len(docs) - 4} more files. Open Document Library to view all.</p>", unsafe_allow_html=True)

    with col_right:
        st.subheader("System Health")
        
        model_status = "Fallback Engine (Offline/TF-IDF)" if embedding_manager.is_fallback else f"SentenceTransformer ({embedding_manager.model_name})"
        model_color = "#D98A7B" if embedding_manager.is_fallback else "#606C5A"
        
        db_size_bytes = 0
        if os.path.exists(vector_db.db_path):
            db_size_bytes = os.path.getsize(vector_db.db_path)
        db_size_mb = db_size_bytes / (1024 * 1024)

        st.markdown(f"""
            <div class="premium-card" style="margin-bottom: 1.5rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem; font-size:0.85rem;">
                    <span style="color:#6B7068;">Schema State:</span>
                    <span style="font-weight:600; color:#606C5A;">Operational</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem; font-size:0.85rem;">
                    <span style="color:#6B7068;">Database Size:</span>
                    <span style="font-weight:600; color:#2C2F2B;">{db_size_mb:.2f} MB</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem; font-size:0.85rem;">
                    <span style="color:#6B7068;">Vector Processor:</span>
                    <span style="font-weight:600; color:#2C2F2B;">NumPy Matrix Scanning</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                    <span style="color:#6B7068;">Embedder:</span>
                    <span style="font-weight:600; color:{model_color}; text-align:right;">{model_status}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Quick Launch")
        cols = st.columns(2)
        with cols[0]:
            if st.button("Workspace Chat", use_container_width=True):
                st.session_state.current_page = "Chat Assistant"
                st.rerun()
        with cols[1]:
            if st.button("Library", use_container_width=True):
                st.session_state.current_page = "Document Library"
                st.rerun()
                
import os
