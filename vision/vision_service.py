# vision/vision_service.py
# Gives AURA eyes — it can SEE your screen and click on things

from flask import Flask, request, jsonify
from groq import Groq
from PIL import ImageGrab, Image
import pyautogui
import base64, io, os, json, time, requests, sys
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
load_dotenv(ENV_PATH)
app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SCREENSHOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screen.png")
PROVIDER = os.getenv("AURA_LLM_PROVIDER", "GROQ")

# ── Take a screenshot and return as base64 ──────────────────
def take_screenshot(region=None):
    """Captures screen, saves it, returns (base64 string, (orig_w, orig_h), (new_w, new_h))."""
    try:
        img = ImageGrab.grab(bbox=region)  # None = full screen
        orig_w, orig_h = img.size

        # Preserve exact aspect ratio while scaling within max 1280x720
        scale = min(1280.0 / orig_w, 720.0 / orig_h)
        new_w = max(1, int(orig_w * scale))
        new_h = max(1, int(orig_h * scale))

        resized_img = img.resize((new_w, new_h), Image.LANCZOS)
        resized_img.save(SCREENSHOT_PATH)
        buf = io.BytesIO()
        resized_img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return b64, (orig_w, orig_h), (new_w, new_h)
    except Exception as e:
        print(f"[VISION] Screenshot failed: {e}")
        return None, (0, 0), (0, 0)

# ── Ask Groq Vision what's on screen ────────────────────────
def ask_groq_vision(b64_image, question):
    try:
        model = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ],
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[VISION GROQ ERROR] {e}")
        return None

# ── Ask Ollama Vision what's on screen ──────────────────────
def ask_ollama_vision(b64_image, question):
    try:
        url = os.getenv("OLLAMA_VISION_URL", "http://localhost:11434/api/chat")
        model = os.getenv("OLLAMA_VISION_MODEL", "llava")
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": question,
                    "images": [b64_image]
                }
            ],
            "stream": False
        }
        r = requests.post(url, json=payload, timeout=25)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[VISION OLLAMA ERROR] {e}")
        return None

# ── Ask Vision routing orchestrator ─────────────────────────
def ask_vision(b64_image, question):
    if PROVIDER == "OLLAMA":
        print("[VISION] Analyzing screen via local Ollama...")
        res = ask_ollama_vision(b64_image, question)
        if res is not None:
            return res
        print("[VISION WARNING] Ollama failed, falling back to Groq...")
    
    return ask_groq_vision(b64_image, question)

# ── Find the pixel location of an icon by name ──────────────
def find_icon_location(b64_image, icon_name, canvas_w=1280, canvas_h=720):
    """Ask vision model to return the center x,y coordinates of an icon."""
    question = f"""You are an expert GUI element locator.
The image provided is a desktop screenshot of dimensions {canvas_w}x{canvas_h} (width={canvas_w}, height={canvas_h}, top-left is x=0, y=0, bottom-right is x={canvas_w}, y={canvas_h}).
Target element to locate: '{icon_name}'

Carefully inspect the image:
- If this is a system status icon (e.g. battery, wifi, sound/volume, network, action center, or clock), it is located in the Windows system tray at the bottom right of the screen on the taskbar.
- If this is a taskbar app or the Windows Start button, look along the bottom taskbar.
- If this is a desktop icon or shortcut, inspect the desktop area.
- If this is a window control button (minimize, maximize, close), look at the top title bar of windows.
- Determine the center pixel coordinates (x between 0 and {canvas_w}, y between 0 and {canvas_h}) of this element.

Return ONLY a raw JSON object:
{{"found": true, "x": <int>, "y": <int>, "description": "<brief description>"}}
If not found:
{{"found": false, "x": 0, "y": 0, "description": "not found"}}
"""

    result = ask_vision(b64_image, question)
    if not result:
        return {"found": False, "x": 0, "y": 0, "description": "Vision failed"}
    try:
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        data = json.loads(result.strip())
        if isinstance(data, dict):
            return data
        return {"found": False, "x": 0, "y": 0, "description": "Invalid JSON format"}
    except:
        return {"found": False, "x": 0, "y": 0, "description": result}

# ════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════

# 1. READ SCREEN — tell AURA what's on screen
@app.route('/read_screen', methods=['POST'])
def read_screen():
    """Take screenshot and describe what's visible."""
    data     = request.get_json() or {}
    question = data.get('question', 'What applications, icons, and folders do you see on the desktop? List everything visible.')
    print(f"[VISION] Reading screen...")
    b64, _, _ = take_screenshot()
    if not b64:
        return jsonify({"result": "Could not take screenshot."}), 500
    answer = ask_vision(b64, question)
    print(f"[VISION] Screen says: {str(answer)[:150]}")
    return jsonify({"result": answer or "Could not read screen."})

# 2. CLICK ICON — find and click something by name
@app.route('/click_icon', methods=['POST'])
def click_icon():
    """Find an icon/app/folder by name and click it."""
    data   = request.get_json() or {}
    target = data.get('target', '')
    action = data.get('action', 'double_click')  # single_click or double_click

    print(f"[VISION] Looking for '{target}' on screen...")
    b64, (orig_w, orig_h), (new_w, new_h) = take_screenshot()
    if not b64:
        return jsonify({"result": "Could not take screenshot."}), 500

    loc = find_icon_location(b64, target, new_w, new_h)
    print(f"[VISION] Found: {loc}")

    if not loc.get('found'):
        return jsonify({"result": f"I couldn't find '{target}' on your screen. {loc.get('description','')}"})

    raw_x = int(loc.get('x', 0))
    raw_y = int(loc.get('y', 0))

    # Scale coordinates back to actual screen resolution
    screen_w, screen_h = pyautogui.size()
    target_w = orig_w if orig_w > 0 else screen_w
    target_h = orig_h if orig_h > 0 else screen_h
    
    x = int(raw_x * target_w / new_w) if new_w > 0 else raw_x
    y = int(raw_y * target_h / new_h) if new_h > 0 else raw_y

    # Clamp coordinates to screen boundaries
    x = max(0, min(screen_w - 1, x))
    y = max(0, min(screen_h - 1, y))

    print(f"[VISION] Moving mouse to ({x}, {y}) on {screen_w}x{screen_h} display for action '{action}'")
    pyautogui.moveTo(x, y, duration=0.4)
    time.sleep(0.15)
    if action == 'double_click':
        pyautogui.doubleClick(x, y)
    else:
        pyautogui.click(x, y)

    return jsonify({"result": f"Found '{target}' at ({x}, {y}) and clicked it. {loc.get('description', '')}"})

# 3. DESCRIBE SCREEN — what is AURA currently looking at
@app.route('/describe', methods=['POST'])
def describe():
    """Full description of current screen state."""
    b64, _, _ = take_screenshot()
    if not b64:
        return jsonify({"result": "Could not take screenshot."}), 500
    answer = ask_vision(b64, "Describe exactly what is on this screen in detail. List all visible icons, windows, folders, text, and taskbar items.")
    return jsonify({"result": answer or "Could not describe screen."})

# 4. FIND TEXT ON SCREEN
@app.route('/find_text', methods=['POST'])
def find_text():
    """Find specific text visible on screen."""
    data = request.get_json() or {}
    text = data.get('text', '')
    b64, _, _ = take_screenshot()
    if not b64:
        return jsonify({"result": "Could not take screenshot."}), 500
    answer = ask_vision(b64, f"Is the text '{text}' visible anywhere on this screen? If yes, describe where it is and return its approximate x,y coordinates as JSON. If no, say not found.")
    return jsonify({"result": answer or "Could not search screen."})

# 5. GET DESKTOP ICONS — list all icons on desktop
@app.route('/desktop_icons', methods=['GET'])
def desktop_icons():
    """List all icons visible on desktop + from filesystem."""
    # Method 1: Read from filesystem (reliable)
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    try:
        items = os.listdir(desktop_path)
        files   = [i for i in items if os.path.isfile(os.path.join(desktop_path, i))]
        folders = [i for i in items if os.path.isdir(os.path.join(desktop_path, i))]
        fs_result = f"Desktop folders: {', '.join(folders) or 'none'}\nDesktop files: {', '.join(files) or 'none'}"
    except Exception as e:
        fs_result = f"Could not read desktop folder: {e}"

    # Method 2: Visual scan (what AI sees on screen)
    b64, _, _ = take_screenshot()
    visual = ask_vision(b64, "List ALL icons you can see on the desktop. Include their approximate positions (left/center/right, top/middle/bottom of screen).") if b64 else "Screenshot failed."

    return jsonify({
        "filesystem": fs_result,
        "visual":     visual or "Could not scan visually.",
        "result":     fs_result  # used by gateway
    })

if __name__ == '__main__':
    print("[VISION] Screen vision service running on port 5005...")
    app.run(port=5005, debug=False)