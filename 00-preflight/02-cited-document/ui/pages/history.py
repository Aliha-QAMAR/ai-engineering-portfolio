import streamlit as st
from ui.components import render_back_navigation
import json

def show_history_page(vector_db):
    """
    Renders the Conversation History timelines manager.
    """
    render_back_navigation("History")

    st.markdown("<h1>Conversation History</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7068;'>Browse, export, or manage past workspace conversations and grounding diagnostic histories.</p>", unsafe_allow_html=True)

    if "chat_sessions" not in st.session_state or not st.session_state.chat_sessions:
        st.session_state.chat_sessions = [{"id": 0, "title": "New Conversation", "messages": []}]

    sessions = st.session_state.chat_sessions

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("Search conversations by message content:", placeholder="Search keywords...")
    with col_filter:
        filter_status = st.selectbox("Status Filter", ["All Sessions", "With Answers", "Empty Sessions"])
    filtered_sessions = []
    for s in sessions:

        text_match = True
        if search_query:
            text_match = False
            for m in s["messages"]:
                if search_query.lower() in m["content"].lower():
                    text_match = True
                    break
        
        status_match = True
        msg_count = len(s["messages"])
        if filter_status == "With Answers" and msg_count == 0:
            status_match = False
        elif filter_status == "Empty Sessions" and msg_count > 0:
            status_match = False

        if text_match and status_match:
            filtered_sessions.append(s)

    if not filtered_sessions:
        st.markdown("""
            <div class="premium-card" style="text-align: center; padding: 4rem 1rem; border-style: dashed !important;">
                <div style="color: #6B7068; font-size: 0.95rem;">No historical records match your search query.</div>
            </div>
        """, unsafe_allow_html=True)
        return

    for idx, s in enumerate(filtered_sessions):
        msg_count = len(s["messages"])
        
        st.markdown(f"""
            <div class="premium-card" style="margin-bottom:1.5rem !important;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <div>
                        <h3 style="margin:0; font-family:'Lora'; font-size:1.2rem; color:#2C2F2B;">{s['title']}</h3>
                        <div style="font-size:0.75rem; color:#6B7068; margin-top:0.25rem;">
                            Session ID: #{s['id']} • Total interactions: {msg_count}
                        </div>
                    </div>
                    <span style="background-color:#F3EFE9; color:#3E6B6B; font-size:0.8rem; padding:0.25rem 0.6rem; border-radius:4px; font-weight:600;">
                        {msg_count // 2} Q&A Pairs
                    </span>
                </div>
        """, unsafe_allow_html=True)

        if msg_count > 0:
            preview_q = s["messages"][0]["content"]
            preview_a = s["messages"][1]["content"] if len(s["messages"]) > 1 else "[Generating...]"
            st.markdown(f"""
                <div style="background-color:#FAF8F5; border-left:3px solid #606C5A; padding:0.75rem 1rem; margin-bottom:0.75rem; font-size:0.9rem; color:#2C2F2B;">
                    <strong>Q:</strong> <i>{preview_q}</i><br>
                    <div style="margin-top:0.35rem; color:#6B7068;">
                        <strong>A:</strong> {preview_a[:160]}...
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View Full Transcript ({msg_count} messages)"):
                for m in s["messages"]:
                    role_label = "USER" if m["role"] == "user" else "CITED ASSISTANT"
                    bg_color = "#F3EFE9" if m["role"] == "user" else "#ffffff"
                    st.markdown(f"""
                        <div style="background-color:{bg_color}; border: 1px solid #DFDAD0; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.5rem; font-size:0.9rem;">
                            <span style="font-weight:700; font-size:0.75rem; color:#606C5A; display:block; margin-bottom:0.25rem;">{role_label} ({m.get('timestamp', '')})</span>
                            <div style="color:#2C2F2B; line-height:1.5;">{m['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:0.85rem; color:#6B7068; font-style:italic;'>Empty session context.</p>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        cols = st.columns([5, 1.2, 1.2])
        with cols[1]:
            export_str = json.dumps(s, indent=2)
            st.markdown("<div class='button-secondary'>", unsafe_allow_html=True)
            st.download_button(
                "Export JSON",
                data=export_str,
                file_name=f"conversation_session_{s['id']}.json",
                mime="application/json",
                key=f"btn_exp_hist_{s['id']}",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown("<div class='button-warning'>", unsafe_allow_html=True)
            if st.button("Delete Session", key=f"btn_del_hist_{s['id']}", use_container_width=True):
                st.session_state.chat_sessions = [session for session in sessions if session["id"] != s["id"]]
                if not st.session_state.chat_sessions:
                    st.session_state.chat_sessions = [{"id": 0, "title": "New Conversation", "messages": []}]
                st.success("Conversation history record removed.")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
