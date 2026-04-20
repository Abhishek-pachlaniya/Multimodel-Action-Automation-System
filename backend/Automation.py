# Import required libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import pyautogui
import time
import re
import sys

YouTubeMode       = False
HandGestureProcess = None

# -------------------------------------------------------
# FIX: Track mute state so mute/unmute actually work
# -------------------------------------------------------
_is_muted = False

env_vars   = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW",
    "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc", "O5uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe",
    "LWkfKe", "VQF4g", "qv3Wpe",
    "kno-rdesc", "SPZ6b"
]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
client    = Groq(api_key=GroqAPIKey)

messages = []

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters,codes,applications,essays,notes,songs,poems etc."}
]


# -------------------------------------------------------
# Google Search
# -------------------------------------------------------
def GoogleSearch(Topic):
    search(Topic)
    return True


# -------------------------------------------------------
# Content Generation
# -------------------------------------------------------
def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(["notepad.exe", File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic        = Topic.replace("Content ", "")
    ContentByAI  = ContentWriterAI(Topic)
    safe_name    = Topic.lower().replace(' ', '')[:50]  # cap filename length

    os.makedirs("Data", exist_ok=True)
    filepath = f"Data/{safe_name}.txt"

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filepath)
    return True


# -------------------------------------------------------
# YouTube
# -------------------------------------------------------
def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True


def PlayYoutube(query):
    global YouTubeMode
    clean_query = query.replace("youtube", "").strip()
    try:
        # Step 1: YouTube par search karke open karna
        playonyt(clean_query) 
        
        # Step 2: Pehla Enter click (agar zarurat ho, waise playonyt search results kholta hai)
        time.sleep(2) # Browser khulne ka wait
        pyautogui.press('enter')
        
        # Step 3: 5 second ka wait jo tune bola
        print("Waiting for 5 seconds before second Enter...")
        time.sleep(5) 
        
        # Step 4: Doosra Enter click (taki video play ho jaye)
        pyautogui.press('enter')
        
        YouTubeMode = True
        return True
    except Exception as e:
        print(f"Error playing youtube video: {e}")
        return False


# -------------------------------------------------------
# App opener
# -------------------------------------------------------
def OpenApp(app, sess=requests.session()):
    app = app.lower().strip()
    web_apps = {
        "instagram": "https://www.instagram.com",
        "whatsapp":  "https://web.whatsapp.com",
        "chatgpt":   "https://chat.openai.com",
        "youtube":   "https://youtube.com",
        "gmail":     "https://mail.google.com",
        "google":    "https://www.google.com",
        "maps":      "https://maps.google.com",
    }
    if app in web_apps:
        webbrowser.open(web_apps[app])
        return True
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        webbrowser.open(f"https://www.google.com/search?q={app}")
        return True


def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False


# -------------------------------------------------------
# System controls — FIX: mute/unmute now use state
# -------------------------------------------------------
def System(command):
    global _is_muted
    command = command.lower().strip().replace(".", "")

    def mute():
        global _is_muted
        if not _is_muted:
            keyboard.press_and_release("volume mute")
            _is_muted = True

    def unmute():
        global _is_muted
        if _is_muted:
            keyboard.press_and_release("volume mute")
            _is_muted = False

    def volume_up(cmd):
        steps = int(n[0]) if (n := re.findall(r'\d+', cmd)) else 5
        for _ in range(steps):
            keyboard.press_and_release("volume up")
            time.sleep(0.05)

    def volume_down(cmd):
        steps = int(n[0]) if (n := re.findall(r'\d+', cmd)) else 5
        for _ in range(steps):
            keyboard.press_and_release("volume down")
            time.sleep(0.05)

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command.startswith("volume up"):
        volume_up(command)
    elif command.startswith("volume down"):
        volume_down(command)

    return True


# -------------------------------------------------------
# Hand Gesture
# -------------------------------------------------------
def StartHandGesture():
    global HandGestureProcess
    if HandGestureProcess and HandGestureProcess.poll() is None:
        print("Already Running")
        return True
    path = os.path.join(os.path.dirname(__file__), "HandGesture.py")
    HandGestureProcess = subprocess.Popen([sys.executable, path])
    print("HandGesture Started")
    return True


def StopHandGesture():
    global HandGestureProcess
    if HandGestureProcess and HandGestureProcess.poll() is None:
        HandGestureProcess.terminate()
        HandGestureProcess.wait()
        HandGestureProcess = None
        print("HandGesture Stopped")
    else:
        print("Not Running")
    return True


# -------------------------------------------------------
# NEW: Reminder wrapper
# -------------------------------------------------------
def SetReminder(reminder_text: str):
    try:
        from backend.Reminder import AddReminder
        return AddReminder(reminder_text)
    except Exception as e:
        return f"Reminder error: {e}"


# -------------------------------------------------------
# NEW: Weather wrapper
# -------------------------------------------------------
def GetWeather(city: str):
    try:
        from backend.Weather import GetWeather as _GetWeather
        return _GetWeather(city)
    except Exception as e:
        return f"Weather error: {e}"


# -------------------------------------------------------
# NEW: Screenshot Analysis wrapper
# -------------------------------------------------------
def ScreenshotAnalysis(question: str = "What is on this screen?"):
    try:
        from backend.ScreenshotAnalysis import AnalyzeScreen
        return AnalyzeScreen(question)
    except Exception as e:
        return f"Screenshot analysis error: {e}"


# -------------------------------------------------------
# NEW: Send WhatsApp wrapper
# -------------------------------------------------------
def SendWhatsApp(command: str):
    try:
        from backend.Messaging import SendWhatsApp as _SendWhatsApp
        return _SendWhatsApp(command)
    except Exception as e:
        return f"WhatsApp error: {e}"


# -------------------------------------------------------
# NEW: Send Email wrapper
# -------------------------------------------------------
def SendEmail(command: str):
    try:
        from backend.Messaging import SendEmail as _SendEmail
        return _SendEmail(command)
    except Exception as e:
        return f"Email error: {e}"


# -------------------------------------------------------
# NEW: File Management wrapper
# -------------------------------------------------------
def ManageFiles(command: str):
    try:
        from backend.FileManagement import FileManagement
        return FileManagement(command)
    except Exception as e:
        return f"File management error: {e}"


# -------------------------------------------------------
# Async command dispatcher
# -------------------------------------------------------
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        command = command.lower().strip()

        if command.startswith("open "):
            if "open it" in command or command == "open file":
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith(("volume", "mute", "unmute", "system")):
            command = command.replace("system ", "")
            fun = asyncio.to_thread(System, command)
            funcs.append(fun)

        elif "start" in command and "gesture" in command:
            fun = asyncio.to_thread(StartHandGesture)
            funcs.append(fun)

        elif "stop" in command and "gesture" in command:
            fun = asyncio.to_thread(StopHandGesture)
            funcs.append(fun)

        elif command.startswith("reminder "):
            reminder_text = command.removeprefix("reminder ")
            fun = asyncio.to_thread(SetReminder, reminder_text)
            funcs.append(fun)

        elif command.startswith("weather "):
            city = command.removeprefix("weather ")
            fun = asyncio.to_thread(GetWeather, city)
            funcs.append(fun)

        elif command == "screenshot analysis" or command.startswith("screenshot analysis "):
            question = command.removeprefix("screenshot analysis").strip() or "What is on this screen?"
            fun = asyncio.to_thread(ScreenshotAnalysis, question)
            funcs.append(fun)

        elif command.startswith("send whatsapp "):
            fun = asyncio.to_thread(SendWhatsApp, command.removeprefix("send whatsapp "))
            funcs.append(fun)

        elif command.startswith("send email "):
            fun = asyncio.to_thread(SendEmail, command.removeprefix("send email "))
            funcs.append(fun)

        elif command.startswith("file management "):
            fun = asyncio.to_thread(ManageFiles, command.removeprefix("file management "))
            funcs.append(fun)

        elif command.startswith("general ") or command.startswith("realtime "):
            pass  # handled by main loop

        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
