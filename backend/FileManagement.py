"""
FileManagement.py — AI-powered file & folder automation
Commands like: 'move all PDFs from Downloads to Documents',
               'delete files older than 30 days in temp folder',
               'organize Downloads by file type'
"""
import os
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta
from groq import Groq
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
client   = Groq(api_key=env_vars.get("GroqAPIKey"))

# Common folder shortcuts
FOLDER_ALIASES = {
    "downloads":  str(Path.home() / "Downloads"),
    "documents":  str(Path.home() / "Documents"),
    "desktop":    str(Path.home() / "Desktop"),
    "pictures":   str(Path.home() / "Pictures"),
    "music":      str(Path.home() / "Music"),
    "videos":     str(Path.home() / "Videos"),
    "temp":       os.environ.get("TEMP", "C:\\Temp"),
}

# File type categories
FILE_CATEGORIES = {
    "images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"],
    "videos":     [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "documents":  [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".odt"],
    "archives":   [".zip", ".rar", ".7z", ".tar", ".gz"],
    "code":       [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".ts"],
    "executables":[".exe", ".msi", ".bat", ".cmd"],
}


def _resolve_folder(name: str) -> str:
    """Resolve folder alias to full path."""
    key = name.lower().strip()
    if key in FOLDER_ALIASES:
        return FOLDER_ALIASES[key]
    # If it looks like a real path, return as-is
    if os.path.sep in name or (len(name) > 2 and name[1] == ":"):
        return name
    return name


# -------------------------------------------------------
# Core operations
# -------------------------------------------------------

def OrganizeByType(folder: str = "downloads") -> str:
    """
    Organizes files in a folder into subfolders by type.
    e.g. Downloads/images/, Downloads/documents/, etc.
    """
    folder_path = _resolve_folder(folder)
    if not os.path.exists(folder_path):
        return f"Folder not found: {folder_path}"

    moved = 0
    errors = []

    for file in Path(folder_path).iterdir():
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        category = None
        for cat, exts in FILE_CATEGORIES.items():
            if ext in exts:
                category = cat
                break

        if not category:
            category = "others"

        dest_folder = Path(folder_path) / category
        dest_folder.mkdir(exist_ok=True)

        try:
            shutil.move(str(file), str(dest_folder / file.name))
            moved += 1
        except Exception as e:
            errors.append(f"{file.name}: {e}")

    result = f"Organized {moved} files in '{folder_path}' by type."
    if errors:
        result += f"\nErrors ({len(errors)}): " + ", ".join(errors[:3])
    return result


def MoveFiles(source_folder: str, dest_folder: str, extension: str = None) -> str:
    """
    Move files from source to destination.
    Optionally filter by extension (e.g. '.pdf')
    """
    src  = _resolve_folder(source_folder)
    dest = _resolve_folder(dest_folder)

    if not os.path.exists(src):
        return f"Source folder not found: {src}"

    os.makedirs(dest, exist_ok=True)
    moved = 0

    for file in Path(src).iterdir():
        if not file.is_file():
            continue
        if extension and file.suffix.lower() != extension.lower():
            continue
        try:
            shutil.move(str(file), os.path.join(dest, file.name))
            moved += 1
        except Exception as e:
            print(f"Error moving {file.name}: {e}")

    return f"Moved {moved} files from '{src}' to '{dest}'."


def DeleteOldFiles(folder: str, days: int = 30) -> str:
    """Delete files older than N days from a folder."""
    folder_path = _resolve_folder(folder)
    if not os.path.exists(folder_path):
        return f"Folder not found: {folder_path}"

    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0

    for file in Path(folder_path).iterdir():
        if not file.is_file():
            continue
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime < cutoff:
            try:
                file.unlink()
                deleted += 1
            except Exception as e:
                print(f"Error deleting {file.name}: {e}")

    return f"Deleted {deleted} files older than {days} days from '{folder_path}'."


def FindFiles(folder: str, keyword: str) -> str:
    """Search for files containing keyword in their name."""
    folder_path = _resolve_folder(folder)
    if not os.path.exists(folder_path):
        return f"Folder not found: {folder_path}"

    results = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if keyword.lower() in file.lower():
                results.append(os.path.join(root, file))

    if not results:
        return f"No files found matching '{keyword}' in '{folder_path}'."

    output = f"Found {len(results)} file(s) matching '{keyword}':\n"
    for r in results[:10]:  # show max 10
        output += f"  {r}\n"
    if len(results) > 10:
        output += f"  ... and {len(results)-10} more."
    return output.strip()


def RenameFiles(folder: str, old_pattern: str, new_pattern: str) -> str:
    """
    Batch rename files.
    e.g. RenameFiles('downloads', 'IMG_', 'Photo_')
    """
    folder_path = _resolve_folder(folder)
    if not os.path.exists(folder_path):
        return f"Folder not found: {folder_path}"

    renamed = 0
    for file in Path(folder_path).iterdir():
        if not file.is_file():
            continue
        if old_pattern in file.name:
            new_name = file.name.replace(old_pattern, new_pattern)
            try:
                file.rename(file.parent / new_name)
                renamed += 1
            except Exception as e:
                print(f"Error renaming {file.name}: {e}")

    return f"Renamed {renamed} files (replaced '{old_pattern}' with '{new_pattern}')."


# -------------------------------------------------------
# AI-powered natural language file command interpreter
# -------------------------------------------------------

def FileManagement(command: str) -> str:
    """
    Natural language file management.
    Uses Groq to parse the command and execute the right operation.
    """
    system_prompt = """You are a file management command parser.
Given a natural language command, extract the operation and parameters.
Respond ONLY in this exact format (one line):
OPERATION|PARAM1|PARAM2|PARAM3

Operations available:
- organize_by_type|folder_name
- move_files|source_folder|destination_folder|extension_or_none
- delete_old_files|folder_name|days
- find_files|folder_name|keyword
- rename_files|folder_name|old_pattern|new_pattern

Examples:
"organize my downloads" → organize_by_type|downloads
"move PDFs from downloads to documents" → move_files|downloads|documents|.pdf
"delete files older than 7 days in temp" → delete_old_files|temp|7
"find resume in documents" → find_files|documents|resume
"rename all IMG_ files to Photo_ in pictures" → rename_files|pictures|IMG_|Photo_

If unclear, respond: unclear|unknown
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            max_tokens=100,
            temperature=0.0
        )

        parsed = response.choices[0].message.content.strip()
        parts  = parsed.split("|")
        op     = parts[0].lower()

        if op == "organize_by_type":
            folder = parts[1] if len(parts) > 1 else "downloads"
            return OrganizeByType(folder)

        elif op == "move_files":
            src  = parts[1] if len(parts) > 1 else "downloads"
            dest = parts[2] if len(parts) > 2 else "documents"
            ext  = parts[3] if len(parts) > 3 and parts[3] != "none" else None
            return MoveFiles(src, dest, ext)

        elif op == "delete_old_files":
            folder = parts[1] if len(parts) > 1 else "downloads"
            days   = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 30
            return DeleteOldFiles(folder, days)

        elif op == "find_files":
            folder  = parts[1] if len(parts) > 1 else "documents"
            keyword = parts[2] if len(parts) > 2 else ""
            return FindFiles(folder, keyword)

        elif op == "rename_files":
            folder      = parts[1] if len(parts) > 1 else "downloads"
            old_pattern = parts[2] if len(parts) > 2 else ""
            new_pattern = parts[3] if len(parts) > 3 else ""
            return RenameFiles(folder, old_pattern, new_pattern)

        else:
            return f"I didn't understand the file management command: '{command}'. Please be more specific."

    except Exception as e:
        return f"File management error: {str(e)}"


if __name__ == "__main__":
    while True:
        cmd = input("File command: ")
        print(FileManagement(cmd))
