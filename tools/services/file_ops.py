import os
import glob
import shutil
import subprocess
from security import is_path_safe, WORKSPACE_DIR

# ════════════════════════════════════════════
# UNIVERSAL FILE FINDER
# Searches strictly inside the Workspace sandbox
# ════════════════════════════════════════════
def find_file_everywhere(filename):
    """Search for a file by name recursively inside the WORKSPACE_DIR sandbox."""
    found = []
    if os.path.exists(filename):
        resolved = os.path.abspath(filename)
        if is_path_safe(resolved):
            return [resolved]

    name = os.path.basename(filename) if os.path.sep in filename else filename
    try:
        matches = glob.glob(os.path.join(WORKSPACE_DIR, '**', name), recursive=True)
        for m in matches:
            resolved_m = os.path.abspath(m)
            if is_path_safe(resolved_m):
                found.append(resolved_m)
    except Exception:
        pass
    return found

def resolve_path(path):
    """Resolves relative or absolute path and checks if it falls inside the sandbox.
    Returns: (resolved_path, error_message)
    """
    path = os.path.expandvars(os.path.expanduser(path.strip()))
    
    # If file exists, check sandbox safety
    if os.path.exists(path):
        resolved = os.path.abspath(path)
        if is_path_safe(resolved):
            return resolved, None
        return None, f"Security Block: Access to target path '{resolved}' outside workspace is restricted."

    # Try searching the workspace directory recursively
    name = os.path.basename(path) if os.path.sep in path else path
    results = find_file_everywhere(name)
    if results:
        return results[0], None

    # If it contains path separator but doesn't exist yet, verify target folder safety
    if os.path.sep in path or ':' in path:
        resolved = os.path.abspath(path)
        if is_path_safe(resolved):
            return resolved, None
        return None, f"Security Block: Access to target path '{resolved}' outside workspace is restricted."

    # Otherwise, resolve to root of the workspace directory
    resolved = os.path.abspath(os.path.join(WORKSPACE_DIR, path))
    if is_path_safe(resolved):
        return resolved, None
    return None, f"Security Block: Access to target path '{resolved}' outside workspace is restricted."

# ════════════════════════════════════════════
# READ FILE — sandboxed
# ════════════════════════════════════════════
def tool_read_file(params):
    raw_path = params.get('path', '')
    try:
        path, err = resolve_path(raw_path)
        if err:
            return err
        if not path or not os.path.exists(path):
            return f"Could not find '{raw_path}' inside your workspace."

        size = os.path.getsize(path)
        if size > 50000:
            return f"File too large to read ({size} bytes)."
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)
        return f"Contents of {path}:\n{content}{'...(truncated)' if size > 2000 else ''}"
    except Exception as e:
        return f"Could not read file: {e}"

# ════════════════════════════════════════════
# CREATE FILE — sandboxed
# ════════════════════════════════════════════
def tool_create_file(params):
    raw_path = params.get('path', '')
    content  = params.get('content', '')
    try:
        path, err = resolve_path(raw_path)
        if err:
            return err
        
        dir_ = os.path.dirname(path)
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File created at {path}."
    except Exception as e:
        return f"Could not create file: {e}"

# ════════════════════════════════════════════
# EDIT / APPEND FILE — sandboxed
# ════════════════════════════════════════════
def tool_edit_file(params):
    raw_path = params.get('path', '')
    content  = params.get('content', '')
    mode     = params.get('mode', 'overwrite')
    try:
        path, err = resolve_path(raw_path)
        if err:
            return err
        if not path or not os.path.exists(path):
            return f"Could not find '{raw_path}' inside your workspace. Use create_file to make it first."

        write_mode = 'a' if mode == 'append' else 'w'
        with open(path, write_mode, encoding='utf-8') as f:
            f.write(('\n' if mode == 'append' else '') + content)
        action = "Appended to" if mode == 'append' else "Overwrote"
        return f"{action} {path} successfully."
    except Exception as e:
        return f"Could not edit file: {e}"

# ════════════════════════════════════════════
# DELETE FILE — sandboxed
# ════════════════════════════════════════════
def tool_delete_file(params):
    raw_path = params.get('path', '')
    try:
        path, err = resolve_path(raw_path)
        if err:
            return err

        if not path or not os.path.exists(path):
            return f"Could not find '{raw_path}' inside your workspace."

        if os.path.isfile(path):
            os.remove(path)
            return f"Deleted file: {path}"
        if os.path.isdir(path):
            shutil.rmtree(path)
            return f"Deleted folder: {path}"
        return f"Could not delete '{raw_path}' (unsupported resource type)."
    except Exception as e:
        return f"Could not delete: {e}"

# ════════════════════════════════════════════
# LIST FILES — sandboxed
# ════════════════════════════════════════════
def tool_list_files(params):
    raw_path = params.get('path', 'workspace')
    try:
        guesses = {
            'desktop':   WORKSPACE_DIR,
            'downloads': WORKSPACE_DIR,
            'documents': WORKSPACE_DIR,
            'workspace': WORKSPACE_DIR
        }
        matched = guesses.get(raw_path.lower().strip())
        if matched:
            path = matched
        else:
            path = os.path.expandvars(os.path.expanduser(raw_path))

        resolved = os.path.abspath(path)
        if not is_path_safe(resolved):
            return f"Security Block: Access to target path '{resolved}' outside workspace is restricted."

        if not os.path.exists(resolved):
            return f"Folder not found: {raw_path}"

        items   = os.listdir(resolved)
        files   = [i for i in items if os.path.isfile(os.path.join(resolved, i))]
        folders = [i for i in items if os.path.isdir(os.path.join(resolved, i))]
        return f"In {resolved}:\nFolders ({len(folders)}): {', '.join(folders[:15]) or 'none'}\nFiles ({len(files)}): {', '.join(files[:15]) or 'none'}"
    except Exception as e:
        return f"Could not list files: {e}"

# ════════════════════════════════════════════
# FIND FILE — sandboxed
# ════════════════════════════════════════════
def tool_find_file(params):
    name = params.get('name', '')
    try:
        results = find_file_everywhere(name)
        if not results:
            return f"Could not find '{name}' inside the workspace sandbox."
        return f"Found '{name}' in {len(results)} location(s):\n" + "\n".join(results[:10])
    except Exception as e:
        return f"Search failed: {e}"

# ════════════════════════════════════════════
# OPEN FILE — sandboxed
# ════════════════════════════════════════════
def tool_open_file(params):
    raw_path = params.get('name') or params.get('path', '')
    if not raw_path:
        return "Please specify a file name to open."
    try:
        path, err = resolve_path(raw_path)
        if err:
            return err
        if not path or not os.path.exists(path):
            return f"Could not find '{raw_path}' inside your workspace."
        if not os.path.isfile(path):
            return f"'{raw_path}' is not a file."

        if hasattr(os, 'startfile'):
            os.startfile(path)
        else:
            subprocess.Popen(f'start "" "{path}"', shell=True)
        return f"Opened file: {os.path.basename(path)}"
    except Exception as e:
        return f"Could not open file: {e}"
