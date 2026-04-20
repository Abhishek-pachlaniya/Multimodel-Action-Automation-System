import requests
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username      = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey    = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# -------------------------------------------------------
# FIX: Load messages ONCE at startup (same as Chatbot.py)
# -------------------------------------------------------
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

MAX_HISTORY = 20

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]


def GoogleSearch(query):
    try:
        url = "https://google.serper.dev/search"
        payload = {"q": query}
        headers = {
            "X-API-KEY": env_vars.get("SERPER_API_KEY"),
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=8)
        data = response.json()

        Answer = f"The search results for '{query}' are:\n[start]\n"
        for result in data.get("organic", [])[:5]:
            Answer += f"Title: {result.get('title','')}\nDescription: {result.get('snippet','')}\n\n"
        Answer += "[end]"
        return Answer

    except Exception as e:
        return f"[Search Error]: {str(e)}"


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def Information():
    current_date_time = datetime.datetime.now()
    data  = "Use This Real-time Information if needed:\n"
    data += f"Day: {current_date_time.strftime('%A')}\n"
    data += f"Date: {current_date_time.strftime('%d')}\n"
    data += f"Month: {current_date_time.strftime('%B')}\n"
    data += f"Year: {current_date_time.strftime('%Y')}\n"
    data += f"Time: {current_date_time.strftime('%H')} hours, {current_date_time.strftime('%M')} minutes, {current_date_time.strftime('%S')} seconds.\n"
    return data


def RealtimeSearchEngine(prompt):
    global messages

    # -------------------------------------------------------
    # FIX: Use try/finally so SystemChatBot.pop() ALWAYS
    # runs — even if Groq API throws an exception.
    # This prevents the list from growing unboundedly.
    # -------------------------------------------------------
    search_result = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_result})

    try:
        messages.append({"role": "user", "content": f"{prompt}"})

        # Trim history to avoid token overflow
        if len(messages) > MAX_HISTORY:
            messages = messages[-MAX_HISTORY:]

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        try:
            with open(r"Data\ChatLog.json", "w") as f:
                dump(messages, f, indent=4)
        except Exception as disk_err:
            print(f"[Warning] Could not save chat log: {disk_err}")

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"RealtimeSearchEngine Error: {e}")
        return "I encountered an error while searching. Please try again."

    finally:
        # ALWAYS remove the search result we appended — no leaks
        if len(SystemChatBot) > 3:
            SystemChatBot.pop()


if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
