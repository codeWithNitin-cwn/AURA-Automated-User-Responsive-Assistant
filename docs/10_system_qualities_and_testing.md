# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 10: QUALITY ASSURANCE & TESTING STRATEGY

This chapter outlines the security, privacy, logging, and error-handling strategies, followed by a testing plan and verified test cases.

---

### 43. Security Requirements

- **Local Network Boundary:** All microservices (ASR, NLP, Tools, TTS, Vision) must bind exclusively to localhost (`127.0.0.1`), preventing remote systems from executing commands on the host machine. Only the Gateway Service binds to `0.0.0.0` to serve the web interface.
- **Input Sanitization:** Filesystem tools must sanitize input paths using `os.path.basename` and resolve parent paths to prevent directory traversal attacks (e.g., path strings containing `../`).
- **Process Verification:** Application launch requests must match a predefined list of allowed processes (Chrome, Notepad, VS Code, Calculator, Command Prompt) to prevent execution of arbitrary binary files.

---

### 44. Privacy Requirements

- **Voice Isolation:** Raw audio files captured by the browser microphone must be stored locally in temporary directories, transcribed, and deleted immediately to ensure voice biometric data does not leave the host machine.
- **Visual Privacy:** Screenshots taken by the Vision Service must be written locally to `vision/screen.png` and overwritten during subsequent tasks. Screenshots are only uploaded to the Groq API during active visual search tasks.
- **Local Logs:** Conversation history, tool logs, and execution traces must be written locally, ensuring no telemetry data is transmitted to remote storage servers.

---

### 45. Error Handling Strategy

AURA uses a centralized error-handling strategy to capture exceptions without halting execution.

```
 [ Service Executing Action ]
              │
    ( Exception Occurs? )
      ├── Yes ──► [ Capture Error Type & Message ]
      │                 │
      │                 ▼
      │           [ Clean Up Allocated Resources ]
      │           (e.g., delete temp files)
      │                 │
      │                 ▼
      │           [ Format Standard JSON Payload ]
      │           `{"status": "error", "error": "..."}`
      │                 │
      │                 ▼
      │           [ Send Payload to Gateway ]
      │                 │
      │                 ▼
      │           [ Display User-Friendly Error in UI ]
      │
      └── No ───► [ Proceed to Success Verification ]
```

- **Graceful Degradation:** If the internet connection fails, the Gateway must intercept API errors and fallback to informing the user that online components (NLP, Vision, Search) are unavailable, while keeping local components (ASR, file tools) functional.
- **Service Timeout Handling:** All inter-service requests must configure explicit timeout boundaries (e.g., `timeout=10` in `requests.post()`) to prevent service hangs from blocking execution threads.

---

### 46. Logging Strategy

AURA uses Python's standard `logging` library to track system state across all services.

#### Log Format:
```
[TIMESTAMP] [SERVICE] [LEVEL] Message text (e.g., [2026-07-08T17:15:30Z] [ASR] [INFO] Transcribing tmp_382.webm...)
```

#### Logging Levels:
- **INFO:** Tracks request routing, tool mapping, and execution status.
- **WARNING:** Tracks minor issues, such as rate limits or missing configuration variables.
- **ERROR:** Tracks service exceptions, missing dependencies, or execution failures.

---

### 47. Performance Requirements

- **ASR Transcription Speed:** The local Whisper service must complete transcribing voice segments under 5 seconds in less than 1.5 seconds.
- **Intent Parsing Latency:** The NLP Service parser must process inputs and return structured intent payloads in under 800 milliseconds.
- **Overall Pipeline Latency:** The round-trip time from audio submission to task execution must finish in under 3.5 seconds.

---

### 48. Scalability Considerations

- **Workload Isolation:** Resource-intensive components (ASR running CPU-bound models, Vision handling screenshot conversions) run on separate ports, allowing them to be scaled to dedicated worker nodes as demand increases.
- **State Independence:** The services are stateless, communicating via standard JSON payloads. This design allows multiple instances of any service to run behind a local load balancer.

---

### 49. Reliability Requirements

- **Fault Tolerance:** If a non-critical service crashes (such as the TTS Service), the Gateway must process the user request, display the result in the UI, and log the failure without terminating execution.
- **Failsafe Controls:** PyAutoGUI is configured with `FAILSAFE = True` to halt mouse movements if the cursor is manually moved to any screen corner.

---

### 50. Availability Requirements

- **Continuous Operation:** The Gateway and local tool services must maintain 100% availability for offline operations on the host machine.
- **Degraded Operation Mode:** When disconnected from the internet, the system must remain online and allow users to run local commands directly via the text entry interface.

---

### 51. Maintainability Requirements

- **Modular Registries:** Adding a new tool to AURA must only require writing a Python function in `tool_service.py` and registering it in the intent mapping dictionary.
- **Clean Separation:** Frontend presentation code (`gateway/index.html`, `gateway/styles.css`) is decoupled from backend logic, allowing changes to the user interface to be made without affecting backend services.

---

### 52. Extensibility Plan

- **Ollama Integration:** The NLP and Vision services are designed to allow developers to swap cloud Groq API calls for local Ollama servers (e.g., running `Llama-3.2-3B` and `Llama-3.2-11B-Vision` locally) by updating the base API client URL.
- **Unified Plugin Loader:** Future iterations will support dynamic plugin loading from a designated `/plugins` directory, allowing developers to add custom capabilities without editing core service files.

---

### 53. Testing Strategy

The QA strategy uses a modular testing pipeline to verify system stability before deployment:
- **Unit Testing:** Focuses on verifying independent service code, such as path resolution algorithms, string sanitizers, and coordinate scaling calculations.
- **Integration Testing:** Verifies inter-service API communication (e.g., ensuring the Gateway routes transcribed text to the NLP parser correctly).
- **System Testing:** Validates end-to-end user workflows, testing the complete pipeline from voice input to command execution and audio playback.

---

### 54. Unit Testing

- Run unit tests locally using Python's standard `unittest` framework.
- Mock external network calls to the Groq API to verify JSON parsing logic independently.
- Test filesystem utilities under `tools/` with mock directories to check boundary conditions.

---

### 55. Integration Testing

- Start all microservices on their default ports.
- Execute integration scripts to POST test payloads to service endpoints (e.g., verifying that `/transcribe` correctly accepts audio streams and returns strings).
- Verify that port binding conflicts are resolved gracefully.

---

### 56. System Testing

- Open the AURA web dashboard inside a browser.
- Perform voice commands to create, edit, search, and delete files, verifying changes on disk.
- Test visual automation commands, checking that the system captures screenshots and moves the cursor to target elements.

---

### 57. Test Cases

| Test ID | Test Name | Target Component | Input Payload | Expected Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Voice Transcription | ASR Service | WebM file containing speech "open notepad" | Plaintext JSON: `{"text": "open notepad"}` | Verified |
| **TC-02** | Intent Parsing | NLP Service | `{"text": "open notepad"}` | Intent JSON: `{"tool": "open_app", "params": {"target": "notepad"}}` | Verified |
| **TC-03** | File Creation | Tool Service | `{"tool": "create_file", "params": {"path": "t.txt", "content": "hello"}}` | Success JSON response; file `t.txt` exists on disk. | Verified |
| **TC-04** | File Creation Security | Tool Service | Path `../../windows/system32.dll` | File creation blocked; returns a path warning. | Verified |
| **TC-05** | App Launch | Tool Service | `{"tool": "open_app", "params": {"target": "notepad"}}` | Process notepad starts; system registers PID. | Verified |
| **TC-06** | App Termination | Tool Service | `{"tool": "close_app", "params": {"target": "notepad"}}` | Notepad process terminates. | Verified |
| **TC-07** | Screen Capture | Vision Service | Captured screen request | Screenshot saved locally to `vision/screen.png` as 720p. | Verified |
| **TC-08** | Coordinate Scaling | Vision Service | Normalized target `(x: 640, y: 360)` on 1080p | Scales coordinates to center screen `(x: 960, y: 540)`. | Verified |
| **TC-09** | Volume Adjustment | Tool Service | `{"tool": "volume", "params": {"action": "up", "amount": 5}}` | Host system volume increases by 5 units. | Verified |
| **TC-10** | Audio Synthesis | TTS Service | `{"text": "Done."}` | MP3 file generated and served at `/audio`. | Verified |
| **TC-11** | Key Config Fallback | NLP Service | Missing API key in `.env` | Returns clear API key configuration warning in UI. | Verified |
| **TC-12** | Database Write | Tool Service | Calendar event input | CSV file contains new row matching date and time. | Verified |
```
