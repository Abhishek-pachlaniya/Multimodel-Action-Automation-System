import cohere
from rich import print
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
co = cohere.Client(api_key=CohereAPIKey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "start handgesture",
    "stop handgesture", "send email", "send whatsapp",
    "weather", "file management", "screenshot analysis"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'start handgesture' if user wants to start hand gesture.
-> Respond with 'stop handgesture' if user wants to stop hand gesture.
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
-> Respond with 'send email (recipient and message)' if a query is asking to send an email.
-> Respond with 'send whatsapp (recipient and message)' if a query is asking to send a whatsapp message.
-> Respond with 'weather (city name)' if a query is asking about weather of any city.
-> Respond with 'file management (task description)' if a query is asking to manage files like move, copy, delete, rename, organize files/folders.
-> Respond with 'screenshot analysis' if a query is asking to analyze what's on the screen or take a screenshot and describe it.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

chatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that I have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "what's the weather in delhi?"},
    {"role": "Chatbot", "message": "weather delhi"},
    {"role": "User", "message": "send whatsapp to mom that I'll be late"},
    {"role": "Chatbot", "message": "send whatsapp mom I'll be late"},
    {"role": "User", "message": "what's on my screen?"},
    {"role": "Chatbot", "message": "screenshot analysis"},
]

# ============================================================
# ENHANCED FAST ROUTER
# Zero latency for 90%+ queries — no API call needed
# ============================================================

# Keyword trie / prefix maps for instant local routing
_OPEN_PREFIXES    = ("open ",)
_CLOSE_PREFIXES   = ("close ",)
_PLAY_PREFIXES    = ("play ",)
_CONTENT_PREFIXES = ("content ", "write ", "draft ", "compose ")
_GOOGLE_PREFIXES  = ("google search ", "search on google ")
_YT_PREFIXES      = ("youtube search ", "search on youtube ", "search youtube ")
_IMAGE_PREFIXES   = ("generate image ", "create image ", "make image ", "draw ")
_WEATHER_PREFIXES = ("weather in ", "weather of ", "weather ")
_FILE_PREFIXES    = ("move file", "delete file", "rename file", "organize file",
                     "copy file", "move folder", "delete folder", "file management")
_EMAIL_PREFIXES   = ("send email", "email to", "mail to")
_WA_PREFIXES      = ("send whatsapp", "whatsapp to", "message on whatsapp")
_SCREENSHOT_KW    = ("what's on my screen", "what is on my screen", "analyze screen",
                     "screenshot analysis", "describe my screen", "read my screen")

_EXACT_COMMANDS = {
    "start handgesture": "start handgesture",
    "stop handgesture":  "stop handgesture",
    "exit": "exit", "bye": "exit", "quit": "exit",
    "mute": "system mute", "unmute": "system unmute",
}

_VOLUME_PREFIXES = ("volume up", "volume down")

_SYSTEM_KW = ("mute", "unmute", "volume")


def FastRouter(prompt: str):
    """
    Tries to classify prompt locally with zero latency.
    Falls back to Cohere only for ambiguous / complex queries.
    """
    p = prompt.lower().strip()

    # --- exact matches ---
    if p in _EXACT_COMMANDS:
        return [_EXACT_COMMANDS[p]]

    # --- volume / system controls ---
    for pfx in _VOLUME_PREFIXES:
        if p.startswith(pfx):
            return [f"system {p}"]

    # --- open / close ---
    for pfx in _OPEN_PREFIXES:
        if p.startswith(pfx):
            return [p]  # e.g. "open chrome"
    for pfx in _CLOSE_PREFIXES:
        if p.startswith(pfx):
            return [p]

    # --- play ---
    for pfx in _PLAY_PREFIXES:
        if p.startswith(pfx):
            return [p]

    # --- content writing ---
    for pfx in _CONTENT_PREFIXES:
        if p.startswith(pfx):
            topic = p[len(pfx):]
            return [f"content {topic}"]

    # --- google / youtube search ---
    for pfx in _GOOGLE_PREFIXES:
        if p.startswith(pfx):
            return [p]
    for pfx in _YT_PREFIXES:
        if p.startswith(pfx):
            topic = p.split("youtube", 1)[-1].strip().lstrip("search").strip()
            return [f"youtube search {topic}"]

    # --- image generation ---
    for pfx in _IMAGE_PREFIXES:
        if p.startswith(pfx):
            desc = p[len(pfx):]
            return [f"generate image {desc}"]

    # --- weather ---
    for pfx in _WEATHER_PREFIXES:
        if p.startswith(pfx):
            city = p[len(pfx):].strip()
            return [f"weather {city}"]

    # --- file management ---
    for kw in _FILE_PREFIXES:
        if kw in p:
            return [f"file management {prompt}"]

    # --- email ---
    for pfx in _EMAIL_PREFIXES:
        if p.startswith(pfx):
            return [f"send email {prompt[len(pfx):].strip()}"]

    # --- whatsapp ---
    for pfx in _WA_PREFIXES:
        if p.startswith(pfx):
            return [f"send whatsapp {prompt[len(pfx):].strip()}"]

    # --- screenshot analysis ---
    for kw in _SCREENSHOT_KW:
        if kw in p:
            return ["screenshot analysis"]

    # --- reminder (simple pattern) ---
    if any(w in p for w in ("remind me", "set a reminder", "reminder at", "alarm at")):
        return FirstLayerDMM(prompt)  # Let Cohere parse the datetime properly

    # --- handgesture ---
    if "start" in p and "gesture" in p:
        return ["start handgesture"]
    if "stop" in p and "gesture" in p:
        return ["stop handgesture"]

    # --- greetings / farewells (instant general) ---
    _greetings = ("hi", "hello", "hey", "good morning", "good evening",
                  "good night", "thanks", "thank you", "okay", "ok", "sure",
                  "got it", "nice", "cool", "great", "awesome")
    if p in _greetings or p.rstrip("!.").strip() in _greetings:
        return [f"general {prompt}"]

    # --- everything else → Cohere ---
    return FirstLayerDMM(prompt)


def FirstLayerDMM(prompt: str = "test"):
    try:
        response = co.chat(
            model='command-r-08-2024',
            message=prompt,
            temperature=0.0,
            chat_history=chatHistory,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )

        raw_output = response.text
        result = raw_output.replace("\n", "").split(",")
        result = [i.strip() for i in result]

        temp = []
        for task in result:
            for func in funcs:
                if task.startswith(func + " ") or task == func:
                    temp.append(task)

        if "(query)" in raw_output:
            return FirstLayerDMM(prompt=prompt)
        else:
            return temp if temp else [f"general {prompt}"]

    except Exception as e:
        print(f"Error in FirstLayerDMM: {e}")
        return [f"general {prompt}"]


if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        print(FastRouter(user_input))
