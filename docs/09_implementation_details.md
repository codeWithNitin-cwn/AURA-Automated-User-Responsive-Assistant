# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 9: SYSTEM IMPLEMENTATION DETAILS

This chapter documents AURA's technology stack, directory layout, and configuration parameters.

---

### 40. Technology Stack

AURA's technology stack is designed to minimize local hardware requirements while supporting real-time voice interaction.

#### Backend Core Services:
- **Programming Language:** Python 3.10.1 (supports modern asynchronous libraries, system manipulation wrappers, and ML framework runtimes).
- **Service Frame:** Flask 3.0.x (lightweight, routing-flexible micro-web framework suited for local loopback REST endpoints).
- **Cross-Origin Resource Sharing (CORS):** Flask-CORS (allows frontend scripts served from port 5000 to interact with other backend ports).

#### Machine Learning & Inference Engines:
- **Automatic Speech Recognition (ASR):** OpenAI Whisper (runs on local CPU/GPU, transcribing `.webm` format audio files to English text).
- **Multimodal Visual Model:** Llama 4 Scout (`meta-llama/llama-4-scout-17b-16e-instruct` called via Groq API for visual coordinate detection).
- **Natural Language Processing (NLP):** Llama 3.3 (`llama-3.3-70b-versatile` called via Groq API for intent parsing).
- **Text-to-Speech (TTS):** gTTS (Google Text-To-Speech library, converting output strings to MP3 speech).

#### Host Integration & Automation Libraries:
- **System Monitoring:** `psutil` (provides access to CPU and memory usage statistics).
- **Process Orchestration:** Python's standard `subprocess` library (launches application paths).
- **OS Input Simulation:** PyAutoGUI (controls mouse movement, click actions, and key presses).
- **Window Management:** PyGetWindow (queries, focuses, and minimizes application window handles).
- **Display Buffer Interface:** Pillow / `ImageGrab` (captures active screen buffers).

#### Client Interface (Frontend):
- **Structure and Markup:** HTML5 (semantic layout with container elements).
- **Style System:** CSS3 (modern glassmorphic styles, custom properties, and ambient pulse animations).
- **Routing & Client Scripts:** Native JavaScript (Vanilla ES6 modules handling Web Audio API capture and REST execution calls).

---

### 41. Folder Structure

The following directory tree shows the structure of the AURA workspace:

```
aura/
│
├── requirements.txt            # Unified project dependency file
├── README.md                   # Setup instructions and project overview
├── .env                        # Local configuration and API credentials (gitignored)
│
├── asr/                        # Speech-to-Text Service
│   └── asr_service.py          # Whisper model loader and transcribe endpoint
│
├── gateway/                    # Gateway Service & Static Web Client
│   ├── app.py                  # Pipeline controller and routing logic
│   ├── index.html              # Main web UI dashboard
│   ├── styles.css              # Glassmorphic UI styles
│   └── script.js               # Web Audio recorder and client API loops
│
├── nlp/                        # Intent Parser Service
│   └── nlp_service.py          # Groq llama-3.3 controller
│
├── tools/                      # Tool Execution Service
│   ├── tool_service.py         # Filesystem, processes, system stats, window controllers
│   └── calendar.csv            # Local calendar database
│
├── tts/                        # Text-to-Speech Service
│   ├── tts_service.py          # gTTS wrapper and static server
│   └── response.mp3            # Cached audio response file
│
├── vision/                     # Vision Service
│   ├── vision_service.py       # Screenshot capture, coordinate scaler, Groq vision API
│   └── screen.png              # Cached system screenshot file
│
└── start/                      # Service Orchestration Scripts
    ├── run_all.py              # Python process spawner script
    └── start_aura.bat          # Windows batch launcher (starts individual service cmd windows)
```

---

### 42. Configuration Management

AURA manages service settings using local environment variables defined in a `.env` file in the root directory.

#### Environment Variables Schema (`.env`):
```ini
# AURA Environment Configuration Template
# Place this file in the root folder of the project.

# Groq API Credentials (Required for NLP and Vision services)
# Obtain a key from https://console.groq.com/
GROQ_API_KEY=your_actual_groq_api_key_here

# System Port Definitions (Optional - default ports mapped below)
AURA_GATEWAY_PORT=5000
AURA_ASR_PORT=5001
AURA_NLP_PORT=5002
AURA_TOOLS_PORT=5003
AURA_TTS_PORT=5004
AURA_VISION_PORT=5005
```

#### Port Mapping Table:
If default ports conflict with existing services, developers can update the port mapping in the service source files:
- **Gateway Service:** Bind target: `0.0.0.0:5000` (accessible within local network).
- **ASR Service:** Bind target: `127.0.0.1:5001`.
- **NLP Service:** Bind target: `127.0.0.1:5002`.
- **Tool Service:** Bind target: `127.0.0.1:5003`.
- **TTS Service:** Bind target: `127.0.0.1:5004`.
- **Vision Service:** Bind target: `127.0.0.1:5005`.
