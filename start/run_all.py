import os
import subprocess
import sys
import psutil

# Get root directory of project
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
env_path = os.path.join(project_root, ".env")

# List of services to run
services = [
    "gateway/app.py",
    "asr/asr_service.py",
    "nlp/nlp_service.py",
    "tools/app.py",
    "tts/tts_service.py",

]

# 1. Kill any existing instances of AURA services to prevent port collisions and stale background code
print("Checking for stale AURA services to terminate...")
current_pid = os.getpid()
killed_count = 0
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Skip current process
        if proc.info['pid'] == current_pid:
            continue
        
        # Check if process is Python and running one of our services
        cmdline = proc.info['cmdline']
        if cmdline and any('python' in arg.lower() for arg in cmdline):
            for service in services:
                service_name = os.path.basename(service)
                # If the service file name is in the arguments, kill it
                if any(service_name in arg for arg in cmdline):
                    print(f"Terminating stale service process {proc.info['pid']} ({service_name})...")
                    proc.kill()
                    killed_count += 1
                    break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

if killed_count > 0:
    print(f"Successfully cleaned up {killed_count} stale service processes.")
else:
    print("No stale AURA services found.")

print("-" * 60)

# 2. Run setup wizard if .env is missing
if not os.path.exists(env_path):
    # Import setup_wizard and run it
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from setup_wizard import run_setup
    success = run_setup()
    if not success:
        print("Setup failed. Exiting startup.")
        sys.exit(1)

# 3. Start each service as a separate background process
procs = []
for service in services:
    service_path = os.path.join(project_root, service)
    p = subprocess.Popen(
        [sys.executable, service_path],
        cwd=project_root
    )
    procs.append(p)

print("All AURA services started successfully. Press Ctrl+C to stop all.")
try:
    for p in procs:
        p.wait()
except (KeyboardInterrupt, SystemExit):
    for p in procs:
        try:
            p.terminate()
        except:
            pass

