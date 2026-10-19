import requests

VISION_URL = "http://localhost:5005"

# ════════════════════════════════════════════
# SCREEN VISION CLIENT CALLS
# ════════════════════════════════════════════
def tool_read_screen(params):
    question = params.get('question', 'What do you see on screen?')
    try:
        r = requests.post(f"{VISION_URL}/read_screen", json={"question": question}, timeout=20)
        return r.json().get("result", "Could not read screen.")
    except Exception as e:
        return f"Vision service error: {e}"

def tool_click_icon(params):
    target = params.get('target', '')
    action = params.get('action', 'double_click')
    try:
        r = requests.post(f"{VISION_URL}/click_icon", json={"target": target, "action": action}, timeout=20)
        return r.json().get("result", "Could not click icon.")
    except Exception as e:
        return f"Vision service error: {e}"

def tool_desktop_icons(params):
    try:
        r = requests.get(f"{VISION_URL}/desktop_icons", timeout=15)
        return r.json().get("result", "Could not list icons.")
    except Exception as e:
        return f"Vision service error: {e}"
