# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 2: EXISTING SYSTEM & USER SPECIFICATION

---

### 9. Existing System Analysis

Legacy desktop voice controllers typically fall into two categories: generic cloud assistants or basic scripting frameworks.

#### Cloud Assistants (Cortana, Siri, Google Assistant):
- **Architecture:** Cloud-centric, monolithic black boxes.
- **Vulnerabilities:**
  - **High Latency:** Raw audio data is sent over WAN to distant cloud servers, parsed, and sent back as text before any execution occurs.
  - **Telemetry and Privacy Risks:** Constant logging of user speech patterns, environment audio, and local system paths.
  - **No System Integration:** Security boundaries prevent these assistants from accessing the local shell or running arbitrary developer-defined script files.

#### Custom Scripting Frameworks (Siri Shortcuts, AutoHotkey, VoiceAttack):
- **Architecture:** Rule-based local macro systems.
- **Vulnerabilities:**
  - **Brittle Rule Matching:** Users must match commands *exactly* (e.g., "Open chrome" will succeed, but "Launch my web browser" will fail if not hardcoded).
  - **No Contextual Vision:** They cannot inspect screen contents to click dynamic elements without hardcoding absolute X/Y pixel coordinates.

---

### 10. Proposed System

AURA solves these limitations by implementing a local microservice architecture that combines local edge models with cloud LLMs.

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
│  (Whisper)   │                                    │   (Groq)     │
└──────────────┘                                    └──────────────┘
       │                                                   │
       ├───────────────────────────────────────────────────┤
       ▼ (Port 5003)                                       ▼ (Port 5005)
┌──────────────┐                                    ┌──────────────┐
│ Tool Service │                                    │Vision Service│
│ (OS Actions) │                                    │   (Groq)     │
└──────────────┘                                    └──────────────┘
       │                                                   │
       └───────────────────┬───────────────────────────────┘
                           ▼ (Port 5004)
                    ┌──────────────┐
                    │  TTS Service │
                    │    (gTTS)    │
                    └──────────────┘
```

#### Core Components of the Proposed Solution:
1. **Edge ASR:** Raw audio capture is processed entirely on the local loopback (`127.0.0.1:5001`) via Whisper, keeping audio files on the local machine.
2. **Context-Aware Intent Parsing:** High-performance LLMs parse commands into structured JSON dynamically, accommodating a wide range of natural phrasing.
3. **Multimodal GUI Control:** The Vision Service takes local screenshots and uses visual reasoning models to determine element locations, allowing AURA to interact with application interfaces.
4. **Independent Service Lifecycle:** If one service fails, the remaining infrastructure remains online.

---

### 11. System Overview

AURA operates by chaining specialized microservices via REST API calls. 

1. The frontend client (running in a local browser sandbox) records the user's voice input and POSTs it to the Gateway `/process` endpoint.
2. The Gateway forwards the binary audio payload to the ASR Service (`:5001/transcribe`), receiving a clean text string in response.
3. The transcribed text is sent to the NLP Service (`:5002/parse`), which returns a JSON payload detailing the target tool and required parameters.
4. If the intent requires visual reasoning, the Gateway routes the request to the Vision Service (`:5005`); otherwise, it targets the Tool Service (`:5003/execute`).
5. The selected service runs the command locally (e.g., creating a file or clicking an icon) and returns the text result.
6. The Gateway sends the text result to the TTS Service (`:5004/speak`) to generate an audio response, and then returns both the text output and audio URL back to the frontend.

---

### 12. Stakeholders

- **Student Evaluators / Project Coordinators:** Academics reviewing the system's software architecture, code quality, and engineering documentation.
- **Power Users / Developers:** Users seeking a hands-free, scriptable interface to control their local environment, manage files, and launch applications.
- **Accessibility Users:** Individuals with motor impairments who require reliable, voice-driven system control and visual screen reading.

---

### 13. User Roles

1. **System Operator (End-User):**
   - Interacts with the interface via voice or text input.
   - Grants permissions for high-risk operations.
   - Configures API keys and local settings.
2. **System Developer (Administrator):**
   - Adds custom tools to the Tool Service registry.
   - Monitors port configurations, logs, and system metrics.
   - Optimizes local model weights and execution environments.

---

### 14. User Requirements

- **Voice/Text Toggle:** The user must be able to switch between voice control and typed text input in the UI.
- **Low Latency:** The round-trip pipeline from voice command to execution must finish in under 3.5 seconds.
- **Hands-Free Verification:** The user must receive spoken and visual feedback confirming whether tasks succeeded or failed.
- **Data Privacy Control:** API keys must be stored in a local configuration file (`.env`), and no local audio clips should be sent to cloud storage.
- **System Stability:** Low-level OS execution should not crash the computer or overwrite critical system files.
- **GUI Control:** The system must allow users to click screen buttons and read active screen contents using natural language.
