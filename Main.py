from frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from backend.Model import FirstLayerDMM
from backend.RealtimeSearchEngine import RealtimeSearchEngine
from backend.Automation import Automation
from backend.SpeechToText import SpeechRecognition
from backend.Chatbot import ChatBot
from backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
from backend.Agent import AgenticBrain

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''

Functions = [
    "open", "close", "play", "system", "volume", "mute", 
    "unmute", "content", "google search", "youtube search", 
    "start handgesture", "stop handgesture"
]

def ShowDefaultChatIfNoChats():
    chatlog_path = r'Data\ChatLog.json'
    if os.path.exists(chatlog_path) and os.path.getsize(chatlog_path) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    try:
        json_data = ReadChatLogJson()
        formatted_chatlog = ""
        for entry in json_data:
            role = Username if entry["role"] == "user" else Assistantname
            formatted_chatlog += f"{role} : {entry['content']}\n"

        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception:
        pass

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            Data = file.read()
        if Data:
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(Data)
    except Exception:
        pass

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    
    # Fast-exit agar user ne kuch nahi bola
    if not Query:
        SetAssistantStatus("Available...")
        return

    # === ANTI-LOOP & HALLUCINATION FILTER ===
    # Punctuation hata kar check karenge taaki exact match ho
    clean_query = Query.lower().replace(".", "").replace("!", "").replace("?", "").strip()
    ignore_phrases = ["thank you", "thanks", "you're welcome", "hello", "hi", "bye", "okay", "ok"]
    
    # Agar query ignore list mein hai ya bohot choti hai, toh chup raho
    if clean_query in ignore_phrases or len(clean_query) <= 2:
        SetAssistantStatus("Available...")
        return
    # ========================================

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Processing...")
    
    # Ab Agent decide karega automation aur chatting dono
    FinalResponse = AgenticBrain(Query) 
    
    ShowTextToScreen(f"{Assistantname} : {FinalResponse}")
    SetAssistantStatus("Answering...")
    TextToSpeech(FinalResponse)
    
    
def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." not in AIStatus:
                SetAssistantStatus("Available...")
            sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    # Background service ek hi baar start hogi (No infinite RAM usage)
    try:
        subprocess.Popen(['python', r'backend\ImageGeneration.py'], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                         stdin=subprocess.PIPE, shell=False)
    except Exception as e:
        print(f"Error starting background image generation: {e}")

    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()