# gateway/app.py
import os
import requests
import socket
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASR_URL    = "http://localhost:5001/transcribe"
NLP_URL    = "http://localhost:5002/parse"
TOOL_URL   = "http://localhost:5003/execute"
TTS_URL    = "http://localhost:5004/speak"
VISION_URL = "http://localhost:5005"

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(os.path.join(BASE_DIR, "static"), path)

@app.route("/")
def home():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")

def run_pipeline(text, use_tts=True):
    """Shared pipeline: text → NLP → Tool (including proxy to Vision) → TTS"""

    # Step 1: NLP
    nlp_resp    = requests.post(NLP_URL, json={"text": text})
    try:
        intent_data = nlp_resp.json()
    except Exception:
        intent_data = None

    if not isinstance(intent_data, dict):
        intent_data = {"tool": "general", "params": {"response": "Sorry, I couldn't understand that."}}

    print(f"[NLP] Intent: {intent_data}")

    # Inject command_text for backend database auditing and logging
    intent_data["command_text"] = text

    # Step 2: Route directly to Tool Service (which coordinates vision execution internally)
    resp   = requests.post(TOOL_URL, json=intent_data)
    result = resp.json()["result"]

    print(f"[RESULT] {str(result)[:150]}")

    # Step 3: TTS (Speech output synthesis)
    audio_url = None
    if use_tts:
        requests.post(TTS_URL, json={"text": str(result)[:500]})
        audio_url = "http://localhost:5004/audio"

    return result, audio_url

# ── VOICE route ─────────────────────────────────────────────
@app.route("/process", methods=["POST"])
def process():
    try:
        audio = request.files.get("audio")

        # ASR (Speech to Text)
        asr_resp = requests.post(ASR_URL, files={"audio": (audio.filename, audio.read(), "audio/webm")})
        text = asr_resp.json()["text"]
        print(f"[ASR] User said: {text}")

        result, audio_url = run_pipeline(text)

        return jsonify({
            "user_said": text,
            "response":  result,
            "audio_url": audio_url
        })
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e), "user_said": "", "response": "Something went wrong!"}), 500

# ── TEXT route ──────────────────────────────────────────────
@app.route("/process_text", methods=["POST"])
def process_text():
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400
        print(f"[TEXT] User typed: {text}")
        result, audio_url = run_pipeline(text, use_tts=False)

        return jsonify({
            "user_said": text,
            "response":  result,
            "audio_url": audio_url
        })
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e), "response": "Something went wrong!"}), 500

# ════════════════════════════════════════════
# SYSTEM STATUS CHECK ENDPOINT
# ════════════════════════════════════════════

def check_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.15)
    try:
        s.connect(("127.0.0.1", port))
        s.close()
        return "Online"
    except:
        return "Offline"

@app.route("/status_check", methods=["GET"])
def status_check():
    ports = {
        "Gateway": 5000,
        "ASR":     5001,
        "NLP":     5002,
        "Tools":   5003,
        "TTS":     5004,
        "Vision":  5005,
    }
    status = {}
    for name, port in ports.items():
        status[name] = check_port(port)
    return jsonify(status)

# ════════════════════════════════════════════
# DATABASE API PROXY ROUTING
# ════════════════════════════════════════════

@app.route("/db/history", methods=["GET"])
def db_history():
    try:
        r = requests.get("http://localhost:5003/db/history", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": f"Could not contact database tools server: {e}"}), 500

@app.route("/db/calendar", methods=["GET"])
def db_calendar():
    try:
        r = requests.get("http://localhost:5003/db/calendar", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": f"Could not contact database tools server: {e}"}), 500

@app.route("/db/security", methods=["GET"])
def db_security():
    try:
        r = requests.get("http://localhost:5003/db/security", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": f"Could not contact database tools server: {e}"}), 500

@app.route("/db/configs", methods=["GET", "POST"])
def db_configs():
    try:
        if request.method == "POST":
            r = requests.post("http://localhost:5003/db/configs", json=request.get_json(), timeout=5)
        else:
            r = requests.get("http://localhost:5003/db/configs", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": f"Could not contact database tools server: {e}"}), 500

if __name__ == "__main__":
    print("Gateway running on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)