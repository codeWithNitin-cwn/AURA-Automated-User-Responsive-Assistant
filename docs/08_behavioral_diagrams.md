# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 8: BEHAVIORAL DIAGRAMS & DEPLOYMENT ARCHITECTURE

This chapter provides behavioral models and architecture diagrams for AURA using Mermaid syntax.

---

### 36. Sequence Diagrams

#### Sequence Diagram SD-1: Voice Processing and Execution Flow
This diagram details the sequence of calls involved in executing a system-level command via voice input.

```mermaid
sequenceDiagram
    autonumber
    actor User as Operator
    participant Client as Client Browser
    participant GW as Gateway Orchestrator (:5000)
    participant ASR as ASR Whisper (:5001)
    participant NLP as NLP Parser (:5002)
    participant TOOL as Tool Execution (:5003)
    participant TTS as TTS Synthesizer (:5004)

    User->>Client: Click Mic & Speak Command
    Client->>GW: POST /process (WebM audio)
    GW->>ASR: POST /transcribe (WebM audio)
    ASR-->>GW: JSON {"text": "What is my RAM usage?"}
    GW->>NLP: POST /parse {"text": "What is my RAM usage?"}
    NLP-->>GW: JSON {"tool": "system_info", "params": {"query": "ram"}}
    GW->>TOOL: POST /execute {"tool": "system_info", "params": {"query": "ram"}}
    Note over TOOL: Query host OS metrics using psutil
    TOOL-->>GW: JSON {"result": "RAM is at 58% usage..."}
    GW->>TTS: POST /speak {"text": "RAM is at 58%..."}
    Note over TTS: Synthesize speech and save to local MP3
    TTS-->>GW: JSON {"status": "ok"}
    GW-->>Client: JSON Response (payload details)
    Client->>TTS: GET /audio (stream audio file)
    TTS-->>Client: Serve response.mp3 binary
    Client->>User: Play voice output & show text on UI
```

#### Sequence Diagram SD-2: Vision-Based Click Flow
This diagram illustrates the sequence of calls when the user issues a command to click a visual target on their screen.

```mermaid
sequenceDiagram
    autonumber
    actor User as Operator
    participant GW as Gateway Orchestrator (:5000)
    participant NLP as NLP Parser (:5002)
    participant VIS as Vision Service (:5005)
    participant Groq as Groq Vision API
    participant OS as Host OS API

    User->>GW: POST /process_text {"text": "Open Chrome icon"}
    GW->>NLP: POST /parse {"text": "Open Chrome icon"}
    NLP-->>GW: JSON {"tool": "click_icon", "params": {"target": "Chrome"}}
    GW->>VIS: POST /click_icon {"target": "Chrome"}
    Note over VIS: Grab screenshot & resize to 1280x720
    VIS->>Groq: POST Llama 4 Scout (screenshot + target name)
    Groq-->>VIS: JSON {"found": true, "x": 105, "y": 240}
    Note over VIS: Translate coordinates to screen aspect ratio
    VIS->>OS: pyautogui.moveTo(105, 240)
    VIS->>OS: pyautogui.doubleClick()
    OS-->>VIS: Confirm OS event registered
    VIS-->>GW: JSON {"result": "Found Chrome and double clicked."}
    GW-->>User: JSON Response
```

---

### 37. Activity Diagrams

#### Activity Diagram AD-1: Gateway Command Validation and Routing
This diagram traces the decision path taken by the Gateway orchestrator when processing user requests.

```mermaid
stateDiagram-v2
    [*] --> RequestReceived: Request posted to /process or /process_text
    
    state RequestReceived {
        [*] --> CheckInputType
        CheckInputType --> VoiceInput: Contains audio file
        CheckInputType --> TextInput: Contains text payload
        
        VoiceInput --> SendToASR: Forward to port 5001
        SendToASR --> GetTextString: Transcribe completed
        TextInput --> GetTextString: Extract text parameter
    }
    
    GetTextString --> SendToNLP: Forward to port 5002
    
    state SendToNLP {
        [*] --> CallGroqAPI
        CallGroqAPI --> CheckJSON: Receive response
        CheckJSON --> ParsingFailed: Invalid JSON payload
        CheckJSON --> RoutingParsed: Valid payload
    }
    
    ParsingFailed --> ReturnErrorResult: Format exception
    RoutingParsed --> RouteDecision: Read 'tool' parameter
    
    state RouteDecision {
        [*] --> EvaluateToolName
        EvaluateToolName --> VisionService: Tool in {click_icon, read_screen, ...}
        EvaluateToolName --> ToolService: Tool is standard OS action
    }
    
    VisionService --> RunExecution: POST /click_icon on port 5005
    ToolService --> RunExecution: POST /execute on port 5003
    
    RunExecution --> VerifyOutput: Verify execution status
    VerifyOutput --> BuildAudioResponse: Output valid
    VerifyOutput --> ReturnErrorResult: Output invalid/timeout
    
    BuildAudioResponse --> GenerateTTS: POST /speak on port 5004
    GenerateTTS --> Complete: Return payload to client
    ReturnErrorResult --> Complete: Return error to client
    
    Complete --> [*]
```

---

### 38. State Diagrams

#### State Diagram STD-1: System Execution Lifecycle
This state diagram represents the operational states of the Gateway service as it processes requests.

```mermaid
stateDiagram-v2
    [*] --> Idle: System initialized and listening on port 5000
    
    Idle --> Recording: User clicks mic / voice capture active
    Recording --> Transcribing: Audio payload sent to port 5001
    
    Idle --> Parsing: Text prompt received directly via /process_text
    Transcribing --> Parsing: Text transcription successfully returned
    
    Parsing --> Executing: Intent recognized and routed to target service
    Executing --> Verifying: Execution completed; verifying filesystem/OS changes
    
    Verifying --> Synthesizing: Verification successful; text sent to port 5004
    Synthesizing --> Speaking: TTS file generated and streaming to client
    
    Executing --> ExceptionHandled: Timeout / execution exception caught
    Verifying --> ExceptionHandled: Verification check failed
    ExceptionHandled --> Idle: Error displayed in UI
    
    Speaking --> Idle: Audio playback completed
```

---

### 39. Deployment Architecture

AURA is deployed locally on a single host computer, running as a distributed network of microservices that integrate with cloud-hosted inference APIs.

```mermaid
graph TB
    subgraph Host Machine (Local Environment)
        subgraph Frontend Sandbox (Web Browser)
            UI[Web UI Dashboard]
            Mic[Audio Microphone Input]
            Speaker[System Speakers]
        end

        subgraph Service Mesh (Localhost Port Bindings)
            GW[Gateway Service :5000]
            ASR[ASR Service :5001]
            NLP[NLP Service :5002]
            TOOL[Tool Service :5003]
            TTS[TTS Service :5004]
            VIS[Vision Service :5005]
        end

        subgraph Local System Interfaces
            FS[Filesystem Storage]
            OS[Host OS Window Manager]
        end
    end

    subgraph External Infrastructure (WAN)
        Groq[Groq Cloud Inference API]
        DDG[DuckDuckGo Search Engine]
    end

    %% Network Connections
    UI <-->|HTTP / JSON| GW
    Mic -->|Audio Stream| GW
    GW -->|Static Audio URL| UI
    Speaker <-->|MP3 Stream| TTS

    GW <-->|Loopback HTTP| ASR
    GW <-->|Loopback HTTP| NLP
    GW <-->|Loopback HTTP| TOOL
    GW <-->|Loopback HTTP| TTS
    GW <-->|Loopback HTTP| VIS

    TOOL <-->|System Calls / Filesystem IO| FS
    TOOL <-->|pyautogui / subprocess| OS
    VIS <-->|pyautogui / screen grab| OS

    %% Cloud Integration
    NLP <-->|HTTPS API Key| Groq
    VIS <-->|HTTPS API Key| Groq
    TOOL <-->|HTTP requests| DDG
```
