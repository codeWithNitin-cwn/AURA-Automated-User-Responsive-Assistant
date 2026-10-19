# AURA Capstone Project Viva & Review Guide
## Project Title: AURA – A Microservice-Based Autonomous Universal Response Assistant for Voice-Driven Intelligent Desktop Automation

This guide is prepared to help you ace your capstone project review tomorrow. It explains the exact technology stack, service architecture, communication flows, database schemas, security configurations, and provides a list of probable examiner questions with high-scoring B.Tech-level answers.

---

## 1. System Architecture & Communication Flow

AURA is designed as a **decentralized microservices architecture** rather than a traditional monolith. This separation provides modularity, easy scaling, and independent service lifecycles (if one service fails, the others remain online).

### Service Topology & Ports
The suite consists of **six** distinct Flask-based microservices communicating via HTTP REST APIs (JSON payloads):

| Service Name | Port | Primary Responsibility | Core Tech / Model Used |
| :--- | :--- | :--- | :--- |
| **Gateway Orchestrator** | `5000` | Static file hosting (UI), routing, orchestration, database proxy, health check. | Python (Flask), HTML5, CSS3, Vanilla JS, Fetch API |
| **ASR (Speech-to-Text)** | `5001` | Transcribes audio recordings from the browser. | OpenAI **Whisper (`base` model)** (runs locally offline) |
| **NLP (Intent Parser)** | `5002` | Semantic analysis and parameters extraction from prompt. | **Groq Cloud (`llama-3.3-70b-versatile`)** / Local **Ollama (`llama3.2`)** |
| **Tools Executor** | `5003` | Executes shell commands, searches web, updates calendar/email, files, apps. | PostgreSQL (psycopg2), PyAutoGUI, Subprocess, psutil, DuckDuckGo HTML |
| **TTS (Speech Synthesis)** | `5004` | Synthesizes response text back to voice output. | **gTTS** (Google Text-to-Speech), returns MP3 stream |
| **Vision Service** | `5005` | Screen capturing, OCR search, dynamic icon detection. | **Groq Cloud (`llama-4-scout-17b`)** / Local **Ollama (`llava`)**, Pillow, PyAutoGUI |

```
                     ┌─────────────────────────┐
                     │  Browser UI (Port 5000) │
                     └────────────┬────────────┘
                                  │ HTTP / JSON
                                  ▼
                      ┌───────────────────────┐
                      │  Gateway Orchestrator │
                      └─────┬───────────┬─────┘
                            │           │
        ┌───────────────────┘           └───────────────────┐
        ▼ (Port 5001)                                       ▼ (Port 5002)
 ┌──────────────┐                                    ┌──────────────┐
 │  ASR Service │                                    │  NLP Service │
 │  (Whisper)   │                                    │ (Groq/Ollama)│
 └──────────────┘                                    └──────────────┘
        │                                                   │
        ├───────────────────────────────────────────────────┤
        ▼ (Port 5003)                                       ▼ (Port 5005)
 ┌──────────────┐                                    ┌──────────────┐
 │ Tool Service │                                    │Vision Service│
 │ (OS Actions) │◄───────────────────────────────────┤ (Groq/Ollama)│
 └──────────────┘                                    └──────────────┘
        │
        └───────────────────────────┬───────────────────────┘
                                    ▼ (Port 5004)
                             ┌──────────────┐
                             │  TTS Service │
                             │    (gTTS)    │
                             └──────────────┘
```

### Complete End-to-End Processing Pipeline (Voice Input Flow)
1. **User Voice Capture:** The browser UI records user voice as a WebM audio stream using the browser's MediaRecorder API and posts it to Gateway (`/process`).
2. **Speech Transcription:** Gateway sends the raw WebM bytes to the ASR Service (`:5001/transcribe`). The local Whisper model transcribes it to text.
3. **Intent Parsing:** Gateway forwards the transcribed text to the NLP Service (`:5002/parse`). The LLM reads it, maps it to a tool, extracts execution parameters, and returns a JSON schema (e.g. `{"tool": "open_app", "params": {"target": "chrome"}}`).
4. **Security Filtering:** Gateway passes the JSON to the Tools Service (`:5003/execute`). It executes a safety scan:
   - Evaluates command strings for malicious terminal keywords (blacklist).
   - Validates paths to ensure directory confinement inside the sandboxed workspace folder (preventing path traversal).
   - Verifies target programs against an allowed application whitelist.
5. **Tool Execution:** The Tools Service executes the mapped Python function. (If the task requires visual coordination, e.g. "click Chrome icon", Tools calls the Vision Service (`:5005/click_icon`) which grabs a screen buffer, passes it to a multimodal model to find coordinates, scales them to the host resolution, and executes clicks with `pyautogui`).
6. **Auditing & Logs:** The Tools Service inserts audit trails into the PostgreSQL database (`execution_logs`, `security_logs`, or `calendar_events` tables).
7. **Voice Synthesis:** The tool execution response text is routed to the TTS Service (`:5004/speak`). gTTS generates an MP3 response stream.
8. **Feedback Loop:** Gateway receives the text outcome and MP3 stream url, feeding them back to the browser UI to display in the chat terminal and auto-play the voice.

---

## 2. Database Models & Schema Design (PostgreSQL)

AURA utilizes a local **PostgreSQL** relational database (`aura_db`) for auditing, configuration persistence, and scheduling. It automatically boots and seeds schemas on startup.

### Entity Relationship & Tables
The database consists of **four** core tables:

1. **`execution_logs`** (System Auditing)
   * Track every run command for transparency, troubleshooting, and profiling.
   * *Schema:* `id (SERIAL, PK)`, `timestamp (TIMESTAMP)`, `command_text (TEXT)`, `tool_name (VARCHAR)`, `status (VARCHAR)`, `result (TEXT)`.

2. **`security_logs`** (Intrusion Detection System - IDS)
   * Records details of any blocked attempt to bypass sandboxing rules, whitelist exceptions, or blacklist triggers.
   * *Schema:* `id (SERIAL, PK)`, `timestamp (TIMESTAMP)`, `command_text (TEXT)`, `violation_type (VARCHAR)`, `target_resource (TEXT)`.

3. **`calendar_events`** (Schedule Data Store)
   * Local scheduled calendar event storage.
   * *Schema:* `id (SERIAL, PK)`, `title (VARCHAR)`, `event_time (VARCHAR)`, `action (VARCHAR)`, `created_at (TIMESTAMP)`.

4. **`system_configs`** (Environment Config Persistence)
   * Key-value parameters that change agent behavior.
   * *Schema:* `config_key (VARCHAR, PK)`, `config_value (TEXT)`, `updated_at (TIMESTAMP)`.
   * *Seeded values:* `llm_provider` ('GROQ'), `sandbox_dir` ('c:\Users\Nitin\OneDrive\Desktop\aura\workspace'), `safe_mode` ('True').

---

## 3. Security Framework & Guardrails

Since AURA interacts directly with the operating system, it enforces a multi-layer security grid to prevent malicious or accidental system destruction:

1. **Path-Confinement Sandboxing:**
   * Any file read, write, create, or delete operation resolves absolute target paths and compares them against `WORKSPACE_DIR` using `os.path.commonpath`. If the target resolves outside this directory, a `Security Block` is triggered and logged to `security_logs`.
2. **Application Launch Whitelisting:**
   * The `open_app` intent checks a whitelisted dictionary (`ALLOWED_APPS`) consisting only of safe programs (e.g. Chrome, Notepad, VLC, VS Code, Paint, CMD). Unknown executables or shell command injection parameters are strictly blocked.
3. **Keyword Blacklist Scanner:**
   * High-risk terminal keywords (e.g. `rmdir /s`, `rm -rf`, `format `, `del /f`, `reg delete`, `attrib -r`) are scanned prior to parsing or execution. If matched, the command is instantly rejected.
4. **PyAutoGUI Safety Boundaries:**
   * Set `pyautogui.FAILSAFE = True`. If a visual action goes haywire, the user can slam the mouse cursor into any corner of the screen to throw an exception and instantly kill execution.

---

## 4. B.Tech Viva Questions & Answers (Examiner Prep)

Here are the most likely questions examiners will ask during your project review, alongside highly technical, structured answers to impress them.

### General & Architecture Questions

#### Q1: Why did you choose a Microservices architecture instead of a Monolithic one?
**Answer:** 
* "A microservices design decouples AURA's modules—ASR, NLP, Tools, Vision, and TTS—each of which has entirely different dependency profiles and compute requirements. For instance, Whisper requires heavy ML libraries (`torch`, `numpy`), whereas the Gateway only needs lightweight Flask. 
* Decoupling them allows independent scaling, modular testing, and fault isolation. If our external NLP or TTS services fail, the local speech-to-text and offline tools remain active. We can also hot-swap services (e.g., swapping cloud Groq APIs for a local Ollama model) without changing a single line of code in the Gateway UI or Tools service."

#### Q2: Explain the role of the Gateway Orchestrator in this system.
**Answer:** 
* "The Gateway acts as a Single Point of Entry (API Gateway) for the frontend client. It serves static HTML/CSS/JS files, exposes CORS-enabled endpoints (`/process` for audio, `/process_text` for text), orchestrates the synchronous execution of ASR → NLP → Tools → TTS pipelines, and proxies database queries (e.g., retrieving calendar, audit, or security logs from the Tools service) to keep port mappings clean for the client browser."

#### Q3: How do the services communicate? What happens if there's a slow network connection?
**Answer:** 
* "Services communicate locally over standard HTTP loopback (`127.0.0.1`) on dedicated ports (5000 through 5005) using JSON request/response bodies. 
* Because execution is local, latency between microservices is sub-millisecond. For external cloud APIs (NLP and Vision via Groq), we implement robust error handling, response timeouts, and an automatic offline fallback system that routes the payload to a local Ollama service running `llama3.2` or `llava` on port 11434."

---

### Machine Learning, ASR & NLP Questions

#### Q4: Tell us about the Automatic Speech Recognition (ASR) module. Why Whisper? Does it run locally?
**Answer:** 
* "The ASR service runs locally using OpenAI's **Whisper (`base` model)** loaded via the `whisper` Python package. We chose Whisper because of its high robustness to background noise and accents compared to standard speech recognition APIs. 
* The browser records audio as a WebM file, which is sent as a multipart form-data POST request to `/transcribe`. The service saves this to a temporary file, uses Whisper to transcribe it to text, deletes the temp file, and returns the string in a JSON wrapper. Running Whisper locally keeps voice data offline, ensuring user privacy."

#### Q5: How does the NLP Service parse intents? What model is running?
**Answer:** 
* "The NLP Service translates unstructured user voice transcripts into structured JSON payloads. We configure Groq's high-speed API to run `llama-3.3-70b-versatile` under a zero-temperature environment (T=0.1) for deterministic output, guided by a system instruction prompt. 
* The prompt instructs the LLM to output *only* valid JSON conforming to our tool dispatch tables. For example: `{"intent": "open_app", "tool": "open_app", "params": {"target": "chrome"}}`. If the system is offline or Groq fails, the system automatically redirects requests to a local instance of **Ollama (`llama3.2`)**."

---

### Tools & OS Automation Questions

#### Q6: How does AURA execute local desktop commands? What libraries did you use?
**Answer:** 
* "We use Python's built-in `subprocess` module with `shell=True` to execute OS commands or launch processes, combined with `pyautogui` for mouse/keyboard automation, and `psutil` to query system telemetry (RAM, CPU, active windows). 
* For web searches, we use the `duckduckgo_search` library (specifically `DDGS().text`) to fetch lite search results programmatically without needing expensive search engine API keys."

#### Q7: How does the Vision Service work? How does it 'see' and click elements?
**Answer:** 
* "When a user asks AURA to click a screen element (e.g., 'click the chrome icon'), the Gateway routes the task to the Tools Service, which triggers the Vision helper.
* The Vision service takes a desktop screenshot via Python's Pillow library (`ImageGrab.grab`), resizes it to 1280x720 to optimize token usage, and sends it as a base64 string to a multimodal model (**`llama-4-scout-17b`** via Groq or **`llava`** via Ollama). 
* We prompt the model to find the specific element and return a JSON containing normalized coordinates (e.g., `{"found": true, "x": 123, "y": 456}`). The Vision service scales these coordinates back to the system's actual resolution using `pyautogui.size()`, moves the mouse to the target, and executes a click."

---

### Database & Security Questions

#### Q8: What database are you using, and what schemas are implemented?
**Answer:** 
* "We use **PostgreSQL** running locally on port 5432, integrated via `psycopg2`. The database initialization routine (`init_db`) connects to the local server, creates `aura_db` if it doesn't exist, and creates four tables: 
  1. `execution_logs` (recording the command, tool run, timestamp, and results)
  2. `security_logs` (tracking security blocks and violation details)
  3. `calendar_events` (storing calendar titles, times, and actions)
  4. `system_configs` (storing dynamic parameters like the chosen LLM provider and sandbox directories)."

#### Q9: What happens if a user inputs a command like "delete all files in System32"? How does your security layer handle it?
**Answer:** 
* "We implemented a multi-stage security grid:
  1. **Blacklist Scanning:** Before parsing, the command string is scanned. If it contains dangerous system patterns (like `del /f`, `rmdir /s`, or `rm -rf`), execution is aborted immediately, logged to `security_logs`, and returns a safety warning.
  2. **Path Sandboxing:** If a user tries to access files outside the project, our `resolve_path` function uses `os.path.commonpath` to ensure the resolved file path resides strictly inside `c:\Users\Nitin\OneDrive\Desktop\aura\workspace`. If it escapes the sandbox, a `Security Block` is returned and logged.
  3. **Application Whitelisting:** Attempts to launch arbitrary executables are checked against a predefined `ALLOWED_APPS` set (e.g. notepad, chrome, vscode). Unlisted apps are blocked."

#### Q10: How does path-confinement sandboxing prevent path traversal attacks (like `../../windows`)?
**Answer:** 
* "We pass the user's path parameter through Python's `os.path.abspath()`. This resolves all relative directories, symlinks, and directory traversal dots (`..`) into a single canonical absolute path. We then check if the absolute path starts with our absolute workspace directory. If it doesn't share that common root, it is flagged as a traversal attack and blocked."

---

### Integration & Quality Assurance Questions

#### Q11: How do you verify the health of all services?
**Answer:** 
* "The Gateway service exposes a `/status_check` GET endpoint. When requested, it attempts to open a quick socket connection (`socket.socket`) to localhost on ports 5000, 5001, 5002, 5003, 5004, and 5005. If a connection is accepted within a 150ms timeout, the service is reported as 'Online'. Otherwise, it is listed as 'Offline'. This status is displayed dynamically in the browser UI."

#### Q12: What are the primary limitations of the current prototype?
**Answer:** 
* "The main limitations are:
  1. **Internet Dependency for Cloud LLMs:** While ASR and file tools can run fully offline, intent parsing and vision require active internet connections for Groq APIs (unless the user switches to the local Ollama provider).
  2. **Whisper Init Latency:** On the very first run, Whisper must download its weights (~140MB), requiring internet.
  3. **Single-User Scope:** The assistant is designed for a single local developer environment and lacks multi-tenant user authentication."

#### Q13: How can you scale or improve this project in the future?
**Answer:** 
* "We can improve the project by:
  1. Integrating local, optimized visual language models (like **Llama 3.2 Vision** or **Qwen2-VL**) directly into the pipeline to eliminate Groq API dependencies for screen control.
  2. Adding voice biometric authentication (speaker verification) so only the owner can issue local terminal commands.
  3. Implementing WebSockets for full-duplex streaming audio, enabling real-time voice interruptions rather than recording discrete chunks."

---

## 5. Quick Troubleshooting Cheat Sheet for Viva Demo
If anything acts up during the live demo tomorrow, check this list immediately:

1. **Database connection failed / psycopg2 error:**
   * Make sure PostgreSQL is running on your machine: Open `services.msc` and check that the `postgresql-x64` service is running.
2. **FFmpeg error on launch:**
   * Whisper requires FFmpeg. Ensure `ffmpeg` is downloaded and added to your system Environment variables path (`PATH`).
3. **No audio responses:**
   * Ensure your speakers/volume are up and that the TTS service is running on port 5004. You can visit `http://localhost:5004/audio` directly to check if a voice MP3 plays.
4. **LLM authentication error:**
   * Check your `.env` file in the root folder. Verify that `GROQ_API_KEY` is present and valid.

---
**Good luck with your Capstone Viva review! You have built a highly secure, modular, and functional AI OS agent. You've got this!**
