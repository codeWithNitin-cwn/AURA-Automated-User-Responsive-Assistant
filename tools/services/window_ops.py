import pygetwindow as gw

# ════════════════════════════════════════════
# WINDOW CONTROL
# ════════════════════════════════════════════
def tool_window(params):
    action = params.get('action','')
    target = params.get('target','').lower()
    try:
        if action == 'list':
            wins = [w.title for w in gw.getAllWindows() if w.title.strip()]
            return f"Open windows: {', '.join(wins[:15])}"
        # If no target specified or referring to current/active window
        if not target or target in ('this', 'current', 'window', 'it', 'screen', 'this window', 'current window'):
            active = gw.getActiveWindow()
            if active and active.title.strip():
                if action == 'minimize': active.minimize(); return f"Minimized: {active.title}"
                if action == 'maximize': active.maximize(); return f"Maximized: {active.title}"
            # Fallback to topmost visible window with a title
            visible_wins = [w for w in gw.getAllWindows() if w.title.strip()]
            if visible_wins:
                target_win = visible_wins[0]
                if action == 'minimize': target_win.minimize(); return f"Minimized: {target_win.title}"
                if action == 'maximize': target_win.maximize(); return f"Maximized: {target_win.title}"
            return f"No active window found to {action}."

        wins = [w for w in gw.getAllWindows() if target in w.title.lower()]
        if not wins: return f"No window matching '{target}'."
        if action == 'focus':    wins[0].activate();  return f"Focused: {wins[0].title}"
        if action == 'minimize': wins[0].minimize();  return f"Minimized: {wins[0].title}"
        if action == 'maximize': wins[0].maximize();  return f"Maximized: {wins[0].title}"
        return f"Unknown window action: {action}"
    except Exception as e:
        return f"Window control failed: {e}"
