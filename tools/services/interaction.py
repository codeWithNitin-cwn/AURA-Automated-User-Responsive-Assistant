import pyautogui
import os
import time

# ════════════════════════════════════════════
# MOUSE CONTROL
# ════════════════════════════════════════════
def tool_mouse(params):
    action = params.get('action', '')
    try:
        if action == 'click':
            x, y = params.get('x'), params.get('y')
            if x and y:
                pyautogui.click(int(x), int(y))
                return f"Clicked at ({x}, {y})."
            pyautogui.click()
            return "Clicked."
        elif action == 'move':
            pyautogui.moveTo(int(params.get('x',500)), int(params.get('y',500)), duration=0.5)
            return "Moved mouse."
        elif action == 'scroll_up':
            pyautogui.scroll(int(params.get('amount', 3)))
            return "Scrolled up."
        elif action == 'scroll_down':
            pyautogui.scroll(-int(params.get('amount', 3)))
            return "Scrolled down."
        elif action == 'right_click':
            pyautogui.rightClick(); return "Right clicked."
        elif action == 'double_click':
            pyautogui.doubleClick(); return "Double clicked."
        elif action == 'position':
            x, y = pyautogui.position(); return f"Mouse at ({x}, {y})."
        return f"Unknown mouse action: {action}"
    except Exception as e:
        return f"Mouse failed: {e}"

# ════════════════════════════════════════════
# KEYBOARD CONTROL
# ════════════════════════════════════════════
def tool_keyboard(params):
    action = params.get('action', '')
    try:
        if action == 'type':
            pyautogui.typewrite(params.get('text',''), interval=0.04)
            return f"Typed: {params.get('text','')}"
        elif action == 'hotkey':
            pyautogui.hotkey(*[k.strip() for k in params.get('keys','').split('+')])
            return f"Pressed: {params.get('keys','')}"
        elif action == 'press':
            pyautogui.press(params.get('key',''))
            return f"Pressed: {params.get('key','')}"
        elif action == 'screenshot':
            path = os.path.join(os.path.expanduser('~\\Desktop'), f'screenshot_{int(time.time())}.png')
            pyautogui.screenshot(path)
            return "Screenshot saved to Desktop."
        return f"Unknown keyboard action: {action}"
    except Exception as e:
        return f"Keyboard failed: {e}"

# ════════════════════════════════════════════
# VOLUME
# ════════════════════════════════════════════
def tool_volume(params):
    action = params.get('action','')
    amount = int(params.get('amount', 5))
    try:
        if action == 'up':
            for _ in range(amount): pyautogui.press('volumeup')
            return f"Volume up by {amount}."
        elif action == 'down':
            for _ in range(amount): pyautogui.press('volumedown')
            return f"Volume down by {amount}."
        elif action == 'mute':
            pyautogui.press('volumemute'); return "Muted."
        return "Say volume up, down, or mute."
    except Exception as e:
        return f"Volume failed: {e}"
