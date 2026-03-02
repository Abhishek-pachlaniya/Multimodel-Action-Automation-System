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
YouTubeMode = False
HandGestureProcess = None
# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define CSS classes
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

# User agent
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters,codes,applications,essays,notes,songs,poems etc."}
]

# Google search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Content generation
def Content(Topic):

    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

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

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    with open(f"Data/{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(f"Data/{Topic.lower().replace(' ', '')}.txt")
    return True



# YouTube Search
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    global YouTubeMode

    search_url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(search_url, new=0)
    time.sleep(5)

    pyautogui.press("tab", presses=3)
    pyautogui.press("enter")

    YouTubeMode = True
    return True

def OpenApp(app, sess=requests.session()):
    app = app.lower()

    web_apps = {
        "instagram": "https://www.instagram.com",
        "whatsapp": "https://web.whatsapp.com",
        "chatgpt": "https://chat.openai.com",
        "youtube": "https://youtube.com"
    }

    # web apps → browser
    if app in web_apps:
        webbrowser.open(web_apps[app])
        return True

    # desktop apps → system open
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


def System(command):
     
    command = command.lower().strip().replace(".", "")

    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up(cmd):
        number = re.findall(r'\d+', cmd)

        if number:
            steps = int(number[0])
        else:
            steps = 5   # default steps

        for i in range(steps):
            keyboard.press_and_release("volume up")
            time.sleep(0.05)

    def volume_down(cmd):
        number = re.findall(r'\d+', cmd)

        if number:
            steps = int(number[0])
        else:
            steps = 5   # default steps

        for i in range(steps):
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

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        command = command.lower().strip()
        if command.startswith("open "):

            if "open it" in command:
                pass

            elif "open file" == command:
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

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

        elif command.startswith(("volume","mute","unmute","system")):
            command = command.replace("system ","")
            fun = asyncio.to_thread(System, command)
            funcs.append(fun)
        elif "start" in command and "gesture" in command:
            fun = asyncio.to_thread(StartHandGesture)
            funcs.append(fun)
        elif "stop" in command and "gesture" in command:
            fun = asyncio.to_thread(StopHandGesture)
            funcs.append(fun)
        
        else:
            print(f"No Function Found. For {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass

    return True