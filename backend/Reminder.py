"""
Reminder.py — APScheduler based reminder system
Reminders survive the session via reminders.json
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from dateparser import parse as parse_date   # pip install dateparser
from datetime import datetime
from json import load, dump
import os

REMINDER_FILE = r"Data\reminders.json"
scheduler = BackgroundScheduler()
scheduler.start()

# -------------------------------------------------------
# Storage helpers
# -------------------------------------------------------

def _load_reminders():
    try:
        with open(REMINDER_FILE, "r") as f:
            return load(f)
    except:
        return []


def _save_reminders(data):
    os.makedirs("Data", exist_ok=True)
    with open(REMINDER_FILE, "w") as f:
        dump(data, f, indent=4)


# -------------------------------------------------------
# Core: add a reminder
# -------------------------------------------------------

def AddReminder(reminder_text: str):
    """
    reminder_text examples:
        '9:00pm 25th june business meeting'
        'tomorrow 8am wake up'
        '5 minutes take medicine'
    """
    # Try to extract a date/time from the text
    dt = parse_date(
        reminder_text,
        settings={
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False,
        }
    )

    if not dt:
        return f"Sorry, I couldn't understand the time in: '{reminder_text}'. Please say something like 'remind me at 9pm to take medicine'."

    if dt < datetime.now():
        return "That time has already passed. Please set a future reminder."

    # Extract message (remove date/time tokens — rough approach)
    # We pass the full text to TTS so user hears the full message
    message = reminder_text

    # Schedule the job
    job_id = f"reminder_{int(dt.timestamp())}"
    scheduler.add_job(
        _fire_reminder,
        trigger=DateTrigger(run_date=dt),
        args=[message],
        id=job_id,
        replace_existing=True
    )

    # Persist
    reminders = _load_reminders()
    reminders.append({
        "id": job_id,
        "text": message,
        "time": dt.strftime("%Y-%m-%d %H:%M:%S")
    })
    _save_reminders(reminders)

    return f"Reminder set for {dt.strftime('%I:%M %p, %d %B %Y')}."


def _fire_reminder(message: str):
    """Called by scheduler when reminder time arrives."""
    print(f"\n[REMINDER] {message}\n")

    # Play TTS notification
    try:
        from backend.TextToSpeech import TextToSpeech
        TextToSpeech(f"Reminder: {message}")
    except Exception as e:
        print(f"Reminder TTS error: {e}")

    # Windows toast notification (optional, needs win10toast)
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(
            "Reminder",
            message,
            duration=8,
            threaded=True
        )
    except:
        pass


# -------------------------------------------------------
# List & cancel reminders
# -------------------------------------------------------

def ListReminders():
    reminders = _load_reminders()
    if not reminders:
        return "You have no upcoming reminders."
    lines = ["Your upcoming reminders:"]
    for i, r in enumerate(reminders, 1):
        lines.append(f"  {i}. {r['text']} — at {r['time']}")
    return "\n".join(lines)


def CancelReminder(index: int):
    """Cancel reminder by 1-based index from ListReminders()."""
    reminders = _load_reminders()
    if not reminders or index < 1 or index > len(reminders):
        return "Invalid reminder number."
    r = reminders.pop(index - 1)
    try:
        scheduler.remove_job(r["id"])
    except:
        pass
    _save_reminders(reminders)
    return f"Reminder cancelled: '{r['text']}'."


# -------------------------------------------------------
# Restore reminders on startup (so they survive restart)
# -------------------------------------------------------

def RestoreReminders():
    reminders = _load_reminders()
    now = datetime.now()
    valid = []
    for r in reminders:
        try:
            dt = datetime.strptime(r["time"], "%Y-%m-%d %H:%M:%S")
            if dt > now:
                scheduler.add_job(
                    _fire_reminder,
                    trigger=DateTrigger(run_date=dt),
                    args=[r["text"]],
                    id=r["id"],
                    replace_existing=True
                )
                valid.append(r)
        except Exception as e:
            print(f"Could not restore reminder '{r}': {e}")
    _save_reminders(valid)
    if valid:
        print(f"[Reminder] Restored {len(valid)} reminder(s).")


# Auto-restore when module is imported
RestoreReminders()


if __name__ == "__main__":
    import time
    print(AddReminder("10 seconds test reminder"))
    print(ListReminders())
    time.sleep(15)
