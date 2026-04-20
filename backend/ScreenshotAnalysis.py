"""
ScreenshotAnalysis.py — Takes a screenshot and analyzes it using Groq Vision API
"""
import pyautogui
import base64
import os
from io import BytesIO
from groq import Groq
from dotenv import dotenv_values
from datetime import datetime

env_vars  = dotenv_values(".env")
client    = Groq(api_key=env_vars.get("GroqAPIKey"))

SCREENSHOT_DIR = "Data"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def _capture_screenshot() -> str:
    """Take a screenshot and save it. Returns the file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path


def _image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def AnalyzeScreen(user_question: str = "What is on this screen? Describe it in detail.") -> str:
    """
    Takes a screenshot and asks Groq Vision to analyze it.

    Args:
        user_question: What to ask about the screen.
                       e.g. "What application is open?"
                            "Read the text on screen"
                            "What should I click to submit this form?"

    Returns:
        AI's answer as a string.
    """
    try:
        # 1. Capture screen
        screenshot_path = _capture_screenshot()
        print(f"[Screenshot saved: {screenshot_path}]")

        # 2. Convert to base64
        image_data = _image_to_base64(screenshot_path)

        # 3. Send to Groq Vision (llama-3.2-90b-vision-preview)
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Groq's vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": user_question
                        }
                    ]
                }
            ],
            max_tokens=1024,
            temperature=0.3
        )

        answer = response.choices[0].message.content.strip()
        return answer

    except Exception as e:
        print(f"ScreenshotAnalysis Error: {e}")
        return f"Sorry, I couldn't analyze the screen. Error: {str(e)}"


def ReadTextOnScreen() -> str:
    """Convenience function — reads all text visible on screen."""
    return AnalyzeScreen("Please read and list all the text visible on this screen.")


def DescribeScreen() -> str:
    """Convenience function — general description of what's on screen."""
    return AnalyzeScreen("What application is open and what is happening on this screen? Give a brief description.")


def HelpWithScreen() -> str:
    """Convenience function — asks AI what to do next."""
    return AnalyzeScreen(
        "Look at this screen and tell me: what application is open, what is currently displayed, "
        "and what are the main actions I can take from here?"
    )


if __name__ == "__main__":
    print("Analyzing screen...")
    result = DescribeScreen()
    print(result)
