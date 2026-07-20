import streamlit as st
from ui.components import render_back_navigation, render_metric_card
from core.retrieval import RAGRetriever
import time
import pandas as pd

def show_explorer_page(vector_db, embedding_manager):
    """
    Renders a dedicated RAG search testing sandbox.
    """
    render_back_navigation("Retrieval Explorer")

    st.markdown("<h1>Retrieval Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Run queries to test search performance, inspect vector similarity parameters, and trace ranking structures.</p>", unsafe_allow_html=True)

    # Scoping parameters
    docs = vector_db.get_all_documents()
    
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Query Configuration")
        
        search_query = st.text_input("Enter search text / query:", placeholder="Type query keywords...")
        top_k = st.slider("Max Chunks (Top K)", min_value=1, max_value=12, value=4, step=1)
        threshold = st.slider("Similarity Cutoff", min_value=0.0, max_value=1.0, value=0.40, step=0.05)
        
        # Scoped documents list
        doc_scope_names = []
        doc_scope_ids = []
        if docs:
            st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#2C2F2B; margin-top:1rem;'>File Context Filter:</p>", unsafe_allow_html=True)
            for doc in docs:
                if st.checkbox(doc["filename"], value=True, key=f"explorer_doc_{doc['id']}"):
                    doc_scope_ids.append(doc["id"])
                    
        run_search = st.button("Query Database Index", use_container_width=True)

    with col_right:
        st.subheader("Search Rankings & Scores")
        
        if not search_query:
            st.markdown("""
                <div class="premium-card" style="text-align: center; padding: 4rem 1rem; border-style: dashed !important;">
                    <div style="color: #6B7068; font-size: 0.9rem;">Input a query on the left to run semantic vector search.</div>
                </div>
            """, unsafe_allow_html=True)
            return

        if run_search or search_query:
            retriever = RAGRetriever(vector_db, embedding_manager)
            res = retriever.retrieve(query=search_query, top_k=top_k, threshold=threshold, doc_ids=doc_scope_ids)
            
            chunks = res["chunks"]
            all_retrieved = res["all_retrieved"]
            diagnostics = res["diagnostics"]
            
            # Show summary stats
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                render_metric_card("Retrieved", str(len(all_retrieved)), "Total candidate matches")
            with sc2:
                render_metric_card("Passed Filter", str(len(chunks)), f"Exceeded > {threshold:.2f}")
            with sc3:
                render_metric_card("Highest Similarity", f"{diagnostics['highest_similarity_score']:.4f}", "Closest vector score")
                
            if not all_retrieved:
                st.info("No text matches found in database. Ingest document files first.")
                return

            # Display simple chart showing similarity scores of retrieved items
            st.markdown("<h4>Similarity Score Distribution</h4>", unsafe_allow_html=True)
            scores_data = []
            for idx, item in enumerate(all_retrieved):
                scores_data.append({
                    "Rank": f"Rank #{idx+1}",
                    "Score": item["similarity_score"],
                    "Document": item["doc_name"]
                })
            
            df = pd.DataFrame(scores_data)
            st.bar_chart(df, x="Rank", y="Score", color="Document")

            st.markdown("<h4>Matched Text Blocks</h4>", unsafe_allow_html=True)
            for idx, item in enumerate(all_retrieved):
                passed_text = "PASSED" if item["similarity_score"] >= threshold else "FILTERED OUT"
                badge_bg = "#606C5A" if passed_text == "PASSED" else "#D98A7B"
                
                st.markdown(f"""
                    <div class="premium-card" style="padding:1.25rem !important;">
                        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem; font-size:0.75rem; color:#6B7068; border-bottom:1px solid #DFDAD0; padding-bottom: 0.25rem;">
                            <span><strong>Rank #{idx+1}</strong> • Similarity Score: <strong>{item['similarity_score']:.4f}</strong></span>
                            <span style="background-color:{badge_bg}; color:#ffffff; padding:0.1rem 0.4rem; border-radius:4px; font-weight:600;">{passed_text}</span>
                        </div>
                        <div style="font-size:0.9rem; line-height:1.5; color:#2C2F2B; margin-bottom:0.5rem;">
                            {item['text']}
                        </div>
                        <div style="font-size:0.75rem; color:#6B7068;">
                            <strong>File:</strong> {item['doc_name']} • <strong>Page:</strong> {item['page_number']} • <strong>Chunk ID:</strong> #{item['chunk_index']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
