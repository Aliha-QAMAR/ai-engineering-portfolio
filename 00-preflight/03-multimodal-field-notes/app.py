import os
import streamlit as st
from schemas import FitCheckAnalysis
from vision import extract_image_data, ask_image_question
from transcribe import transcribe_audio
from summarize import summarize_transcript
from speak import text_to_speech

st.set_page_config(page_title="FitCheck & Voice Notes AI", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .stButton>button { background-color: #6366F1; color: white; border-radius: 8px; border: none; }
</style>
""", unsafe_allow_allow_html=True)

st.title("✨ FitCheck & Multimodal Voice Assistant")

tab1, tab2 = st.tabs(["👗 Fit Check & Vision", "🎧 Voice Memo & Audio Assistant"])

with tab1:
    st.header("Upload Outfit or Image")
    uploaded_image = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        temp_img_path = f"temp_{uploaded_image.name}"
        with open(temp_img_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
            user_q = st.text_input("Ask a question about this image:")
            if st.button("Ask Question"):
                ans, latency = ask_image_question(temp_img_path, user_q)
                st.write(f"**Answer:** {ans}")
                st.caption(f"Latency: {latency}s")

        with col2:
            if st.button("Extract Fit Data"):
                fit_data, latency = extract_image_data(temp_img_path, FitCheckAnalysis, "Analyze this outfit")
                st.subheader("Style Breakdown")
                st.write(f"**Vibe:** {fit_data.aesthetic_vibe}")
                st.write(f"**Palette:** {', '.join(fit_data.color_palette)}")
                st.json(fit_data.model_dump())
                st.caption(f"Extraction Latency: {latency}s")

with tab2:
    st.header("Audio Transcript & Voice Notes")
    uploaded_audio = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a"])
    
    if uploaded_audio:
        temp_aud_path = f"temp_{uploaded_audio.name}"
        with open(temp_aud_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())
        
        st.audio(temp_aud_path)
        
        if st.button("Process Audio Pipeline"):
            with st.spinner("Transcribing & Summarizing..."):
                transcript, t_lat = transcribe_audio(temp_aud_path)
                summary, s_lat = summarize_transcript(transcript)
                audio_file, tts_lat = text_to_speech(summary.summary, "response.mp3")
                
                st.subheader("Transcript")
                st.write(transcript)
                
                st.subheader("Structured Meeting Notes")
                st.json(summary.model_dump())
                
                st.subheader("Audio Response")
                st.audio(audio_file)
                
                st.caption(f"Latency Breakdown — Transcribe: {t_lat}s | Summarize: {s_lat}s | TTS: {tts_lat}s | Total: {round(t_lat+s_lat+tts_lat, 2)}s")