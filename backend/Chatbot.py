from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]
chatlog_path = r"Data\chatLog.json"

# -------------------------------------------------------
# FIX: Load messages ONCE at startup into memory.
# No more disk read on every ChatBot() call.
# -------------------------------------------------------
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(chatlog_path, "w") as f:
        dump([], f)

# Keep chat history to last N turns to avoid token overflow
MAX_HISTORY = 20


def _trim_history():
    """Keep only the last MAX_HISTORY messages in memory."""
    global messages
    if len(messages) > MAX_HISTORY:
        messages = messages[-MAX_HISTORY:]


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day    = current_date_time.strftime("%A")
    date   = current_date_time.strftime("%d")
    month  = current_date_time.strftime("%B")
    year   = current_date_time.strftime("%Y")
    hour   = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data  = "Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def ChatBot(Query):
    global messages
    try:
        messages.append({"role": "user", "content": f"{Query}"})
        _trim_history()

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
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

        # -------------------------------------------------------
        # FIX: Write to disk only after getting the answer,
        # not before. Also wrapped in try so a disk error
        # doesn't crash the whole response.
        # -------------------------------------------------------
        try:
            with open(chatlog_path, "w") as f:
                dump(messages, f, indent=4)
        except Exception as disk_err:
            print(f"[Warning] Could not save chat log: {disk_err}")

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"ChatBot Error: {e}")
        return "I encountered an error, please try again."


def ClearHistory():
    """Call this to wipe chat history (useful for 'start fresh' command)."""
    global messages
    messages = []
    try:
        with open(chatlog_path, "w") as f:
            dump([], f)
        return "Chat history cleared."
    except Exception as e:
        return f"Could not clear history: {e}"


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ("clear", "reset"):
            print(ClearHistory())
        else:
            print(ChatBot(user_input))
