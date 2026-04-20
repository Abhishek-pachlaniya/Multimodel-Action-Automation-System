import speech_recognition as sr
from groq import Groq
from dotenv import dotenv_values
import os

# === Load environment variables ===
env_vars = dotenv_values(".env")
client = Groq(api_key=env_vars.get("GroqAPIKey"))
InputLanguage = env_vars.get("InputLanguage", "en") 

# === Function to properly punctuate the query ===
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can", "what's", "where's", "how's"]

    if any(word in query_words for word in question_words):
        if not new_query.endswith(('.', '?', '!')):
            new_query += "?"
    else:
        if not new_query.endswith(('.', '?', '!')):
            new_query += "."

    return new_query.capitalize()

# === Superfast Speech to Text using Groq Whisper API ===
def SpeechRecognition():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        r.pause_threshold = 0.5 
        print("\nListening...")
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"Microphone error: {e}")
            return ""

    temp_file = "temp_audio.wav"
    with open(temp_file, "wb") as f:
        f.write(audio.get_wav_data())

    try:
        with open(temp_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_file, file.read()),
                model="whisper-large-v3",
                language="en" 
            )
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        text = transcription.text.strip()
        
        # === WHISPER HALLUCINATION FILTER ===
        # Ye filter background noise se banne wale fake words ko block karega
        ignore_phrases = ["thank you", "thank you.", "thanks", "thanks.", "hello", "hello.", "hi", "hi.", "bye", "bye."]
        if text.lower() in ignore_phrases or len(text) <= 3:
            return ""
        # ====================================

        if text:
            return QueryModifier(text)
        return ""
        
    except Exception as e:
        print(f"STT Error: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return ""

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text:
            print("Recognized:", Text)