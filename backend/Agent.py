from groq import Groq
from backend.RealtimeSearchEngine import RealtimeSearchEngine
from dotenv import dotenv_values
import os

# === Load environment variables ===
env_vars = dotenv_values(".env")
client = Groq(api_key=env_vars.get("GroqAPIKey"))

def AgenticBrain(query):
    # Ab Agent ko tere SAARE tools pata hain!
    tools_inventory = """
    1. play_music: Use this to play songs on YouTube. Input: song name.
    2. web_search: Use this for real-time information, news, or factual questions. Input: search query.
    3. open_app: Use this to open applications. Input: app name.
    4. system_control: Use this to change system volume or mute. Input: "volume up", "volume down", "mute", or "unmute".
    5. write_content: Use this to write essays, applications, notes, or code. Input: topic to write about.
    6. image_generation: Use this to generate an AI image. Input: description of the image.
    7. hand_gesture: Use this to start or stop the hand gesture feature. Input: "start" or "stop".
    """

    system_prompt = f"""You are an advanced AI. You have the following tools: {tools_inventory}
    If you need to use a tool, your response MUST exactly match this format:
    Action: [tool_name]
    Input: [tool_input]

    If you do NOT need a tool (like answering a greeting, how are you, or basic chat), just reply normally to the user as a helpful assistant. Do NOT use the 'Action:' format.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2
        )

        ai_msg = response.choices[0].message.content.strip()

        # Check if AI decided to use a tool
        if "Action:" in ai_msg and "Input:" in ai_msg:
            # Safely extract action and input
            lines = ai_msg.split('\n')
            action = ""
            tool_input = ""
            for line in lines:
                if line.startswith("Action:"):
                    action = line.replace("Action:", "").strip()
                elif line.startswith("Input:"):
                    tool_input = line.replace("Input:", "").strip()

            print(f"\n[Agent Decided to use Tool: {action} | Input: {tool_input}]\n")

            # === EXECUTE THE CHOSEN TOOL ===
            
            if action == "play_music":
                from backend.Automation import PlayYoutube
                PlayYoutube(tool_input)
                return f"Playing {tool_input} on YouTube for you."

            elif action == "web_search":
                return RealtimeSearchEngine(tool_input)

            elif action == "open_app":
                from backend.Automation import OpenApp
                OpenApp(tool_input)
                return f"Opening {tool_input}."
            
            # --- NAYE TOOLS ADD KIYE HAIN NEECHE ---
            
            elif action == "system_control":
                from backend.Automation import System
                System(tool_input)
                return f"System {tool_input} executed."
                
            elif action == "write_content":
                from backend.Automation import Content
                Content(tool_input)
                return f"I have written the content for {tool_input} and opened it in Notepad."
                
            elif action == "hand_gesture":
                from backend.Automation import StartHandGesture, StopHandGesture
                if "start" in tool_input.lower():
                    StartHandGesture()
                    return "Hand gesture control started."
                else:
                    StopHandGesture()
                    return "Hand gesture control stopped."
                    
            elif action == "image_generation":
                with open(r"frontend\files\ImageGeneration.data", "w") as file:
                    file.write(f"{tool_input},True")
                return f"Generating an image of {tool_input} in the background."

            else:
                return str(ai_msg) # Fallback if tool name is weird

        else:
            # NORMAL CHAT
            return str(ai_msg)

    except Exception as e:
        print(f"AgenticBrain Error: {e}")
        return "I faced a small glitch while processing that."

    return "Task completed."