import streamlit as st
from ui.components import render_back_navigation, render_metric_card
import time

def show_library_page(vector_db, embedding_manager):
    """
    Renders the document library management system.
    """
    render_back_navigation("Document Library")

    selected_doc_id = st.session_state.get("library_inspect_doc_id", None)

    if selected_doc_id is not None:
        show_document_details(selected_doc_id, vector_db)
        return

    st.markdown("<h1>Document Library</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Inspect, reprocess, or delete documents ingested into your vector database workspace.</p>", unsafe_allow_html=True)

    docs = vector_db.get_all_documents()

    if not docs:
        st.markdown("""
            <div class="premium-card" style="text-align: center; padding: 4rem 2rem; border-style: dashed !important;">
                <div style="font-family: 'Lora', serif; font-size: 1.25rem; color: #2C2F2B; margin-bottom: 0.5rem;">No Documents Found</div>
                <div style="color: #6B7068; margin-bottom: 1.5rem; font-size: 0.9rem;">Your vector workspace is currently empty. Ingest text or PDF files to get started.</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Upload Document", use_container_width=True):
                st.session_state.current_page = "Upload Documents"
                st.rerun()
        return
    for doc in docs:
        size_kb = doc["file_size"] / 1024
        
        st.markdown(f"""
            <div class="premium-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0; font-family: 'Lora', serif; font-size: 1.25rem; color: #2C2F2B;">{doc['filename']}</h3>
                        <div style="font-size: 0.8rem; color: #6B7068; margin-top: 0.25rem;">
                            Ingested on {doc['upload_date']} • File Size: {size_kb:.1f} KB
                        </div>
                    </div>
                    <span style="background-color: #606C5A; color: #ffffff; font-size: 0.75rem; padding: 0.25rem 0.6rem; border-radius: 20px; font-weight: 500;">
                        Indexed
                    </span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 1rem; border-top: 1px solid #DFDAD0; border-bottom: 1px solid #DFDAD0; padding: 0.75rem 0; margin-bottom: 1rem; font-size: 0.85rem; color: #2C2F2B;">
                    <div><strong>Pages:</strong> {doc['pages']}</div>
                    <div><strong>Characters:</strong> {doc['character_count']}</div>
                    <div><strong>Chunks:</strong> {doc['chunk_count']}</div>
                    <div><strong>Embedding:</strong> {doc['embedding_model']}</div>
                    <div><strong>Chunk Size:</strong> {doc['chunk_size']} ch</div>
                    <div><strong>Overlap:</strong> {doc['chunk_overlap']} ch</div>
                </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([4.5, 1.4, 1.7, 1.4])
        with cols[1]:
            st.markdown("<div class='button-primary'>", unsafe_allow_html=True)
            if st.button("Inspect", key=f"btn_inspect_{doc['id']}", use_container_width=True):
                st.session_state.library_inspect_doc_id = doc["id"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown("<div class='button-secondary'>", unsafe_allow_html=True)
            if st.button("Reprocess", key=f"btn_repro_{doc['id']}", use_container_width=True):
                st.info(f"Triggering pipeline reprocessing for {doc['filename']}...")
                time.sleep(1)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with cols[3]:
            st.markdown("<div class='button-warning'>", unsafe_allow_html=True)
            if st.button("Delete", key=f"btn_del_{doc['id']}", use_container_width=True):
                vector_db.delete_document(doc["id"])
                st.success(f"Deleted document from workspace index.")
                time.sleep(0.8)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

def show_document_details(doc_id: int, vector_db):
    """
    Renders details about a single document: metadata, chunks, embeddings.
    """
    doc = vector_db.get_document(doc_id)
    if not doc:
        st.session_state.library_inspect_doc_id = None
        st.rerun()

    if st.button("← Back to Library list", key="btn_library_back"):
        st.session_state.library_inspect_doc_id = None
        st.rerun()

    st.markdown(f"<h1>Document Inspector: {doc['filename']}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Granular details, chunks structure, and embedded coordinate maps of the active document.</p>", unsafe_allow_html=True)

    chunks = vector_db.get_document_chunks(doc_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Document Chunks", str(len(chunks)), "Total vectors stored", color_accent="teal")
    with col2:
        avg_len = sum(len(c["text"]) for c in chunks) / len(chunks) if chunks else 0
        render_metric_card("Avg. Chunk Length", f"{int(avg_len)} ch", "Total characters split", color_accent="sage")
    with col3:
        render_metric_card("Active Pages", str(doc["pages"]), "Total pages extracted")

    tab_chunks, tab_metadata = st.tabs(["Chunk Viewer", "Ingestion Metadata"])
    
    with tab_chunks:
        st.subheader("Chunk Segments & Embeddings preview")
        
        for chunk in chunks:
            conn = sqlite3.connect(vector_db.db_path)
            row = conn.execute("SELECT vector FROM embeddings WHERE chunk_id = ?", (chunk["id"],)).fetchone()
            vec_preview = "No vector found"
            if row:
                import numpy as np
                vec_arr = np.frombuffer(row[0], dtype=np.float32)
                vec_preview = ", ".join([f"{v:.4f}" for v in vec_arr[:5]]) + " ... (dim: " + str(len(vec_arr)) + ")"
            conn.close()

            st.markdown(f"""
                <div style="background-color: #ffffff; border: 1px solid #DFDAD0; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F3EFE9; padding-bottom: 0.5rem; margin-bottom: 0.75rem; font-size: 0.75rem; color: #6B7068;">
                        <span><strong>Chunk Index:</strong> {chunk['chunk_index']}</span>
                        <span><strong>Source Page:</strong> {chunk['page_number']}</span>
                        <span><strong>Character Offsets:</strong> [{chunk['char_start']} - {chunk['char_end']}]</span>
                    </div>
                    <div style="color: #2C2F2B; line-height: 1.6; margin-bottom: 0.75rem; font-family: sans-serif;">
                        {chunk['text']}
                    </div>
                    <div style="font-size: 0.75rem; color: #606C5A; background-color: #FAF8F5; padding: 0.5rem; border-radius: 4px; font-family: monospace;">
                        <strong>Vector Signatures (first 5 elements):</strong><br>
                        [{vec_preview}]
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tab_metadata:
        st.subheader("System Specifications")
        st.json(doc)

import sqlite3
