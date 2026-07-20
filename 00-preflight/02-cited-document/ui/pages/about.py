import streamlit as st
from ui.components import render_back_navigation

def show_about_page():
    """
    Renders the RAG Pipeline Architecture details page.
    """
    render_back_navigation("About Pipeline")

    st.markdown("<h1>Pipeline Architecture</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>A detailed technical reference of the Cited Document Assistant RAG ingestion and verification loops.</p>", unsafe_allow_html=True)

    # 1. Structural Pipeline Diagram
    st.subheader("RAG Workflow Visualizer")
    
    st.markdown("""
        <style>
            .flow-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 0.5rem;
                padding: 1.5rem;
                background-color: #ffffff;
                border: 1px solid #DFDAD0;
                border-radius: 12px;
                margin-bottom: 2rem;
            }
            .flow-box {
                background-color: #F3EFE9;
                border: 1px solid #DFDAD0;
                border-radius: 6px;
                width: 140px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.82rem;
                font-weight: 600;
                color: #3E6B6B;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            }
            .flow-arrow {
                display: flex;
                align-items: center;
                color: #8F9E8B;
                font-weight: bold;
                font-size: 1.1rem;
            }
        </style>
        
        <div class="flow-container">
            <div class="flow-box">Document</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Chunking</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Embeddings</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Vector DB</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Retriever</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Top K Filter</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Prompt</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">LLM</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Grounded Answer</div>
            <div class="flow-arrow">➔</div>
            <div class="flow-box">Citation</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Key Terms Cards
    st.subheader("Core Pipeline Concepts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="premium-card">
                <div class="premium-card-header">Document Chunking & Overlap</div>
                <div style="color: #6B7068; font-size: 0.85rem; line-height: 1.5;">
                    Large texts must be partitioned into segments to fit model context windows. An <strong>Overlap</strong> (e.g. 100 characters) is used between chunks to ensure keywords or sentences at boundary cuts do not lose their structural context.
                </div>
            </div>
            <div class="premium-card">
                <div class="premium-card-header">Text Embeddings</div>
                <div style="color: #6B7068; font-size: 0.85rem; line-height: 1.5;">
                    Embeddings translate textual content into fixed-dimensional numeric vectors. Similar words or phrases are clustered close together in this mathematical space, enabling semantic retrieval.
                </div>
            </div>
            <div class="premium-card">
                <div class="premium-card-header">Cosine Similarity</div>
                <div style="color: #6B7068; font-size: 0.85rem; line-height: 1.5;">
                    Determines document relevance by evaluating the cosine angle between the query vector and candidate chunk vectors:
                    $$\\cos(\\theta) = \\frac{\\mathbf{A} \\cdot \\mathbf{B}}{\\|\\mathbf{A}\\| \\|\\mathbf{B}\\|}$$
                    Scores range from 0.0 (perpendicular/dissimilar) to 1.0 (parallel/identical).
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="premium-card">
                <div class="premium-card-header">Defensive Ingestion Metadata</div>
                <div style="color: #6B7068; font-size: 0.85rem; line-height: 1.5;">
                    Each vector is indexed along with its original page position, character bounds, file tags, and creation dates. This metadata is strictly passed to output schemas to enforce accurate citation references.
                </div>
            </div>
            <div class="premium-card">
                <div class="premium-card-header">Hallucination Prevention</div>
                <div style="color: #6B7068; font-size: 0.85rem; line-height: 1.5;">
                    RAG accuracy depends on avoiding answers when no supporting evidence exists. We achieve this through <strong>Defensive Prompting</strong> (instructing models to strictly answer from context only) and <strong>Retrieval Cutoffs</strong> (refusing similarity scores below 0.45).
                </div>
            </div>
            <div class="premium-card">
                <div class="premium-card-header">LiteVectorDB Storage</div>
                <div style="color: #6B7068; font-size: 0.85rem; line-height: 1.5;">
                    An optimized hybrid database: utilizes SQLite for transaction-safe relational metadata querying, and Numpy array buffers for rapid, in-memory parallel similarity scanning across active workspace matrices.
                </div>
            </div>
        """, unsafe_allow_html=True)
