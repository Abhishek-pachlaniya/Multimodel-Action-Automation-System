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

# ── Core backends ──────────────────────────────────────────────────────────────
from backend.Model               import FastRouter          # upgraded: local trie first
from backend.RealtimeSearchEngine import RealtimeSearchEngine
from backend.Automation           import Automation
from backend.SpeechToText         import SpeechRecognition
from backend.Chatbot              import ChatBot
from backend.TextToSpeech         import TextToSpeech
from backend.Agent                import AgenticBrain

# ── New feature backends (imported lazily inside functions to save boot time) ──
# backend.Reminder, backend.Weather, backend.ScreenshotAnalysis,
# backend.Messaging, backend.FileManagement

from dotenv import dotenv_values
from asyncio import run
from time   import sleep
import subprocess
import threading
import json
import os
import sys

# ── Env vars ───────────────────────────────────────────────────────────────────
env_vars      = dotenv_values(".env")
Username      = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

DefaultMessage = (
    f"{Username} : Hello {Assistantname}, How are you?\n"
    f"{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"
)

# ── ALL commands that Automation / direct-call can handle ──────────────────────
# (FastRouter returns these prefixes; Main.py routes accordingly)
AUTOMATION_SILENT = [          # execute only, no spoken response
    "open", "close", "play",
    "system", "volume", "mute", "unmute",
    "content", "google search", "youtube search",
    "start handgesture", "stop handgesture",
    "generate image",
]

AUTOMATION_RESPONSE = [        # execute AND return a text response to speak
    "reminder",
    "weather",
    "screenshot analysis",
    "send whatsapp",
    "send email",
    "file management",
]

# Phrases that are almost certainly Whisper hallucinations or trivial fillers
_IGNORE = {
    "thank you", "thanks", "you're welcome",
    "hello", "hi", "hey", "bye", "goodbye",
    "okay", "ok", "sure", "yeah", "yes", "no",
    "hmm", "um", "uh",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_noise(query: str) -> bool:
    """Return True if the query is too short or a filler phrase to act on."""
    clean = query.lower().strip(".!?,").strip()
    return len(clean) <= 2 or clean in _IGNORE


def _show_and_speak(response: str):
    """Update GUI and play TTS for a given response string."""
    if not response:
        return
    ShowTextToScreen(f"{Assistantname} : {response}")
    SetAssistantStatus("Answering...")
    TextToSpeech(response)


# ── Response-generating automation (called directly, returns text) ─────────────

def _run_response_command(command: str) -> str:
    """
    For commands that need to return a text answer (weather, reminder, etc.),
    call the relevant backend directly and return the result string.
    """
    cmd = command.lower().strip()

    # reminder
    if cmd.startswith("reminder "):
        try:
            from backend.Reminder import AddReminder
            return AddReminder(command[len("reminder "):])
        except Exception as e:
            return f"Reminder error: {e}"

    # weather
    elif cmd.startswith("weather "):
        try:
            from backend.Weather import GetWeather
            return GetWeather(command[len("weather "):].strip())
        except Exception as e:
            return f"Weather error: {e}"

    # screenshot analysis
    elif cmd.startswith("screenshot analysis"):
        try:
            from backend.ScreenshotAnalysis import AnalyzeScreen
            question = command[len("screenshot analysis"):].strip()
            return AnalyzeScreen(question or "What is on this screen? Describe it.")
        except Exception as e:
            return f"Screenshot error: {e}"

    # whatsapp
    elif cmd.startswith("send whatsapp "):
        try:
            from backend.Messaging import SendWhatsApp
            return SendWhatsApp(command[len("send whatsapp "):])
        except Exception as e:
            return f"WhatsApp error: {e}"

    # email
    elif cmd.startswith("send email "):
        try:
            from backend.Messaging import SendEmail
            return SendEmail(command[len("send email "):])
        except Exception as e:
            return f"Email error: {e}"

    # file management
    elif cmd.startswith("file management "):
        try:
            from backend.FileManagement import FileManagement
            return FileManagement(command[len("file management "):])
        except Exception as e:
            return f"File management error: {e}"

    return ""


# ── GUI helpers ────────────────────────────────────────────────────────────────

def ShowDefaultChatIfNoChats():
    chatlog_path = r"Data\ChatLog.json"
    if os.path.exists(chatlog_path) and os.path.getsize(chatlog_path) < 5:
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as f:
            f.write("")
        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as f:
            f.write(DefaultMessage)


def ReadChatLogJson():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as f:
        return json.load(f)


def ChatLogIntegration():
    try:
        json_data = ReadChatLogJson()
        formatted = ""
        for entry in json_data:
            role = Username if entry["role"] == "user" else Assistantname
            formatted += f"{role} : {entry['content']}\n"
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as f:
            f.write(AnswerModifier(formatted))
    except Exception:
        pass


def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as f:
            data = f.read()
        if data:
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as f:
                f.write(data)
    except Exception:
        pass


# ── Startup ────────────────────────────────────────────────────────────────────

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

    # Restore any reminders saved from previous sessions
    try:
        from backend.Reminder import RestoreReminders
        RestoreReminders()
        print("[Startup] Reminders restored.")
    except Exception as e:
        print(f"[Startup] Could not restore reminders: {e}")


InitialExecution()


# ── MAIN EXECUTION (called on every mic trigger) ───────────────────────────────

def MainExecution():
    # ── 1. Listen ─────────────────────────────────────────────────────────────
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()

    if not Query or _is_noise(Query):
        SetAssistantStatus("Available...")
        return

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Processing...")

    # ── 2. Classify query via FastRouter ──────────────────────────────────────
    # FastRouter returns a list like:
    #   ['open chrome']
    #   ['general how are you?']
    #   ['realtime who is pm of india']
    #   ['weather delhi', 'open spotify']
    #   ['reminder 9pm take medicine']
    try:
        commands = FastRouter(Query)
    except Exception as e:
        print(f"FastRouter error: {e}")
        commands = [f"general {Query}"]

    if not commands:
        SetAssistantStatus("Available...")
        return

    # ── 3. Handle 'exit' ──────────────────────────────────────────────────────
    if "exit" in commands:
        farewell = f"Goodbye {Username}. Have a great day!"
        _show_and_speak(farewell)
        sleep(2)
        os._exit(0)

    # ── 4. Separate commands by type ──────────────────────────────────────────
    general_queries  = []   # → ChatBot
    realtime_queries = []   # → RealtimeSearchEngine
    silent_cmds      = []   # → Automation (fire-and-forget)
    response_cmds    = []   # → direct backend call (returns text)
    agentic_needed   = False

    for cmd in commands:
        cmd_lower = cmd.lower().strip()

        if cmd_lower.startswith("general "):
            general_queries.append(cmd[len("general "):].strip())

        elif cmd_lower.startswith("realtime "):
            realtime_queries.append(cmd[len("realtime "):].strip())

        elif any(cmd_lower.startswith(pfx) for pfx in AUTOMATION_RESPONSE):
            response_cmds.append(cmd)

        elif any(cmd_lower.startswith(pfx) for pfx in AUTOMATION_SILENT):
            silent_cmds.append(cmd)

        else:
            # Unrecognised — let AgenticBrain handle it
            agentic_needed = True

    # ── 5. Execute silent automation (open/close/play/volume etc.) ────────────
    if silent_cmds:
        try:
            SetAssistantStatus("Executing...")
            run(Automation(silent_cmds))
        except Exception as e:
            print(f"Automation error: {e}")

    # ── 6. Execute response-generating automation (weather/reminder etc.) ─────
    for cmd in response_cmds:
        try:
            prefix = next(p for p in AUTOMATION_RESPONSE if cmd.lower().startswith(p))
            SetAssistantStatus(f"Working on {prefix}...")
            result = _run_response_command(cmd)
            if result:
                _show_and_speak(result)
        except Exception as e:
            _show_and_speak(f"Sorry, I couldn't complete that. {e}")

    # ── 7. General chat (ChatBot) ──────────────────────────────────────────────
    for q in general_queries:
        try:
            SetAssistantStatus("Thinking...")
            response = ChatBot(q)
            _show_and_speak(response)
        except Exception as e:
            _show_and_speak(f"ChatBot error: {e}")

    # ── 8. Realtime search (RealtimeSearchEngine) ─────────────────────────────
    for q in realtime_queries:
        try:
            SetAssistantStatus("Searching...")
            response = RealtimeSearchEngine(q)
            _show_and_speak(response)
        except Exception as e:
            _show_and_speak(f"Search error: {e}")

    # ── 9. Fallback: complex / unclassified → AgenticBrain ────────────────────
    # AgenticBrain is used ONLY when FastRouter couldn't classify the query.
    # This avoids the extra LLM call for every simple command.
    if agentic_needed and not (general_queries or realtime_queries or
                                silent_cmds or response_cmds):
        try:
            SetAssistantStatus("Thinking deeply...")
            response = AgenticBrain(Query)
            _show_and_speak(response)
        except Exception as e:
            _show_and_speak(f"I faced a glitch: {e}")

    SetAssistantStatus("Available...")


# ── Threads ────────────────────────────────────────────────────────────────────

def FirstThread():
    """Mic listener loop — runs on a background thread."""
    while True:
        try:
            if GetMicrophoneStatus() == "True":
                MainExecution()
            else:
                if "Available..." not in GetAssistantStatus():
                    SetAssistantStatus("Available...")
                sleep(0.1)
        except Exception as e:
            print(f"[FirstThread] Error: {e}")
            SetAssistantStatus("Available...")
            sleep(0.5)


def SecondThread():
    """GUI loop — runs on the main thread."""
    GraphicalUserInterface()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start ImageGeneration background service
    try:
        subprocess.Popen(
            [sys.executable, r"backend\ImageGeneration.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=False
        )
        print("[Startup] ImageGeneration service started.")
    except Exception as e:
        print(f"[Startup] Could not start ImageGeneration: {e}")

    # Mic listener on background thread
    mic_thread = threading.Thread(target=FirstThread, daemon=True)
    mic_thread.start()

    # GUI on main thread (blocking)
    SecondThread()
