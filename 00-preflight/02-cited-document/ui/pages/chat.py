import streamlit as st
from ui.components import render_back_navigation
from core.retrieval import RAGRetriever
from core.llm_engine import GroundedLLMEngine
import datetime
import time

def show_chat_page(vector_db, embedding_manager):
    """
    Renders the 3-column Document Review Workspace (Chat Assistant).
    """
    render_back_navigation("Chat Assistant")

    # Initialize chat history and retriever
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = [{"id": 0, "title": "New Conversation", "messages": []}]
    if "active_session_idx" not in st.session_state:
        st.session_state.active_session_idx = 0
    if "chat_input_text" not in st.session_state:
        st.session_state.chat_input_text = ""
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False

    session = st.session_state.chat_sessions[st.session_state.active_session_idx]
    messages = session["messages"]
    
    retriever = RAGRetriever(vector_db, embedding_manager)
    engine = GroundedLLMEngine()

    # Get all documents for scoping
    docs = vector_db.get_all_documents()

    # Define the 3-column Layout
    col_left, col_center, col_right = st.columns([1, 2, 1])

    # ==========================================
    # COLUMN 1: DOCUMENT EXPLORER (LEFT PANEL)
    # ==========================================
    with col_left:
        st.markdown("<h3 style='margin-top:0;'>Document Explorer</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8rem; color:#6B7068;'>Filter the retrieval context by selecting specific documents.</p>", unsafe_allow_html=True)
        
        scoped_doc_ids = []
        if not docs:
            st.markdown("""
                <div style='background-color:#ffffff; border:1px solid #DFDAD0; border-radius:8px; padding:1rem; text-align:center; font-size:0.85rem; color:#6B7068;'>
                    No documents uploaded. Click 'Dashboard' to add files.
                </div>
            """, unsafe_allow_html=True)
        else:
            # Checkbox scope controls
            st.markdown("<div style='max-height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
            for doc in docs:
                is_selected = st.checkbox(
                    doc["filename"],
                    value=True,
                    key=f"scope_chk_{doc['id']}",
                    help=f"{doc['pages']} pages • {doc['chunk_count']} chunks"
                )
                if is_selected:
                    scoped_doc_ids.append(doc["id"])
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Show active scope count
            st.markdown(f"""
                <div style='margin-top: 1rem; font-size:0.75rem; color:#6B7068; background-color:#F3EFE9; padding:0.5rem; border-radius:4px;'>
                    Active Context Scope: <strong>{len(scoped_doc_ids)} of {len(docs)} files</strong>
                </div>
            """, unsafe_allow_html=True)

        # In-page Settings
        st.markdown("<hr style='border:0; border-top:1px solid #DFDAD0; margin:1.5rem 0;'>", unsafe_allow_html=True)
        st.subheader("Retrieval Tuning")
        chat_top_k = st.slider("Top K Chunks", min_value=1, max_value=10, value=5, step=1, key="chat_top_k")
        chat_threshold = st.slider("Similarity Threshold", min_value=0.0, max_value=1.0, value=0.45, step=0.05, key="chat_threshold")
        
        # Debug toggle
        st.session_state.debug_mode = st.toggle("Debug Panel Info", value=st.session_state.debug_mode)

    # ==========================================
    # COLUMN 2: CONVERSATION WORKSPACE (CENTER PANEL)
    # ==========================================
    with col_center:
        st.markdown("<h3 style='margin-top:0; text-align:center; font-family:Lora;'>Conversation Workspace</h3>", unsafe_allow_html=True)
        
        # Scrollable message area
        chat_container = st.container()
        
        with chat_container:
            if not messages:
                st.markdown("""
                    <div style="text-align: center; padding: 4rem 1rem; color: #6B7068; font-size: 0.95rem;">
                        <svg viewBox="0 0 24 24" width="40" height="40" stroke="#8F9E8B" stroke-width="1.5" fill="none" style="margin:0 auto 1rem auto; display:block;">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        Workspace chat initialized. Enter a question below to run semantic retrieval.
                    </div>
                """, unsafe_allow_html=True)
            else:
                for idx, msg in enumerate(messages):
                    is_user = msg["role"] == "user"
                    class_name = "user" if is_user else "assistant"
                    
                    st.markdown(f"""
                        <div class="chat-bubble-container {class_name}">
                            <div class="chat-bubble">
                                <div style="font-weight: 600; font-size: 0.8rem; margin-bottom: 0.25rem; color:#606C5A;">
                                    { 'USER' if is_user else 'CITED ASSISTANT' }
                                </div>
                                <div style="word-break: break-word;">{msg['content']}</div>
                                <div class="chat-timestamp">{msg.get('timestamp', '')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        # Suggested prompt options floating above input
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        suggestions = ["What are the key policy requirements?", "Summarize the uploaded documents", "Are there any compliance deadlines?"]
        scols = st.columns(3)
        clicked_suggestion = None
        for i, sug in enumerate(suggestions):
            with scols[i]:
                # Make suggestion look premium
                if st.button(sug, key=f"sug_btn_{i}", use_container_width=True):
                    clicked_suggestion = sug

        # Chat Input Form
        # To handle clear inputs neatly, we use a key and submit handlers
        with st.form(key="chat_input_form", clear_on_submit=True):
            user_query = st.text_input("Ask a question about your documents...", key="user_query_input", placeholder="Type query and press enter...")
            submit_button = st.form_submit_button("Ask Assistant", use_container_width=True)

        # If a suggestion or text input was submitted
        active_query = clicked_suggestion or (user_query if submit_button else None)

        if active_query:
            # 1. Append user query
            timestamp = datetime.datetime.now().strftime("%I:%M %p")
            messages.append({
                "role": "user",
                "content": active_query,
                "timestamp": timestamp
            })
            st.rerun()

        # Generate Assistant response if last message is from user
        if messages and messages[-1]["role"] == "user":
            user_msg = messages[-1]["content"]
            
            with chat_container:
                # Setup visual spinner and empty block
                with st.spinner("Retrieving document context and generating answer..."):
                    # Step A: Retrieval
                    retrieval_res = retriever.retrieve(
                        query=user_msg, 
                        top_k=chat_top_k, 
                        threshold=chat_threshold, 
                        doc_ids=scoped_doc_ids
                    )
                    
                    # Step B: LLM Generation
                    # Set up placeholder for stream
                    stream_placeholder = st.empty()
                    
                    # Stream generator yield loop
                    answer_buffer = ""
                    generator = engine.generate_response_stream(
                        query=user_msg,
                        chunks=retrieval_res["chunks"],
                        diagnostics=retrieval_res["diagnostics"]
                    )
                    
                    for token in generator:
                        answer_buffer += token
                        # Render partially streamed response in chat styling
                        stream_placeholder.markdown(f"""
                            <div class="chat-bubble-container assistant">
                                <div class="chat-bubble">
                                    <div style="font-weight: 600; font-size: 0.8rem; margin-bottom: 0.25rem; color:#606C5A;">CITED ASSISTANT (streaming...)</div>
                                    <div style="word-break: break-word;">{answer_buffer}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    # Step C: Evaluate final details
                    response_details = engine.generate_response_details(
                        query=user_msg,
                        chunks=retrieval_res["chunks"],
                        diagnostics=retrieval_res["diagnostics"],
                        full_answer_text=answer_buffer
                    )
                    
                    timestamp = datetime.datetime.now().strftime("%I:%M %p")
                    messages.append({
                        "role": "assistant",
                        "content": answer_buffer,
                        "timestamp": timestamp,
                        "metrics": response_details,
                        "diagnostics": retrieval_res["diagnostics"],
                        "retrieved_chunks": retrieval_res["chunks"]
                    })
                    
            st.rerun()

    # ==========================================
    # COLUMN 3: EVIDENCE & CITATION PANEL (RIGHT PANEL)
    # ==========================================
    with col_right:
        st.markdown("<h3 style='margin-top:0;'>Evidence Panel</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8rem; color:#6B7068;'>Citations, source texts, similarity parameters, and grounding indices.</p>", unsafe_allow_html=True)

        # Get last assistant message to retrieve evidence
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]
        
        if not assistant_msgs:
            st.markdown("""
                <div style='background-color:#ffffff; border:1px solid #DFDAD0; border-radius:8px; padding:1.5rem; text-align:center; font-size:0.85rem; color:#6B7068; line-height: 1.5;'>
                    Ask a question to load retrieval evidence here.
                </div>
            """, unsafe_allow_html=True)
        else:
            last_msg = assistant_msgs[-1]
            metrics = last_msg.get("metrics", {})
            diag = last_msg.get("diagnostics", {})
            chunks = last_msg.get("retrieved_chunks", [])
            
            # Grounding Status Badge
            status = metrics.get("grounding_status", "Unknown")
            status_color = "#606C5A" if "Verified" in status else "#D98A7B"
            
            st.markdown(f"""
                <div style="background-color: {status_color}; color: #ffffff; text-align: center; border-radius: 6px; padding: 0.4rem; font-size: 0.85rem; font-weight: 600; margin-bottom: 1.5rem;">
                    Status: {status}
                </div>
            """, unsafe_allow_html=True)

            # Metadata Indicators
            st.markdown(f"""
                <div class="premium-card" style="padding: 1rem !important; margin-bottom: 1rem; font-size:0.8rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.4rem;">
                        <span style="color:#6B7068;">Confidence Index:</span>
                        <span style="font-weight:600; color:#2C2F2B;">{metrics.get('confidence_score', 0.0)}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.4rem;">
                        <span style="color:#6B7068;">Search Latency:</span>
                        <span style="font-weight:600; color:#2C2F2B;">{diag.get('latency_ms', 0.0):.1f} ms</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.4rem;">
                        <span style="color:#6B7068;">Citation Count:</span>
                        <span style="font-weight:600; color:#2C2F2B;">{metrics.get('citation_count', 0)} sources</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#6B7068;">Processing Cost:</span>
                        <span style="font-weight:600; color:#2C2F2B;">${metrics.get('processing_cost_usd', 0.0):.6f}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Retrieved source text chunks
            st.subheader("Citations & Raw Chunks")
            
            if not chunks:
                st.markdown("<p style='font-size:0.8rem; color:#6B7068;'>No context blocks exceeded similarity threshold.</p>", unsafe_allow_html=True)
            else:
                for i, chunk in enumerate(chunks):
                    # Collapsible details per chunk
                    with st.expander(f"[{i+1}] {chunk['doc_name']} (p. {chunk['page_number']})"):
                        st.markdown(f"""
                            <div style="font-size: 0.85rem; line-height: 1.5; color:#2C2F2B; margin-bottom: 0.5rem;">
                                {chunk['text']}
                            </div>
                            <div style="font-size: 0.75rem; border-top:1px solid #DFDAD0; padding-top:0.35rem; color:#606C5A;">
                                <strong>Similarity:</strong> {chunk['similarity_score']:.4f} <br>
                                <strong>Chunk ID:</strong> #{chunk['chunk_index']}
                            </div>
                        """, unsafe_allow_html=True)

            # Get last user query for debug log
            last_user_query = ""
            for m in reversed(messages):
                if m["role"] == "user":
                    last_user_query = m["content"]
                    break

            # Debug Mode expansion
            if st.session_state.debug_mode:
                st.markdown("<hr style='border:0; border-top:1px solid #DFDAD0; margin:1rem 0;'>", unsafe_allow_html=True)
                st.subheader("Debug Telemetry")
                with st.expander("Show Ingested Prompt Logs", expanded=False):
                    st.code(f"System Prompt: ...\nQuery: {last_user_query}\nContext length: {len(chunks)} blocks")
                st.json(diag)
