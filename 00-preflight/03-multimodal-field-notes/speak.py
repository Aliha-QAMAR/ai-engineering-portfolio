import time
from gtts import gTTS

def text_to_speech(text: str, output_path: str = "output.mp3") -> tuple[str, float]:
    start_time = time.time()
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    latency = round(time.time() - start_time, 2)
    return output_path, latency