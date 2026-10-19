# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 4: SYSTEM QUALITIES & OPERATIONAL RULES

---

### 16. Non-Functional Requirements

#### Performance:
- **ASR Latency:** Voice transcribing on the local Whisper base service must complete within 1.5 seconds for audio clips under 5 seconds.
- **NLP Turnaround:** The intent parsing service must respond within 800 milliseconds.
- **UI Responsiveness:** The web-based dashboard must render message responses in under 200 milliseconds after receiving the Gateway payload.

#### Reliability:
- **ASR Error Tolerance:** The system must gracefully handle background noise, returning a fallback transcription string ("sorry I could not hear that") instead of crashing the process.
- **Failure Recovery:** If the Vision service or Tool service crashes, the Gateway must capture the exception and remain online to handle subsequent requests.

#### Security:
- **No Hardcoded Credentials:** The system must restrict the use of hardcoded keys, loading the `GROQ_API_KEY` from a local `.env` file.
- **Sandbox Boundary:** Low-level file actions must be restricted to user directories (Desktop, Documents, Downloads, Pictures) to prevent modification of critical OS directories.

#### Scalability:
- **Independent Scaling:** Since services run on individual ports, CPU-bound tasks like Whisper ASR and GPU-bound components can be scaled independently on separate hosts or Docker nodes.

#### Availability:
- **Local Availability:** When running offline, all core components (Gateway, ASR, Tools, TTS) must remain operational, disabling only cloud-dependent features (NLP, Vision, Web Search).

#### Maintainability:
- **Modularity:** Adding a new tool to the Tool service must require only writing a Python function and registering it in the intent mapping dictionary.

#### Usability:
- **Accessibility Support:** The interface must feature high-contrast modes, readable font scales (Syne, Instrument Serif, DM Mono), and real-time screen descriptions for visually impaired users.

#### Portability:
- **Cross-Platform Compatibility:** The codebase must run on Windows 10/11, macOS, and Linux configurations with minimal environment modifications.

#### Compatibility:
- **Python Compatibility:** The software must be fully compatible with Python versions 3.8 through 3.11.

#### Privacy:
- **On-Device Processing:** Raw audio recordings must be written, processed, and deleted locally, ensuring voice biometric data does not leave the host machine.

#### Accessibility:
- **Keyboard Access:** All UI actions must be accessible using standard keyboard navigation shortcuts (Tab, Enter).

#### Logging:
- **Central Log System:** Each service must output structured terminal logs detailing incoming requests, execution times, and status results.

#### Recovery:
- **State Reset:** If execution locks up or encounters an error, the user can reset the system state by clicking the central logo orb.

---

### 17. Business Rules

- **Voice commands must be validated before execution:** Intent parameters must be checked against system boundaries before calling python automation scripts.
- **Tool execution must occur only after successful intent recognition:** The execution service must reject payloads lacking a valid intent mapping.
- **Invalid commands must return clarification:** If the confidence of the NLP intent parser drops below a set threshold, it must ask the user for clarification.
- **Each microservice must be independently deployable:** Services must not have hard dependencies on shared libraries, using only REST endpoints to communicate.
- **Services communicate only through REST APIs:** No direct memory sharing or inter-process communication is permitted outside of standard HTTP requests.
- **Sensitive credentials must never be hardcoded:** Any required API keys must be loaded from local environment variables.
- **Voice responses must only be generated after successful task completion:** The TTS engine should only speak after the target action returns a status code.

---

### 18. Assumptions

- The host system has a functional microphone input configured at the OS level.
- The host system has active internet access to resolve cloud-based Groq API calls.
- The system shell running the python scripts has write access to the user's Desktop, Downloads, and Documents folders.
- FFmpeg is correctly installed and registered in the host system's PATH.

---

### 19. Constraints

- **Single-Threaded Execution:** Because PyAutoGUI takes control of the physical mouse cursor, only one visual clicking operation can run at any given time.
- **Hardware Limitations:** The local Whisper ASR service requires at least 2GB of free system memory to load model weights.
- **API Limits:** Groq API calls are subject to external rate limits (requests per minute and tokens per minute).

---

### 20. Use Cases

```
  ┌────────────────────────────────────────────────────────┐
  │ AURA System Boundary                                   │
  │                                                        │
  │                   ┌──────────────┐                     │
  │  ┌───────────────►│  Voice Input │                     │
  │  │                └──────────────┘                     │
  │  │                                                     │
  │  │                ┌──────────────┐                     │
  │  ├───────────────►│  File Action │                     │
  │  │                └──────────────┘                     │
  │  │                                                     │
  │  │                ┌──────────────┐                     │
  │  ├───────────────►│  System Info │◄─────────┐          │
  │  │                └──────────────┘          │          │
  │  │                                          │          │
  │  │                ┌──────────────┐          │          │
  │  ├───────────────►│ Vision Click │          │          │
  │  │                └──────────────┘          │          │
  │  │                                          │          │
  │  │                ┌──────────────┐          │          │
  │  └───────────────►│  Web Search  │          │          │
  │                   └──────────────┘          │          │
  │                                             │          │
  └─────────────────────────────────────────────┼──────────┘
                                                │
     ▲                                          ▲
     │                                          │
┌────┴────────┐                          ┌──────┴──────┐
│   User      │                          │ System APIs │
└─────────────┘                          └─────────────┘
```

#### Use Case UC-1: Perform System Action via Voice Command
- **Actor:** User
- **Description:** The user speaks a command to perform a system action (e.g., launching an application or checking RAM).
- **Flow of Events:**
  1. User clicks the microphone button and speaks: "What is my RAM usage?"
  2. The system records the voice input.
  3. The ASR service transcribes the audio to text.
  4. The NLP service parses the text and identifies the target tool (`system_info`).
  5. The Tool service runs the system check and retrieves RAM metrics.
  6. The system reads the results back to the user via TTS.

#### Use Case UC-2: Vision-Based Visual Automation
- **Actor:** User
- **Description:** The user asks AURA to open a application visible on the screen by name.
- **Flow of Events:**
  1. The user speaks: "Open Recycle Bin".
  2. The ASR service transcribes the command.
  3. The NLP service parses the command as a `click_icon` action with parameters `{"target": "Recycle Bin"}`.
  4. The Gateway routes the request to the Vision Service.
  5. The Vision Service captures a screenshot, downscales it to 720p, and sends it to the Groq vision API.
  6. The API returns the screen coordinates of the Recycle Bin icon.
  7. The Vision Service translates the coordinates and clicks the icon.

---

### 21. User Stories

1. **File Management:** "As a developer, I want to create and edit files using voice commands so that I can quickly log ideas without switching from my editor."
2. **Hands-Free System Info:** "As a system administrator, I want to check my system resource usage (RAM/CPU) using voice queries so that I can monitor system load while working on full-screen applications."
3. **Accessibility Assistance:** "As a user with limited motor function, I want to click screen buttons and control desktop windows using natural language, helping me navigate my computer without a physical mouse."

---

### 22. Acceptance Criteria

- **AC-1 (Voice Accuracy):** The system must transcribe voice inputs with at least 90% accuracy in quiet environments.
- **AC-2 (Execution Verification):** File creation commands must verify that the file exists on disk before returning a success message.
- **AC-3 (Fail-Safe Trigger):** In visual clicking tasks, if the target coordinates fall outside system bounds, the cursor must return to the center of the screen without executing clicks.
- **AC-4 (API Configuration):** The system must fail gracefully and notify the user if no valid `GROQ_API_KEY` is present in the configuration.
