import streamlit as st

def show_landing_page():
    """
    Renders the premium marketing landing page for the portfolio project.
    """
    # Custom CSS blobs background container
    st.markdown("""
        <style>
            .hero-container {
                position: relative;
                padding: 2.5rem 1.5rem;
                text-align: center;
                background: linear-gradient(135deg, rgba(243, 239, 233, 0.6) 0%, rgba(250, 248, 245, 0.95) 100%);
                border-radius: 20px;
                border: 1px solid #DFDAD0;
                margin-top: -2.5rem; /* Drastically reduces empty space at the top */
                margin-bottom: 2.5rem;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(44, 47, 43, 0.02);
            }
            /* Floating animated gradient leaks */
            .blob {
                position: absolute;
                border-radius: 50%;
                filter: blur(60px);
                opacity: 0.12;
                z-index: 0;
                animation: float-blob 15s infinite alternate ease-in-out;
            }
            .blob-1 {
                width: 280px;
                height: 280px;
                background-color: #3E6B6B;
                top: -60px;
                left: -60px;
            }
            .blob-2 {
                width: 320px;
                height: 320px;
                background-color: #8F9E8B;
                bottom: -90px;
                right: -90px;
                animation-delay: -6s;
            }
            @keyframes float-blob {
                0% { transform: translate(0, 0) scale(1); }
                50% { transform: translate(30px, -40px) scale(1.08); }
                100% { transform: translate(-15px, 15px) scale(0.95); }
            }
            /* Subtle grid background pattern */
            .grid-overlay {
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background-image: radial-gradient(#DFDAD0 1px, transparent 1px);
                background-size: 24px 24px;
                opacity: 0.2;
                z-index: 0;
            }
            /* Animated Folder Logo CSS */
            .folder-animation {
                display: flex;
                justify-content: center;
                margin: 0 auto 1.25rem auto;
                width: 100px;
                height: 90px;
                position: relative;
                z-index: 1;
                perspective: 1000px;
            }
            .folder-front {
                transform-origin: bottom center;
                animation: open-folder 4s infinite alternate ease-in-out;
            }
            @keyframes open-folder {
                0%, 15% { transform: rotateX(0deg); fill: #F3EFE9; }
                45%, 100% { transform: rotateX(-40deg); fill: #DFDAD0; }
            }
            .doc-sheets .sheet-1 {
                animation: fly-sheet-1 4s infinite alternate ease-in-out;
                transform-origin: bottom center;
            }
            .doc-sheets .sheet-2 {
                animation: fly-sheet-2 4s infinite alternate ease-in-out;
                transform-origin: bottom center;
            }
            @keyframes fly-sheet-1 {
                0%, 20% { transform: translateY(0px) rotate(0deg); opacity: 0; }
                55%, 100% { transform: translateY(-16px) rotate(-6deg); opacity: 1; }
            }
            @keyframes fly-sheet-2 {
                0%, 30% { transform: translateY(0px) rotate(0deg); opacity: 0; }
                65%, 100% { transform: translateY(-24px) rotate(6deg); opacity: 1; }
            }
            .hero-content {
                position: relative;
                z-index: 1;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 3rem;
            }
            .tech-badge {
                background-color: #F3EFE9;
                border: 1px solid #DFDAD0;
                color: #2C2F2B;
                padding: 0.35rem 0.75rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 500;
                display: inline-block;
                margin: 0.25rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <div class="grid-overlay"></div>
            <div class="blob blob-1"></div>
            <div class="blob blob-2"></div>
            <div class="hero-content">
                <div class="folder-animation">
                    <!-- Premium Animated SVG Folder and documents -->
                    <svg viewBox="0 0 100 80" width="100" height="80" style="overflow: visible;">
                        <!-- Folder Back Cover -->
                        <path d="M10 18 L35 18 L42 25 L90 25 L90 72 L10 72 Z" fill="#DFDAD0" stroke="#606C5A" stroke-width="1.5" stroke-linejoin="round"/>
                        <!-- Floating Sheets -->
                        <g class="doc-sheets">
                            <rect x="22" y="10" width="46" height="50" rx="3" fill="#ffffff" stroke="#DFDAD0" stroke-width="1" class="sheet-1"/>
                            <rect x="30" y="6" width="46" height="50" rx="3" fill="#ffffff" stroke="#3E6B6B" stroke-width="1" class="sheet-2"/>
                        </g>
                        <!-- Folder Front Cover (opens with keyframe) -->
                        <path d="M10 30 L90 30 L90 72 L10 72 Z" fill="#F3EFE9" stroke="#606C5A" stroke-width="1.5" stroke-linejoin="round" class="folder-front"/>
                    </svg>
                </div>
                <h1 style="font-size: 3rem; margin-bottom: 0.5rem; letter-spacing: -0.03em;">Cited Document Assistant</h1>
                <div style="font-family: 'Lora', serif; font-size: 1.5rem; color: #606C5A; font-style: italic; margin-bottom: 1.5rem;">
                    Understand Every Document with Confidence
                </div>
                <p style="max-width: 700px; margin: 0 auto 2rem auto; font-size: 1.1rem; line-height: 1.6; color: #6B7068;">
                    Upload enterprise documentation, explore highly verified information, trace every answer back to its exact page/paragraph coordinates, and inspect the complete semantic retrieval pipeline.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CTA Button container
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        # Wrap button inside custom CSS for smooth transition & expansion
        st.markdown("<div style='text-align: center; margin-bottom: 4rem;'>", unsafe_allow_html=True)
        if st.button("Enter Dashboard", key="enter_dash_btn", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Features Section
    st.subheader("Core Capabilities")
    st.markdown("""
        <div class="feature-grid">
            <div class="premium-card">
                <div class="premium-card-header">Grounded Answers</div>
                <div style="color: #6B7068; font-size: 0.9rem; line-height: 1.5;">
                    Response synthesis strictly uses text segments parsed from your document vector database. Synthesizer rejects prompt injections and refuses to hallucinate when evidence is missing.
                </div>
            </div>
            <div class="premium-card">
                <div class="premium-card-header">Granular Citation Mapping</div>
                <div style="color: #6B7068; font-size: 0.9rem; line-height: 1.5;">
                    Traces references back to source file, page index, and chunk boundaries. Dynamic evidence panel shows raw texts and similarity distances.
                </div>
            </div>
            <div class="premium-card">
                <div class="premium-card-header">Retrieval Diagnostics</div>
                <div style="color: #6B7068; font-size: 0.9rem; line-height: 1.5;">
                    Dedicated query explorer lets developers run text embeddings searches, evaluate distance rankings, filter thresholds, and inspect prompt logs.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Architecture Preview
    st.subheader("Ingestion & Inference Pipeline")
    st.markdown("""
        <div class="premium-card" style="padding: 2rem;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <span style="font-weight:600; font-size: 1rem; color:#2C2F2B;">File Ingestion</span>
                <span style="color:#DFDAD0; margin: 0 10px;">➔</span>
                <span style="font-weight:600; font-size: 1rem; color:#2C2F2B;">Recursive Chunker</span>
                <span style="color:#DFDAD0; margin: 0 10px;">➔</span>
                <span style="font-weight:600; font-size: 1rem; color:#2C2F2B;">MiniLM Vectorization</span>
                <span style="color:#DFDAD0; margin: 0 10px;">➔</span>
                <span style="font-weight:600; font-size: 1rem; color:#2C2F2B;">LiteVectorDB Indexing</span>
            </div>
            <div style="font-size: 0.9rem; color:#6B7068; line-height: 1.6; text-align: center;">
                Built on industry-standard engineering practices using semantic paragraph chunking, dense vector similarity scoring, and strict RAG grounding evaluation loops.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Tech Stack
    st.subheader("Technology Stack")
    st.markdown("""
        <div style="margin-bottom: 3rem; text-align:center;">
            <span class="tech-badge">Streamlit Interface</span>
            <span class="tech-badge">Python Core</span>
            <span class="tech-badge">SQLite Database</span>
            <span class="tech-badge">NumPy Scoring</span>
            <span class="tech-badge">Sentence Transformers</span>
            <span class="tech-badge">Scikit-Learn Fallbacks</span>
            <span class="tech-badge">PDFPlumber Extractor</span>
        </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <hr style="border: 0; border-top: 1px solid #DFDAD0; margin: 3rem 0 1rem 0;">
        <div style="text-align: center; font-size: 0.8rem; color:#6B7068; padding-bottom: 2rem;">
            AI Engineering Portfolio • Cited Document Assistant • © 2026
        </div>
    """, unsafe_allow_html=True)
