from flask import Flask, request, jsonify
import sys
import os
import pyautogui

# Ensure current service path is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "services"))

# Set PyAutoGUI safety boundaries
pyautogui.FAILSAFE = True

# Import modular service controllers
from services.file_ops import (
    tool_read_file,
    tool_open_file,
    tool_create_file,
    tool_edit_file,
    tool_delete_file,
    tool_list_files,
    tool_find_file,
)
from services.system import (
    tool_system_info,
    tool_get_time,
)
from services.window_ops import (
    tool_window,
)
from services.interaction import (
    tool_mouse,
    tool_keyboard,
    tool_volume,
)
from services.integrations import (
    tool_web_search,
    tool_calendar,
    tool_email,
    tool_open_app,
    tool_open_folder,
    tool_close_app,
)
from services.vision_helper import (
    tool_read_screen,
    tool_click_icon,
    tool_desktop_icons,
)

# Import Database and Security configurations
import services.db_helper as db
from security import is_input_safe

# Initialize PostgreSQL schemas
db.init_db()

app = Flask(__name__)

# General fallback controller
def tool_general(params):
    return params.get('response', "I'm AURA. How can I help?")

# Tool Dispatch Table mapping parsed intents to functions
TOOLS = {
    'web_search':    tool_web_search,
    'calendar':      tool_calendar,
    'email':         tool_email,
    'open_app':      tool_open_app,
    'open_folder':   tool_open_folder,
    'search_folder': tool_open_folder,  # alias
    'close_app':     tool_close_app,
    'open_file':     tool_open_file,
    'read_file':     tool_read_file,
    'create_file':   tool_create_file,
    'edit_file':     tool_edit_file,
    'get_time':      tool_get_time,
    'delete_file':   tool_delete_file,
    'list_files':    tool_list_files,
    'find_file':     tool_find_file,
    'mouse':         tool_mouse,
    'keyboard':      tool_keyboard,
    'volume':        tool_volume,
    'system_info':   tool_system_info,
    'window':        tool_window,
    'general':       tool_general,
    'read_screen':   tool_read_screen,
    'click_icon':    tool_click_icon,
    'desktop_icons': tool_desktop_icons,
}

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json() or {}
    tool = data.get('tool', 'general')
    params = data.get('params', {})
    command_text = data.get('command_text', '').strip()

    print(f"[TOOL] Running: {tool} with {params}")

    # 1. Pre-execution safety check on user prompt string
    if command_text and not is_input_safe(command_text):
        err_msg = "Security Block: Command contains blacklisted keyword patterns and cannot be processed."
        db.log_security_violation(command_text, "malicious_keyword", "input_string")
        db.log_execution(command_text, tool, "blocked", err_msg)
        return jsonify({"result": err_msg})

    # 2. Execute the Whitelisted function
    fn = TOOLS.get(tool, tool_general)
    try:
        result = fn(params)
        result_str = str(result)
        
        # Check if result is a security boundary block
        if result_str.startswith("Security Block:"):
            db.log_security_violation(command_text or "API Call", "path_or_app_escape", result_str)
            db.log_execution(command_text or "API Call", tool, "blocked", result_str)
        else:
            db.log_execution(command_text or "API Call", tool, "success", result_str)

    except Exception as e:
        result_str = f"Error during tool execution: {e}"
        db.log_execution(command_text or "API Call", tool, "error", result_str)
    
    print(f"[TOOL] Result: {result_str[:120]}")
    return jsonify({"result": result_str})

# ════════════════════════════════════════════
# DATABASE API PROXY ENDPOINTS
# ════════════════════════════════════════════

@app.route('/db/history', methods=['GET'])
def db_history():
    return jsonify(db.get_execution_logs())

@app.route('/db/calendar', methods=['GET'])
def db_calendar():
    return jsonify(db.get_calendar_events())

@app.route('/db/security', methods=['GET'])
def db_security():
    return jsonify(db.get_security_logs())

@app.route('/db/configs', methods=['GET', 'POST'])
def db_configs():
    if request.method == 'POST':
        payload = request.get_json() or {}
        key = payload.get("key")
        val = payload.get("value")
        if not key or val is None:
            return jsonify({"error": "Missing key or value"}), 400
        success = db.update_system_config(key, str(val))
        return jsonify({"success": success})
    
    return jsonify(db.get_system_configs())

if __name__ == '__main__':
    print("Tools Service running on port 5003...")
    app.run(port=5003, debug=False)
