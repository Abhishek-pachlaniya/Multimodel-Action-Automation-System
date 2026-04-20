from groq import Groq
from backend.RealtimeSearchEngine import RealtimeSearchEngine
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")
client   = Groq(api_key=env_vars.get("GroqAPIKey"))


def AgenticBrain(query):
    tools_inventory = """
    1.  play_music          : Play songs on YouTube. Input: song name.
    2.  web_search          : Real-time information, news, facts. Input: search query.
    3.  open_app            : Open applications or websites. Input: app/website name.
    4.  system_control      : Change volume or mute/unmute. Input: "volume up N", "volume down N", "mute", "unmute".
    5.  write_content       : Write essays, applications, code, notes. Input: topic.
    6.  image_generation    : Generate an AI image. Input: image description.
    7.  hand_gesture        : Start/stop hand gesture control. Input: "start" or "stop".
    8.  set_reminder        : Set a reminder with date/time. Input: "9pm tomorrow take medicine".
    9.  get_weather         : Get current weather. Input: city name.
    10. screenshot_analysis : Analyze what's on screen. Input: specific question about screen (or empty for general description).
    11. send_whatsapp       : Send a WhatsApp message. Input: "contact_name message text".
    12. send_email          : Send an email. Input: "recipient@email.com subject body".
    13. file_management     : Manage files/folders. Input: describe the task e.g. "organize downloads by type".
    """

    system_prompt = f"""You are an advanced AI assistant. You have access to these tools:
{tools_inventory}

If you need to use a tool, your response MUST exactly match this format:
Action: [tool_name]
Input: [tool_input]

If you do NOT need a tool (greeting, basic chat, math, etc.), just reply normally.
Do NOT use the 'Action:' format for conversational replies.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": query}
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2
        )

        ai_msg = response.choices[0].message.content.strip()

        if "Action:" in ai_msg and "Input:" in ai_msg:
            lines      = ai_msg.split('\n')
            action     = ""
            tool_input = ""
            for line in lines:
                if line.startswith("Action:"):
                    action = line.replace("Action:", "").strip()
                elif line.startswith("Input:"):
                    tool_input = line.replace("Input:", "").strip()

            print(f"\n[Agent → Tool: {action} | Input: {tool_input}]\n")

            # ---- TOOL DISPATCH ----

            if action == "play_music":
                from backend.Automation import PlayYoutube
                PlayYoutube(tool_input)
                return f"Playing '{tool_input}' on YouTube."

            elif action == "web_search":
                return RealtimeSearchEngine(tool_input)

            elif action == "open_app":
                from backend.Automation import OpenApp
                OpenApp(tool_input)
                return f"Opening {tool_input}."

            elif action == "system_control":
                from backend.Automation import System
                System(tool_input)
                return f"System: {tool_input} done."

            elif action == "write_content":
                from backend.Automation import Content
                Content(tool_input)
                return f"Content written for '{tool_input}' and opened in Notepad."

            elif action == "hand_gesture":
                from backend.Automation import StartHandGesture, StopHandGesture
                if "start" in tool_input.lower():
                    StartHandGesture()
                    return "Hand gesture control started."
                else:
                    StopHandGesture()
                    return "Hand gesture control stopped."

            elif action == "image_generation":
                img_data_path = r"frontend\files\ImageGeneration.data"
                os.makedirs(os.path.dirname(img_data_path), exist_ok=True)
                with open(img_data_path, "w") as file:
                    file.write(f"{tool_input},True")
                return f"Generating image: '{tool_input}' in the background."

            # ---- NEW TOOLS ----

            elif action == "set_reminder":
                from backend.Reminder import AddReminder
                return AddReminder(tool_input)

            elif action == "get_weather":
                from backend.Weather import GetWeather
                return GetWeather(tool_input)

            elif action == "screenshot_analysis":
                from backend.ScreenshotAnalysis import AnalyzeScreen
                question = tool_input if tool_input else "What is on this screen? Describe it."
                return AnalyzeScreen(question)

            elif action == "send_whatsapp":
                from backend.Messaging import SendWhatsApp
                return SendWhatsApp(tool_input)

            elif action == "send_email":
                from backend.Messaging import SendEmail
                return SendEmail(tool_input)

            elif action == "file_management":
                from backend.FileManagement import FileManagement
                return FileManagement(tool_input)

            else:
                # Unknown tool name from LLM — fall back to normal reply
                return str(ai_msg)

        else:
            # Normal conversational reply — no tool needed
            return str(ai_msg)

    except Exception as e:
        print(f"AgenticBrain Error: {e}")
        return "I faced a small glitch while processing that."
