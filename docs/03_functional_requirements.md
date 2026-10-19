# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 3: FUNCTIONAL REQUIREMENTS

---

### 15. Functional Requirements (FR-001 to FR-045)

#### FR-001: Web Browser Audio Recording
- **Requirement ID:** FR-001
- **Name:** Web Browser Audio Recording
- **Description:** The system must capture raw user audio using the Web Audio API in the browser.
- **Priority:** High
- **Inputs:** User voice via microphone.
- **Outputs:** Compressed audio stream (WebM/WAV format).
- **Preconditions:** Microphone permissions granted to `localhost:5000`.
- **Postconditions:** Audio file is buffered in browser memory.
- **Success Criteria:** Browser records and compresses audio without data loss.
- **Failure Conditions:** Audio device busy or permission denied, throwing a console error.

#### FR-002: Audio Transmission to Gateway
- **Requirement ID:** FR-002
- **Name:** Audio Transmission to Gateway
- **Description:** The client must POST the recorded audio file to the Gateway service.
- **Priority:** High
- **Inputs:** WebM audio payload.
- **Outputs:** HTTP 200 JSON response containing transcription and execution results.
- **Preconditions:** Gateway server is running on port 5000.
- **Postconditions:** Request payload is received by the Flask app.
- **Success Criteria:** Gateway receives the binary audio payload.
- **Failure Conditions:** Network timeout or Gateway offline, resulting in an HTTP 504.

#### FR-003: Local ASR Transcribe Request
- **Requirement ID:** FR-003
- **Name:** Local ASR Transcribe Request
- **Description:** The Gateway must forward the raw audio stream to the ASR Service.
- **Priority:** High
- **Inputs:** HTTP multipart file payload containing WebM audio.
- **Outputs:** JSON string containing the transcribed text: `{"text": "..."}`.
- **Preconditions:** ASR Service is active on port 5001.
- **Postconditions:** ASR receives and writes the stream to a temporary location.
- **Success Criteria:** Transcription is returned successfully to the Gateway.
- **Failure Conditions:** ASR service is unreachable, returning an HTTP 500.

#### FR-004: Whisper Audio Extraction
- **Requirement ID:** FR-004
- **Name:** Whisper Audio Extraction
- **Description:** The ASR service must convert input audio files to compatible formats and load them into Whisper.
- **Priority:** High
- **Inputs:** Temporary `.webm` audio file.
- **Outputs:** Transcribed English string.
- **Preconditions:** FFmpeg is installed and accessible in the system environment PATH.
- **Postconditions:** Whisper base model transcribes the speech.
- **Success Criteria:** FFmpeg processes the audio and Whisper extracts the text.
- **Failure Conditions:** FFmpeg is missing, causing a `FileNotFoundError` in Python.

#### FR-005: ASR Temporary File Cleanup
- **Requirement ID:** FR-005
- **Name:** ASR Temporary File Cleanup
- **Description:** The ASR service must delete temporary audio files immediately after transcription.
- **Priority:** Medium
- **Inputs:** Path to the temporary `.webm` file.
- **Outputs:** Filesystem status (success/failure code).
- **Preconditions:** File write operation completed.
- **Postconditions:** Temporary audio file is deleted.
- **Success Criteria:** OS reports successful deletion of the file.
- **Failure Conditions:** File permission locks prevent deletion, leaving orphaned files.

#### FR-006: NLP Intent Parser Routing
- **Requirement ID:** FR-006
- **Name:** NLP Intent Parser Routing
- **Description:** The Gateway must POST the transcribed text to the NLP service to extract intents and parameters.
- **Priority:** High
- **Inputs:** Plaintext string `{"text": "..."}`.
- **Outputs:** JSON object `{"intent": "...", "tool": "...", "params": {...}}`.
- **Preconditions:** NLP Service is active on port 5002.
- **Postconditions:** Clean structured payload returned to the Gateway.
- **Success Criteria:** Gateway receives correct JSON structure.
- **Failure Conditions:** NLP Service is down, returning an HTTP 500 connection error.

#### FR-007: Groq LLM Connection
- **Requirement ID:** FR-007
- **Name:** Groq LLM Connection
- **Description:** The NLP service must connect to the Groq API using the key specified in the environment variables.
- **Priority:** High
- **Inputs:** API Key `GROQ_API_KEY`, System Prompt, User Prompt.
- **Outputs:** Chat completion response payload.
- **Preconditions:** Active internet connection and valid key inside the `.env` file.
- **Postconditions:** Groq returns the chat completion payload.
- **Success Criteria:** API returns an HTTP 200 with model choices.
- **Failure Conditions:** Invalid API key or network down, returning an HTTP 401/403 or network timeout.

#### FR-008: Intent Schema Validation
- **Requirement ID:** FR-008
- **Name:** Intent Schema Validation
- **Description:** The NLP service must validate the JSON returned by the LLM against the system capability schema.
- **Priority:** High
- **Inputs:** Raw string response from LLM.
- **Outputs:** Validated JSON structure.
- **Preconditions:** LLM completes its response generation.
- **Postconditions:** JSON is loaded into a Python dictionary.
- **Success Criteria:** Parser successfully parses the response as JSON.
- **Failure Conditions:** LLM returns Markdown or text, causing a JSON decoding error.

#### FR-009: NLP Fallback Routing
- **Requirement ID:** FR-009
- **Name:** NLP Fallback Routing
- **Description:** If the user input does not match any register tool, the NLP service must route the query to a general conversational handler.
- **Priority:** Medium
- **Inputs:** Conversation text string.
- **Outputs:** JSON object with `"intent": "general"` and `"tool": "general"`.
- **Preconditions:** LLM response contains no tool structure.
- **Postconditions:** Action is routed to a general chat handler.
- **Success Criteria:** General response text returned correctly.
- **Failure Conditions:** Routing fails, causing a blank response.

#### FR-010: Create File Tool
- **Requirement ID:** FR-010
- **Name:** Create File Tool
- **Description:** The Tool Service must create a file at the specified location with optional initial content.
- **Priority:** High
- **Inputs:** File path, content string.
- **Outputs:** Execution status: `{"status": "success", "result": "..."}`.
- **Preconditions:** Target folder exists and has write permissions.
- **Postconditions:** File is created on the filesystem.
- **Success Criteria:** The file exists and contains the specified content.
- **Failure Conditions:** Directory path not found or permissions denied, returning an error message.

#### FR-011: Read File Tool
- **Requirement ID:** FR-011
- **Name:** Read File Tool
- **Description:** The Tool Service must open and read the contents of a local file.
- **Priority:** High
- **Inputs:** Absolute or relative file path.
- **Outputs:** Plaintext file contents.
- **Preconditions:** Target file exists and has read permissions.
- **Postconditions:** File handle is closed.
- **Success Criteria:** System successfully reads and returns the file contents.
- **Failure Conditions:** File not found, returning an error message.

#### FR-012: Edit File Tool
- **Requirement ID:** FR-012
- **Name:** Edit File Tool
- **Description:** The Tool Service must edit an existing file, supporting overwrite or append operations.
- **Priority:** High
- **Inputs:** Target path, content string, edit mode ("overwrite" or "append").
- **Outputs:** Success status message.
- **Preconditions:** File exists and is writeable.
- **Postconditions:** File content is updated.
- **Success Criteria:** New text is written to the file.
- **Failure Conditions:** Disk full or write permission denied.

#### FR-013: Delete File Tool
- **Requirement ID:** FR-013
- **Name:** Delete File Tool
- **Description:** The Tool Service must delete a file from the host filesystem.
- **Priority:** High
- **Inputs:** File path.
- **Outputs:** Deletion confirmation message.
- **Preconditions:** Target file exists.
- **Postconditions:** File is removed from disk.
- **Success Criteria:** File no longer exists on disk.
- **Failure Conditions:** File lock or permission denied.

#### FR-014: Global File Search
- **Requirement ID:** FR-014
- **Name:** Global File Search
- **Description:** The Tool Service must search for a file by name across common user directories.
- **Priority:** Medium
- **Inputs:** Target filename.
- **Outputs:** List of absolute file paths matching the query.
- **Preconditions:** Directory indexes are readable.
- **Postconditions:** Return matching file paths.
- **Success Criteria:** Target file is located.
- **Failure Conditions:** Zero matches found, returning "file not found".

#### FR-015: Directory Listing Tool
- **Requirement ID:** FR-015
- **Name:** Directory Listing Tool
- **Description:** The Tool Service must list all files and subdirectories inside a specified folder.
- **Priority:** Medium
- **Inputs:** Target directory path.
- **Outputs:** JSON list containing file names and directory properties.
- **Preconditions:** Target directory exists.
- **Postconditions:** Return listing payload.
- **Success Criteria:** Files inside folder are listed correctly.
- **Failure Conditions:** Access denied or folder missing.

#### FR-016: Local System RAM Query
- **Requirement ID:** FR-016
- **Name:** Local System RAM Query
- **Description:** The Tool Service must read the host system's RAM utilization metrics.
- **Priority:** Medium
- **Inputs:** None.
- **Outputs:** Used/Total RAM capacity metrics (e.g., "RAM at 58%").
- **Preconditions:** `psutil` library is initialized.
- **Postconditions:** Read complete.
- **Success Criteria:** Current RAM status returned.
- **Failure Conditions:** Access violation reading system statistics.

#### FR-017: CPU Load Query
- **Requirement ID:** FR-017
- **Name:** CPU Load Query
- **Description:** The Tool Service must retrieve the current CPU utilization percentage.
- **Priority:** Medium
- **Inputs:** None.
- **Outputs:** Overall CPU load percentage.
- **Preconditions:** System API access is available.
- **Postconditions:** Return stats.
- **Success Criteria:** Average CPU load returned.
- **Failure Conditions:** Library metrics failure.

#### FR-018: Host Battery Status
- **Requirement ID:** FR-018
- **Name:** Host Battery Status
- **Description:** The Tool Service must query the battery level and charging state of the host device.
- **Priority:** Low
- **Inputs:** None.
- **Outputs:** Battery percentage and power plug status.
- **Preconditions:** Power APIs are available on the OS.
- **Postconditions:** Returns battery status payload.
- **Success Criteria:** Correct percentage returned.
- **Failure Conditions:** Device has no battery (e.g., desktop PC), returning "Not available".

#### FR-019: Open Application Tool
- **Requirement ID:** FR-019
- **Name:** Open Application Tool
- **Description:** The Tool Service must launch a designated desktop application via system execution hooks.
- **Priority:** High
- **Inputs:** Target application name or process path.
- **Outputs:** Process ID (PID) or launch confirmation message.
- **Preconditions:** Application path is registered in system environment.
- **Postconditions:** Application runs as a background process.
- **Success Criteria:** Application window opens.
- **Failure Conditions:** Application path is not found in Registry/PATH, returning an error.

#### FR-020: Close Application Tool
- **Requirement ID:** FR-020
- **Name:** Close Application Tool
- **Description:** The Tool Service must terminate running process instances of an application.
- **Priority:** High
- **Inputs:** Application process name (e.g., "chrome.exe").
- **Outputs:** Process termination confirmation message.
- **Preconditions:** Target process is active.
- **Postconditions:** Process is terminated.
- **Success Criteria:** Target application window closes.
- **Failure Conditions:** Access denied or process not running.

#### FR-021: System Volume Adjustment
- **Requirement ID:** FR-021
- **Name:** System Volume Adjustment
- **Description:** The Tool Service must adjust the system master volume level.
- **Priority:** Medium
- **Inputs:** Action ("up", "down", "mute"), amount value.
- **Outputs:** Updated volume status message.
- **Preconditions:** System audio driver is active.
- **Postconditions:** Output volume changes.
- **Success Criteria:** Host system volume adjusts.
- **Failure Conditions:** Audio device not detected.

#### FR-022: Active Windows Listing
- **Requirement ID:** FR-022
- **Name:** Active Windows Listing
- **Description:** The Tool Service must list the titles of all active application windows.
- **Priority:** Medium
- **Inputs:** None.
- **Outputs:** List of active window titles.
- **Preconditions:** `pygetwindow` library is loaded.
- **Postconditions:** List generated.
- **Success Criteria:** Return names of open windows.
- **Failure Conditions:** OS window manager refuses access.

#### FR-023: Window State Manipulation
- **Requirement ID:** FR-023
- **Name:** Window State Manipulation
- **Description:** The Tool Service must minimize, maximize, or focus a designated application window.
- **Priority:** Medium
- **Inputs:** Target window title, action ("minimize", "maximize", "focus").
- **Outputs:** Action confirmation status.
- **Preconditions:** Target window exists.
- **Postconditions:** Window layout changes.
- **Success Criteria:** Selected window changes layout state.
- **Failure Conditions:** Window title not located.

#### FR-024: Web Search Query
- **Requirement ID:** FR-024
- **Name:** Web Search Query
- **Description:** The Tool Service must perform a search query using DuckDuckGo and parse the results.
- **Priority:** High
- **Inputs:** Search query string.
- **Outputs:** Consolidated list of search results.
- **Preconditions:** Internet connection is active.
- **Postconditions:** Connection closed.
- **Success Criteria:** DuckDuckGo returns search snippets.
- **Failure Conditions:** Connection timeout or API blocked.

#### FR-025: Calendar Log Writer
- **Requirement ID:** FR-025
- **Name:** Calendar Log Writer
- **Description:** The Tool Service must log scheduled events to the local `calendar.csv` file.
- **Priority:** Medium
- **Inputs:** Event title, date, time string.
- **Outputs:** Success confirmation message.
- **Preconditions:** Write access to the storage directory.
- **Postconditions:** CSV row is written.
- **Success Criteria:** Event is written to the CSV file.
- **Failure Conditions:** CSV file locked by another application.

#### FR-026: Desktop Screenshot Grabber
- **Requirement ID:** FR-026
- **Name:** Desktop Screenshot Grabber
- **Description:** The Vision Service must capture the desktop frame buffer and save it to disk.
- **Priority:** High
- **Inputs:** Screen region bounding box.
- **Outputs:** Base64 image payload and a local PNG file.
- **Preconditions:** Desktop environment is active (not locked or headless).
- **Postconditions:** File is written to the vision folder.
- **Success Criteria:** Frame buffer is saved as a 720p PNG.
- **Failure Conditions:** Screen device context unavailable (e.g., system locked).

#### FR-027: Screen Resize and Compression
- **Requirement ID:** FR-027
- **Name:** Screen Resize and Compression
- **Description:** The Vision Service must compress the captured screenshot to reduce token usage.
- **Priority:** Medium
- **Inputs:** Original raw image.
- **Outputs:** Resized 1280x720 PNG image.
- **Preconditions:** Image successfully captured.
- **Postconditions:** Compressed image is loaded into memory.
- **Success Criteria:** File size reduced by at least 70%.
- **Failure Conditions:** Image compression library throws an error.

#### FR-028: Vision Model Request
- **Requirement ID:** FR-028
- **Name:** Vision Model Request
- **Description:** The Vision Service must upload the base64-encoded screenshot and query the multimodal model.
- **Priority:** High
- **Inputs:** Base64 image payload, prompt text.
- **Outputs:** Model response text.
- **Preconditions:** Valid Groq API key configured.
- **Postconditions:** Completion received.
- **Success Criteria:** Groq returns a description or parsed coordinate JSON.
- **Failure Conditions:** Upload timeout or API rate limit exceeded.

#### FR-029: Screen Coordinate Extraction
- **Requirement ID:** FR-029
- **Name:** Screen Coordinate Extraction
- **Description:** The Vision Service must locate the coordinates of a target element on screen.
- **Priority:** High
- **Inputs:** Target element name.
- **Outputs:** JSON object: `{"found": true, "x": 123, "y": 456}`.
- **Preconditions:** Vision model processes the screenshot.
- **Postconditions:** Coordinates are parsed.
- **Success Criteria:** System returns valid pixel coordinates.
- **Failure Conditions:** Model returns non-JSON or invalid coordinates.

#### FR-030: Screen Coordinate Translation
- **Requirement ID:** FR-030
- **Name:** Screen Coordinate Translation
- **Description:** The Vision Service must scale coordinates from 1280x720 back to the host system's resolution.
- **Priority:** High
- **Inputs:** Normalized X and Y coordinates.
- **Outputs:** Target system coordinates.
- **Preconditions:** `pyautogui.size()` returns screen dimensions.
- **Postconditions:** Coordinates are converted.
- **Success Criteria:** Target coordinates match the display aspect ratio.
- **Failure Conditions:** Output out of bounds.

#### FR-031: Simulated Mouse Movement
- **Requirement ID:** FR-031
- **Name:** Simulated Mouse Movement
- **Description:** The Vision Service must move the host mouse cursor to target coordinates.
- **Priority:** High
- **Inputs:** Screen X and Y coordinates.
- **Outputs:** None.
- **Preconditions:** Target location is within screen bounds.
- **Postconditions:** Mouse cursor position updates.
- **Success Criteria:** Cursor moves to the target element.
- **Failure Conditions:** PyAutoGUI failsafe is triggered.

#### FR-032: Simulated Click Execution
- **Requirement ID:** FR-032
- **Name:** Simulated Click Execution
- **Description:** The Vision Service must execute a click or double-click action at current coordinates.
- **Priority:** High
- **Inputs:** Action type ("single_click" or "double_click").
- **Outputs:** Success status message.
- **Preconditions:** Mouse cursor is positioned over the target.
- **Postconditions:** OS registers a click event.
- **Success Criteria:** Application element is clicked or opened.
- **Failure Conditions:** Target application window is unresponsive.

#### FR-033: Screen Description
- **Requirement ID:** FR-033
- **Name:** Screen Description
- **Description:** The Vision Service must describe the user's active desktop screen in detail.
- **Priority:** Medium
- **Inputs:** Question prompt.
- **Outputs:** Text description of desktop contents.
- **Preconditions:** Screenshot successfully captured.
- **Postconditions:** Returns description.
- **Success Criteria:** Returns description of open windows and icons.
- **Failure Conditions:** Vision model parsing fails.

#### FR-034: Desktop Icons Scanner
- **Requirement ID:** FR-034
- **Name:** Desktop Icons Scanner
- **Description:** The Vision Service must list all active files and folders visible on the desktop.
- **Priority:** Medium
- **Inputs:** None.
- **Outputs:** List of files and folders.
- **Preconditions:** Read access to Desktop directory.
- **Postconditions:** Return list.
- **Success Criteria:** Return file list matching visual desktop state.
- **Failure Conditions:** Directory read error.

#### FR-035: Find Text on Screen
- **Requirement ID:** FR-035
- **Name:** Find Text on Screen
- **Description:** The Vision Service must search for specific text visible on the user's screen.
- **Priority:** Medium
- **Inputs:** Target text query.
- **Outputs:** Approximate coordinate layout of matched text.
- **Preconditions:** Screenshot successfully captured.
- **Postconditions:** Return location.
- **Success Criteria:** Target text is located on screen.
- **Failure Conditions:** Text not found.

#### FR-036: TTS Speak Request
- **Requirement ID:** FR-036
- **Name:** TTS Speak Request
- **Description:** The Gateway must send response text to the TTS service to generate an audio file.
- **Priority:** High
- **Inputs:** Plaintext response payload.
- **Outputs:** Status code `{"status": "ok"}`.
- **Preconditions:** TTS service is active on port 5004.
- **Postconditions:** Audio file is saved to disk.
- **Success Criteria:** TTS creates the target audio file.
- **Failure Conditions:** TTS engine returns an error.

#### FR-037: TTS Audio File Generation
- **Requirement ID:** FR-037
- **Name:** TTS Audio File Generation
- **Description:** The TTS service must generate an MP3 audio file using Google Text-to-Speech (gTTS).
- **Priority:** High
- **Inputs:** Plaintext string.
- **Outputs:** `response.mp3` saved on disk.
- **Preconditions:** Active internet connection to Google translate servers.
- **Postconditions:** Audio file is written.
- **Success Criteria:** MP3 file exists on disk.
- **Failure Conditions:** Connection timeout.

#### FR-038: TTS Audio Fetch
- **Requirement ID:** FR-038
- **Name:** TTS Audio Fetch
- **Description:** The Gateway must expose a static route to serve the generated MP3 file to the client.
- **Priority:** High
- **Inputs:** HTTP GET to `/audio`.
- **Outputs:** MP3 audio file stream.
- **Preconditions:** `response.mp3` exists.
- **Postconditions:** Audio stream sent.
- **Success Criteria:** Client browser plays the audio payload.
- **Failure Conditions:** Audio file missing on disk.

#### FR-039: Gateway Status API
- **Requirement ID:** FR-039
- **Name:** Gateway Status API
- **Description:** The Gateway must query the status of all microservices and return their online/offline state.
- **Priority:** Medium
- **Inputs:** None.
- **Outputs:** JSON list of service states.
- **Preconditions:** Services are configured on defined ports.
- **Postconditions:** Connection status returned.
- **Success Criteria:** Dashboard displays correct status of each service.
- **Failure Conditions:** Timeout occurs checking ports.

#### FR-040: Text Mode Routing
- **Requirement ID:** FR-040
- **Name:** Text Mode Routing
- **Description:** The Gateway must process text-only prompts, bypassing the ASR transcription step.
- **Priority:** High
- **Inputs:** Text string `{"text": "..."}`.
- **Outputs:** JSON response containing the execution result.
- **Preconditions:** Gateway is active on port 5000.
- **Postconditions:** Command is routed to the NLP Service.
- **Success Criteria:** Execution result is returned directly to the client.
- **Failure Conditions:** Invalid request format.

#### FR-041: Command Pre-Verification Guard
- **Requirement ID:** FR-041
- **Name:** Command Pre-Verification Guard
- **Description:** The system must validate user commands to prevent execution of unauthorized system operations.
- **Priority:** High
- **Inputs:** Intent data payload.
- **Outputs:** Boolean status (authorized/blocked).
- **Preconditions:** NLP successfully parses intent.
- **Postconditions:** Proceed to route task or abort execution.
- **Success Criteria:** System blocks unauthorized commands.
- **Failure Conditions:** Validation engine fails.

#### FR-042: Self-Verification of File Operations
- **Requirement ID:** FR-042
- **Name:** Self-Verification of File Operations
- **Description:** The Tool Service must verify that file modifications were successfully written to disk.
- **Priority:** Medium
- **Inputs:** Target file path.
- **Outputs:** Status check confirmation.
- **Preconditions:** Write operation completes.
- **Postconditions:** Return status.
- **Success Criteria:** System verifies file size or content updates.
- **Failure Conditions:** Verification fails.

#### FR-043: Static Asset Serving
- **Requirement ID:** FR-043
- **Name:** Static Asset Serving
- **Description:** The Gateway service must serve static frontend files (HTML, CSS, JS) from the local directory.
- **Priority:** High
- **Inputs:** HTTP GET requests.
- **Outputs:** HTML, CSS, JS source code files.
- **Preconditions:** Gateway service starts.
- **Postconditions:** Frontend resources loaded in browser.
- **Success Criteria:** Client browser displays the landing page.
- **Failure Conditions:** Missing static folder directory.

#### FR-044: Centralized Error Formatting
- **Requirement ID:** FR-044
- **Name:** Centralized Error Formatting
- **Description:** The Gateway must catch exceptions from all services and return standard error messages to the client.
- **Priority:** Medium
- **Inputs:** Python exception trace stack.
- **Outputs:** JSON error format: `{"error": "...", "response": "..."}`.
- **Preconditions:** Exception occurs during execution.
- **Postconditions:** System state remains stable.
- **Success Criteria:** UI shows a clear error message instead of crashing.
- **Failure Conditions:** Global try-except block fails.

#### FR-045: Execution Timeout Guard
- **Requirement ID:** FR-045
- **Name:** Execution Timeout Guard
- **Description:** The Gateway must abort execution and return a timeout message if a service does not respond within a set limit.
- **Priority:** Medium
- **Inputs:** HTTP request thread.
- **Outputs:** HTTP 504 gateway timeout message.
- **Preconditions:** Gateway routes request.
- **Postconditions:** Unresponsive service connection terminated.
- **Success Criteria:** System stays responsive to new requests.
- **Failure Conditions:** Infinite wait locks the thread pool.
