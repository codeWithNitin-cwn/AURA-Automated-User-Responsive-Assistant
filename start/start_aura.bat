@echo off
cd /d "%~dp0\.."
echo Starting AURA Microservices from %CD%...

start "AURA Gateway (5000)" cmd /k "python gateway/app.py"
start "AURA ASR (5001)" cmd /k "python asr/asr_service.py"
start "AURA NLP (5002)" cmd /k "python nlp/nlp_service.py"
start "AURA Tools (5003)" cmd /k "python tools/app.py"
start "AURA TTS (5004)" cmd /k "python tts/tts_service.py"
start "AURA Vision (5005)" cmd /k "python vision/vision_service.py"

echo All services launched in separate windows.
