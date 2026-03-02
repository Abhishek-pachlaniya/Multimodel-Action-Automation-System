# === Import Required Libraries ===
import pygame                              # For handling audio playback
import random                              # For random selection of responses
import asyncio                             # For asynchronous operations
import edge_tts                            # For text-to-speech conversion
import os                                  # For file handling
from dotenv import dotenv_values           # For reading environment variables

# === Load Environment Variables ===
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Voice name from .env


# === Asynchronous Function to Convert Text to Audio File ===
async def TextToAudioFile(text) -> None:
   file_path = r"data\speech.mp3"  # Path where the speech file will be saved

   # If file already exists, remove it
   if os.path.exists(file_path):
       os.remove(file_path)

   # Create communicate object for TTS
   communicate = edge_tts.Communicate(
       text,
       AssistantVoice,
       pitch="+5Hz",
       rate="+13%"
   )

   # Save generated speech as MP3 file
   await communicate.save(file_path)


# === Text-to-Speech Playback Function ===
def TTS(Text, func=lambda r=None: True):
   while True:
       try:
           # Convert text to speech asynchronously
           asyncio.run(TextToAudioFile(Text))

           # Initialize pygame mixer
           pygame.mixer.init()

           # Load and play generated speech
           pygame.mixer.music.load(r"data\speech.mp3")
           pygame.mixer.music.play()

           # Wait until audio finishes or external function stops it
           while pygame.mixer.music.get_busy():
               if func() == False:
                   break
               pygame.time.Clock().tick(10)

           return True

       except Exception as e:
           print(f"Error in TTS: {e}")

       finally:
           try:
               # Signal end of TTS
               func(False)

               # Stop and quit mixer
               pygame.mixer.music.stop()
               pygame.mixer.quit()

           except Exception as e:
               print(f"Error in finally block: {e}")


# === Function to Manage Long Text and Add Extra Response ===
def TextToSpeech(Text, func=lambda r=None: True):
   Data = str(Text).split(".")  # Split text into sentences

   # Predefined responses for long text
   responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]


   # If text is long (>4 sentences and >250 characters)
   if len(Data) > 4 and len(Text) > 250:
       TTS(".".join(Text.split(".")[:2]) + "." + random.choice(responses), func)
   else:
       TTS(Text, func)


# === Main Execution ===
if __name__ == "__main__":
   while True:
       TextToSpeech(input("Enter the text: "))
