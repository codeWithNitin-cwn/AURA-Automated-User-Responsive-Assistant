import os
from dotenv import load_dotenv

load_dotenv()

# Predefined safe apps mapping
ALLOWED_APPS = {
    'chrome', 'google chrome', 'notepad', 'calculator', 'paint', 
    'file explorer', 'explorer', 'vs code', 'vscode', 'spotify', 
    'task manager', 'cmd', 'terminal', 'word', 'excel', 'powerpoint'
}

# Malicious terminal input execution blacklisted keywords
BLACKLISTED_PATTERNS = {
    'rmdir /s', 'rm -rf', 'format ', 'del /f', 'mkfs', 'shutdown', 
    'attrib -r', 'reg delete'
}

# Fetch the root boundary directory
WORKSPACE_DIR = os.path.abspath(os.getenv("AURA_WORKSPACE_DIR", "c:\\Users\\Nitin\\OneDrive\\Desktop\\aura\\workspace"))

def is_path_safe(target_path):
    """Ensures absolute target_path resides strictly within WORKSPACE_DIR boundary."""
    try:
        # Resolve path to get rid of any relative jumps or traversal tricks
        resolved_target = os.path.abspath(target_path)
        resolved_workspace = os.path.abspath(WORKSPACE_DIR)

        # Simple verification: Does the path start with the workspace root?
        common_path = os.path.commonpath([resolved_target, resolved_workspace])
        
        # If commonpath is exactly workspace root, resolved_target must be inside it
        if common_path == resolved_workspace:
            return True
        return False
    except Exception:
        return False

def is_app_safe(app_name):
    """Checks if requested app resides inside predefined execution whitelist."""
    if not app_name:
        return False
    return app_name.lower().strip() in ALLOWED_APPS

def is_input_safe(text):
    """Pre-verification scanner checks command strings for shell injections or harmful instructions."""
    if not text:
        return True
    
    normalized_text = text.lower()
    for pattern in BLACKLISTED_PATTERNS:
        if pattern in normalized_text:
            return False
    return True
