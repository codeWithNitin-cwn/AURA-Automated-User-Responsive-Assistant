import csv
import os
import time
import subprocess
import psutil
import webbrowser
import urllib.parse
from ddgs import DDGS
from security import is_app_safe, WORKSPACE_DIR, is_path_safe
from services.db_helper import add_calendar_event

# ════════════════════════════════════════════
# 1. WEB SEARCH
# ════════════════════════════════════════════
def tool_web_search(params):
    query = params.get('query', '')
    try:
        time.sleep(1)
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3, backend="lite"))
        if not results:
            return f"No results found for '{query}'."
        lines = [f"Here's what I found about '{query}':"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}: {r['body'][:200]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Search failed: {e}"

# ════════════════════════════════════════════
# 2. CALENDAR (Upgraded to write to SQLite)
# ════════════════════════════════════════════
def tool_calendar(params):
    action = params.get('action', 'add')
    title  = params.get('title', 'Untitled Event')
    dt     = params.get('datetime', 'unspecified time')
    
    success = add_calendar_event(title, dt, action)
    if success:
        return f"Successfully added '{title}' to your SQLite calendar database for {dt}."
    else:
        return f"Failed to record calendar event '{title}' to database."

# ════════════════════════════════════════════
# 3. EMAIL
# ════════════════════════════════════════════
def tool_email(params):
    to      = params.get('to', '')
    subject = params.get('subject', 'No Subject')
    body    = params.get('body', '')

    if not to:
        return "No recipient specified. Please say who to send it to."

    url = (
        "https://mail.google.com/mail/?view=cm"
        f"&to={urllib.parse.quote(to)}"
        f"&su={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )
    webbrowser.open(url)
    return f"Gmail opened — composing email to {to} with subject '{subject}'. Just hit Send."

# ════════════════════════════════════════════
# 4. OPEN APP (Sandboxed App Whitelist)
# ════════════════════════════════════════════
APP_MAP = {
    'chrome':        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'google chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'notepad':       'notepad.exe',
    'calculator':    'calc.exe',
    'paint':         'mspaint.exe',
    'file explorer': 'explorer.exe',
    'explorer':      'explorer.exe',
    'vs code':       'code',
    'vscode':        'code',
    'spotify':       r'C:\Users\Nitin\AppData\Roaming\Spotify\Spotify.exe',
    'task manager':  'taskmgr.exe',
    'cmd':           'cmd.exe',
    'terminal':      'cmd.exe',
    'word':          r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
    'excel':         r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
    'powerpoint':    r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE',
}

def tool_open_app(params):
    target = params.get('target', '').strip()
    if not target:
        return "Please specify an application name to launch."

    # Validate against Whitelist security check
    if not is_app_safe(target):
        return f"Security Block: Access to target application '{target}' is restricted to prevent shell execution escapes."

    path = APP_MAP.get(target.lower())
    try:
        if path:
            subprocess.Popen(path, shell=True)
        else:
            subprocess.Popen(f'start "" "{target}"', shell=True)
        return f"Opening whitelisted application {target}."
    except Exception as e:
        return f"Could not open {target}: {e}"

# ════════════════════════════════════════════
# 4b. OPEN FOLDER (Sandboxed inside WORKSPACE_DIR)
# ════════════════════════════════════════════
def tool_open_folder(params):
    name = params.get('name', '').strip()
    
    if not name:
        subprocess.Popen(f'explorer "{WORKSPACE_DIR}"')
        return "Opened File Explorer in workspace root."

    # Check for shortcut defaults pointing to sandbox workspace root
    guesses = {'desktop', 'downloads', 'documents', 'workspace'}
    if name.lower() in guesses:
        subprocess.Popen(f'explorer "{WORKSPACE_DIR}"')
        return f"Opened sandboxed workspace folder."

    # Verify if it's already a full path
    if os.path.isdir(name):
        resolved = os.path.abspath(name)
        if is_path_safe(resolved):
            subprocess.Popen(f'explorer "{resolved}"')
            return f"Opened folder: {resolved}"
        return f"Security Block: Folder target '{resolved}' is outside workspace directory."

    # Search inside the sandboxed workspace folder recursively
    found = None
    try:
        for dirpath, dirnames, _ in os.walk(WORKSPACE_DIR):
            for d in dirnames:
                if d.lower() == name.lower():
                    found = os.path.join(dirpath, d)
                    break
            if found:
                break
    except Exception:
        pass

    if found:
        subprocess.Popen(f'explorer "{found}"')
        return f"Found and opened folder: {found}"

    return f"Folder '{name}' not found inside your workspace sandbox."

# ════════════════════════════════════════════
# 5. CLOSE APP
# ════════════════════════════════════════════
def tool_close_app(params):
    target = params.get('target', '').strip().lower()
    if not target:
        return "Please specify an app process to terminate."

    # Restrict terminate target to whitelist to avoid closing core OS systems
    if not is_app_safe(target):
        return f"Security Block: Closing system or unrecognized process '{target}' is restricted."

    killed = []
    for proc in psutil.process_iter(['name']):
        if target in proc.info['name'].lower():
            try:
                proc.kill()
                killed.append(proc.info['name'])
            except:
                pass
    return f"Closed: {', '.join(set(killed))}." if killed else f"No active process found for whitelist target '{target}'."
