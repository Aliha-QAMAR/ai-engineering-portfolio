import os
from vision import extract_image_data, ask_image_question
from transcribe import transcribe_audio
from summarize import summarize_transcript
from speak import text_to_speech
from schemas import FitCheckAnalysis

def run_evaluations():
    test_images = ["test1.jpg", "test2.jpg", "test3.jpg"]
    test_audios = ["sample1.mp3", "sample2.mp3"]

    print("=== MULTIMODAL EVALUATION REPORT ===")
    
    image_latencies = []
    for img in test_images:
        if os.path.exists(img):
            _, latency = extract_image_data(img, FitCheckAnalysis, "Analyze fit check")
            image_latencies.append(latency)
            print(f"Image {img} structured extraction latency: {latency}s")
        else:
            print(f"Image {img} missing, skipping...")

    audio_latencies = []
    for aud in test_audios:
        if os.path.exists(aud):
            transcript, t_lat = transcribe_audio(aud)
            summary, s_lat = summarize_transcript(transcript)
            audio_latencies.append(t_lat + s_lat)
            print(f"Audio {aud} total processing latency: {round(t_lat + s_lat, 2)}s")
            print(f"Valid action items count: {len(summary.action_items)}")
        else:
            print(f"Audio {aud} missing, skipping...")

    if image_latencies:
        print(f"Avg Image Latency: {round(sum(image_latencies)/len(image_latencies), 2)}s")
    if audio_latencies:
        print(f"Avg Audio Latency: {round(sum(audio_latencies)/len(audio_latencies), 2)}s")

if __name__ == "__main__":
    run_evaluations()