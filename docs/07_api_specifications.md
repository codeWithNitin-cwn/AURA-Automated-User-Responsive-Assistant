# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 7: REST API SPECIFICATIONS

This chapter documents the REST API specifications for all AURA microservices. All communication payloads are formatted as JSON, except for raw audio files uploaded via multipart forms. No authentication headers are required for local loopback connections.

---

### 1. Gateway Service (Port 5000)

#### Endpoint: `/process`
- **Method:** `POST`
- **Description:** Receives user voice input, routes it through the transcription and intent parser pipelines, executes the target tool, and generates an audio response.
- **Request Headers:** `Content-Type: multipart/form-data`
- **Request Body:**
  - `audio` (File binary: WebM audio stream)
- **Success Response (200 OK):**
  ```json
  {
    "user_said": "open chrome",
    "response": "Chrome is open — launching now.",
    "audio_url": "http://localhost:5004/audio"
  }
  ```
- **Error Responses:**
  - **500 Internal Server Error (ASR Service Offline):**
    ```json
    {
      "error": "Failed to connect to ASR service at http://localhost:5001/transcribe",
      "response": "Something went wrong!"
    }
    ```

#### Endpoint: `/process_text`
- **Method:** `POST`
- **Description:** Processes typed text commands directly, bypassing the voice transcription pipeline.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "text": "What is my RAM usage?"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "user_said": "What is my RAM usage?",
    "response": "RAM is at 58% usage (9.3 GB used of 16.0 GB total).",
    "audio_url": null
  }
  ```
- **Error Responses:**
  - **400 Bad Request (Missing Text Payload):**
    ```json
    {
      "error": "No text provided"
    }
    ```

---

### 2. ASR Service (Port 5001)

#### Endpoint: `/transcribe`
- **Method:** `POST`
- **Description:** Transcribes raw WebM audio streams into plaintext using a local instance of Whisper.
- **Request Headers:** `Content-Type: multipart/form-data`
- **Request Body:**
  - `audio` (File binary: WebM audio stream)
- **Success Response (200 OK):**
  ```json
  {
    "text": "read the file demo.txt"
  }
  ```
- **Error Responses:**
  - **400 Bad Request (Missing Audio Payload):**
    ```json
    {
      "error": "No audio file"
    }
    ```

---

### 3. NLP Service (Port 5002)

#### Endpoint: `/parse`
- **Method:** `POST`
- **Description:** Evaluates conversational text queries and maps them to system tools and parameters.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "text": "open chrome browser"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "intent": "open_app",
    "tool": "open_app",
    "params": {
      "target": "chrome"
    }
  }
  ```
- **Error Responses:**
  - **400 Bad Request (Missing Text Parameter):**
    ```json
    {
      "error": "No text provided"
    }
    ```

---

### 4. Tool Service (Port 5003)

#### Endpoint: `/execute`
- **Method:** `POST`
- **Description:** Executes filesystem operations, queries system metrics, or controls applications based on parsed intents.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "tool": "create_file",
    "params": {
      "path": "notes.txt",
      "content": "AURA B.Tech project notes."
    }
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "result": "Created file notes.txt at path C:\\Users\\Nitin\\Desktop\\notes.txt"
  }
  ```
- **Error Responses:**
  - **400 Bad Request (Unsupported Tool):**
    ```json
    {
      "result": "Error: Unknown tool or missing parameters."
    }
    ```

---

### 5. TTS Service (Port 5004)

#### Endpoint: `/speak`
- **Method:** `POST`
- **Description:** Synthesizes output text into spoken audio and saves the stream to a local cache file.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "text": "Created file notes.txt successfully."
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "status": "ok",
    "message": "Audio ready."
  }
  ```
- **Error Responses:**
  - **500 Internal Server Error (Synthesis Failure):**
    ```json
    {
      "error": "Google translation API timeout."
    }
    ```

#### Endpoint: `/audio`
- **Method:** `GET`
- **Description:** Streams the most recently generated speech audio file back to the requesting client.
- **Success Response (200 OK):**
  - **Headers:** `Content-Type: audio/mpeg`
  - **Body:** Binary audio file stream.
- **Error Responses:**
  - **404 Not Found (Missing Audio File):**
    ```json
    {
      "error": "No audio file found. Call /speak first."
    }
    ```

---

### 6. Vision Service (Port 5005)

#### Endpoint: `/read_screen`
- **Method:** `POST`
- **Description:** Captures a system screenshot and describes visible desktop elements based on user questions.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "question": "What window is currently open?"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "result": "Visual scan indicates that Notepad is open with the title draft.txt."
  }
  ```

#### Endpoint: `/click_icon`
- **Method:** `POST`
- **Description:** Locates a target desktop icon or GUI element by name and executes a mouse click.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "target": "Recycle Bin",
    "action": "double_click"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "result": "Found 'Recycle Bin' and clicked it. Double-clicked desktop item."
  }
  ```

#### Endpoint: `/describe`
- **Method:** `POST`
- **Description:** Returns a detailed description of all applications, windows, and desktop icons visible on the user's screen.
- **Request Body:** `{}`
- **Success Response (200 OK):**
  ```json
  {
    "result": "The screen displays a Windows desktop background. The taskbar is visible at the bottom with shortcut icons for Chrome and File Explorer. In the center, a VS Code window is open, showing Python code."
  }
  ```

#### Endpoint: `/find_text`
- **Method:** `POST`
- **Description:** Searches the visible screen area for a target text string and describes its location.
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "text": "run_all.py"
  }
  ```
- **Success Response (200 OK):**
  ```json
  {
    "result": "The text 'run_all.py' was located inside the VS Code editor panel, near the top tab area."
  }
  ```

#### Endpoint: `/desktop_icons`
- **Method:** `GET`
- **Description:** Returns a combined list of files and folders retrieved from the local directory and identified visually on screen.
- **Success Response (200 OK):**
  ```json
  {
    "filesystem": "Desktop folders: project, config\nDesktop files: document.pdf, todo.txt",
    "visual": "A visual scan confirms folders 'project' and 'config' are present on the upper left side of the display.",
    "result": "Desktop folders: project, config\nDesktop files: document.pdf, todo.txt"
  }
  ```
