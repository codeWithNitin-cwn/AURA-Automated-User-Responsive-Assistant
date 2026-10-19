import psutil
import platform
from datetime import datetime

# ════════════════════════════════════════════
# SYSTEM INFO
# ════════════════════════════════════════════
def tool_system_info(params):
    query = params.get('query','all').lower()
    try:
        info = {}
        if query in ('all','cpu'):
            info['CPU Usage'] = f"{psutil.cpu_percent(interval=1)}%"
            info['CPU Cores'] = psutil.cpu_count()
        if query in ('all','memory','ram'):
            mem = psutil.virtual_memory()
            info['RAM Total']     = f"{mem.total//(1024**3)} GB"
            info['RAM Used']      = f"{mem.used//(1024**3)} GB"
            info['RAM Available'] = f"{mem.available//(1024**3)} GB"
            info['RAM %']         = f"{mem.percent}%"
        if query in ('all','disk'):
            disk = psutil.disk_usage('C:\\')
            info['Disk Total'] = f"{disk.total//(1024**3)} GB"
            info['Disk Free']  = f"{disk.free//(1024**3)} GB"
        if query in ('all','system','os'):
            info['OS']       = platform.system()+' '+platform.release()
            info['Hostname'] = platform.node()
        if query in ('all','battery'):
            b = psutil.sensors_battery()
            if b: info['Battery'] = f"{b.percent}% {'(charging)' if b.power_plugged else ''}"
        return "\n".join(f"{k}: {v}" for k,v in info.items()) or "No info."
    except Exception as e:
        return f"System info failed: {e}"

# ════════════════════════════════════════════
# GET TIME / DATE
# ════════════════════════════════════════════
def tool_get_time(params):
    now = datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')} and today is {now.strftime('%A, %d %B %Y')}."
