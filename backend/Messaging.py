"""
Messaging.py — WhatsApp & Email automation
WhatsApp via pywhatkit | Email via smtplib (Gmail)
Add to .env:
    EMAIL_ADDRESS=your@gmail.com
    EMAIL_PASSWORD=your_app_password   (Gmail App Password, not your main password)
"""
import pywhatkit as kit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from groq import Groq
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
client   = Groq(api_key=env_vars.get("GroqAPIKey"))

EMAIL_ADDRESS  = env_vars.get("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = env_vars.get("EMAIL_PASSWORD", "")  # Gmail App Password

# -------------------------------------------------------
# WhatsApp
# -------------------------------------------------------

# Store contact name → phone number mapping
# You can extend this dict or load from a contacts.json
CONTACTS = {
    "harshita":"+917000285053",   # Replace with real numbers
    "ajay thakur":"+918894620997",
    "mom":   "+917000285053",
    "friend": "+919753358017",
}


def SendWhatsApp(command: str) -> str:
    """
    Send a WhatsApp message.
    command examples:
        'mom I will be late'
        'friend are you free tonight?'
        '+919876543210 hello'
    """
    # Parse command with AI
    parsed = _parse_message_command(command, channel="whatsapp")
    if not parsed:
        return "Could not understand the WhatsApp command. Say something like 'send whatsapp to mom I will be late'."

    recipient, message = parsed

    # Resolve contact name to number
    phone = None
    if recipient.startswith("+"):
        phone = recipient
    else:
        phone = CONTACTS.get(recipient.lower())

    if not phone:
        return (f"Contact '{recipient}' not found. "
                f"Please add them to CONTACTS dict in Messaging.py, "
                f"or use their full phone number like +91XXXXXXXXXX.")

    try:
        # Schedule 2 minutes ahead (pywhatkit requirement)
        now = datetime.now()
        send_hour   = now.hour
        send_minute = now.minute + 2
        if send_minute >= 60:
            send_minute -= 60
            send_hour = (send_hour + 1) % 24

        kit.sendwhatmsg_instantly(
            phone_no=phone,
            message=message,
            # time_hour=send_hour,
            # time_min=send_minute,
            wait_time=15,
            tab_close=True,
            close_time=4
        )
        return f"WhatsApp message scheduled to {recipient}: '{message}'"

    except Exception as e:
        return f"WhatsApp error: {str(e)}"


# -------------------------------------------------------
# Email (Gmail via SMTP)
# -------------------------------------------------------

def SendEmail(command: str) -> str:
    """
    Send an email.
    command examples:
        'boss subject meeting tomorrow body I will be late'
        'friend@gmail.com hello there'
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return ("Email not configured. Please add EMAIL_ADDRESS and "
                "EMAIL_PASSWORD (Gmail App Password) to your .env file.")

    parsed = _parse_email_command(command)
    if not parsed:
        return "Could not understand the email command."

    recipient_email, subject, body = parsed

    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return f"Email sent to {recipient_email} with subject '{subject}'."

    except smtplib.SMTPAuthenticationError:
        return ("Gmail authentication failed. Make sure you're using a Gmail App Password, "
                "not your regular Gmail password. "
                "Generate one at: myaccount.google.com/apppasswords")
    except Exception as e:
        return f"Email error: {str(e)}"


# -------------------------------------------------------
# AI parsers
# -------------------------------------------------------

def _parse_message_command(command: str, channel: str = "whatsapp"):
    """Use Groq to extract recipient and message from natural language."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Extract the recipient and message from this {channel} command. "
                        "Respond ONLY in this format: RECIPIENT|MESSAGE\n"
                        "Example: 'tell mom I will be late' → mom|I will be late\n"
                        "Example: 'message +919876543210 hello there' → +919876543210|hello there"
                    )
                },
                {"role": "user", "content": command}
            ],
            max_tokens=100,
            temperature=0.0
        )
        parts = response.choices[0].message.content.strip().split("|", 1)
        if len(parts) == 2:
            return parts[0].strip().lower(), parts[1].strip()
        return None
    except Exception as e:
        print(f"Parse error: {e}")
        return None


def _parse_email_command(command: str):
    """Use Groq to extract recipient email, subject, and body."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the email recipient, subject, and body from the command. "
                        "Respond ONLY in format: EMAIL|SUBJECT|BODY\n"
                        "If subject is not mentioned, generate a short appropriate one.\n"
                        "Example: 'email boss@gmail.com I will be late tomorrow' → "
                        "boss@gmail.com|Running Late Tomorrow|Hi, I wanted to let you know I will be late tomorrow."
                    )
                },
                {"role": "user", "content": command}
            ],
            max_tokens=200,
            temperature=0.3
        )
        parts = response.choices[0].message.content.strip().split("|", 2)
        if len(parts) == 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        return None
    except Exception as e:
        print(f"Email parse error: {e}")
        return None


if __name__ == "__main__":
    print(SendWhatsApp("mom I will be home late tonight"))
