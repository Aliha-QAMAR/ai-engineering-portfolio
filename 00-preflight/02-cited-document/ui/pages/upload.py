import streamlit as st
import time
from ui.components import render_back_navigation, render_pipeline_visualizer
from core.chunking import DocumentChunker
import datetime

def show_upload_page(vector_db, embedding_manager):
    """
    Renders the document ingestion configuration page.
    """
    render_back_navigation("Upload Documents")
    
    st.markdown("<h1>Ingestion Pipeline Configuration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Configure processing parameters and upload documents for vectorization.</p>", unsafe_allow_html=True)

    # 1. Split Layout: Config on left, Upload on right
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.subheader("Pipeline Settings")
        
        emb_model = st.selectbox(
            "Embedding Model",
            options=["all-MiniLM-L6-v2", "bge-small-en-v1.5", "local-tfidf-fallback"],
            index=0,
            help="High-dimensional text representation model. all-MiniLM-L6-v2 projects text into a 384-dimensional dense semantic space."
        )
        
        chunk_size = st.slider(
            "Chunk Size (Characters)",
            min_value=400,
            max_value=1200,
            value=800,
            step=100,
            help="Maximum length of characters per sliding window block. Smaller sizes capture local topics; larger sizes preserve general context."
        )
        
        chunk_overlap = st.slider(
            "Chunk Overlap (Characters)",
            min_value=50,
            max_value=200,
            value=100,
            step=50,
            help="Overlap size between contiguous chunks. Minimizes context loss at boundaries."
        )
        
        vector_db_opt = st.selectbox(
            "Vector Database",
            options=["SQLite (StoneDB - Cosine Scanned)", "ChromaDB (In-Memory Mock)", "In-Memory NumPy"],
            index=0,
            help="The active storage index for vector vectors and text metadata."
        )
        
        st.markdown("""
            <div style="font-size: 0.75rem; color: #6B7068; line-height: 1.4; border-top: 1px solid #DFDAD0; padding-top: 1rem; margin-top: 1rem;">
                <strong>Standard Configurations:</strong><br>
                • Legal texts: 800 size, 100 overlap<br>
                • Technical manuals: 600 size, 100 overlap<br>
                • Narrative prose: 1000 size, 150 overlap
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.subheader("Workspace Ingestion Zone")
        
        # Hide standard file uploader button styling to look like a drag-and-drop area only
        st.markdown("""
            <style>
                [data-testid="stFileUploader"] {
                    background-color: #ffffff;
                    border: 2px dashed #DFDAD0 !important;
                    border-radius: 12px !important;
                    padding: 1rem !important;
                    text-align: center;
                    cursor: pointer;
                }
                [data-testid="stFileUploader"] section {
                    padding: 0 !important;
                }
                [data-testid="stFileUploaderDropzone"] {
                    border: none !important;
                    background-color: transparent !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # File uploader
        uploaded_files = st.file_uploader(
            "Drag & Drop File Here",
            type=["pdf", "md", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        # Guide message
        st.markdown("""
            <div style="text-align: center; color: #6B7068; font-size: 0.85rem; margin-top: 0.5rem; margin-bottom: 2rem;">
                Supported file formats: <strong>PDF, Markdown (.md), Text (.txt)</strong>
            </div>
        """, unsafe_allow_html=True)

        if uploaded_files:
            # We process files that were uploaded
            for idx, uploaded_file in enumerate(uploaded_files):
                # Check if document already exists
                existing_docs = [d["filename"] for d in vector_db.get_all_documents()]
                if uploaded_file.name in existing_docs:
                    st.warning(f"File '{uploaded_file.name}' already exists in workspace. Re-ingestion will overwrite.")
                    
                # Ingestion Trigger Button
                if st.button(f"Process and Index: {uploaded_file.name}", key=f"btn_process_{uploaded_file.name}_{idx}"):
                    # Ingestion Animation & Pipeline Stepper
                    pipeline_placeholder = st.empty()
                    progress_bar = st.progress(0)
                    
                    # 1. Ingesting text
                    pipeline_placeholder.empty()
                    with pipeline_placeholder.container():
                        st.markdown("<p style='font-weight:600; color: #3E6B6B;'>Step 1: Extracting raw text from document...</p>", unsafe_allow_html=True)
                        render_pipeline_visualizer(active_step=0)
                    file_bytes = uploaded_file.read()
                    
                    pages_data = DocumentChunker.extract_text_from_file(file_bytes, uploaded_file.name)
                    total_chars = sum(len(p["text"]) for p in pages_data)
                    total_pages = len(pages_data)
                    progress_bar.progress(25)
                    time.sleep(0.6)
                    
                    # 2. Chunking text
                    pipeline_placeholder.empty()
                    with pipeline_placeholder.container():
                        st.markdown("<p style='font-weight:600; color: #3E6B6B;'>Step 2: Partitioning text into sliding-window chunks...</p>", unsafe_allow_html=True)
                        render_pipeline_visualizer(active_step=1)
                    chunks = DocumentChunker.create_chunks(pages_data, chunk_size, chunk_overlap)
                    progress_bar.progress(50)
                    time.sleep(0.6)
                    
                    # 3. Vector Embeddings
                    pipeline_placeholder.empty()
                    with pipeline_placeholder.container():
                        st.markdown(f"<p style='font-weight:600; color: #3E6B6B;'>Step 3: Vectorizing {len(chunks)} text chunks using {emb_model}...</p>", unsafe_allow_html=True)
                        render_pipeline_visualizer(active_step=2)
                    chunk_texts = [c["text"] for c in chunks]
                    embeddings = embedding_manager.embed_texts(chunk_texts)
                    progress_bar.progress(75)
                    time.sleep(0.6)
                    
                    # 4. Storage & Indexing
                    pipeline_placeholder.empty()
                    with pipeline_placeholder.container():
                        st.markdown("<p style='font-weight:600; color: #3E6B6B;'>Step 4: Writing records to LiteVectorDB SQLite storage...</p>", unsafe_allow_html=True)
                        render_pipeline_visualizer(active_step=3)
                        
                    doc_metadata = {
                        "filename": uploaded_file.name,
                        "upload_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_size": len(file_bytes),
                        "character_count": total_chars,
                        "embedding_model": emb_model,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "pages": total_pages
                    }
                    
                    try:
                        vector_db.add_document(doc_metadata, chunks, embeddings)
                        progress_bar.progress(100)
                        
                        pipeline_placeholder.empty()
                        with pipeline_placeholder.container():
                            st.markdown("<p style='font-weight:600; color: #606C5A; font-size: 1.1rem;'>✓ Pipeline Ingestion Complete</p>", unsafe_allow_html=True)
                            render_pipeline_visualizer(active_step=4)
                            
                        # Show success summary
                        st.success(f"Successfully processed and indexed document! Created {len(chunks)} chunks.")
                        
                        # Add a clean delay before refreshing to clear files or direct to library
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save document to vector database: {str(e)}")
                        pipeline_placeholder.empty()
