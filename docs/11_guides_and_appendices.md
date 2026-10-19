# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 11: DEPLOYMENT MANUAL, GLOSSARY & REFERENCES

This chapter provides step-by-step setup guides, plans for future upgrades, a project glossary, and IEEE references.

---

### 58. Deployment Guide

AURA can be deployed manually by starting each microservice or using the provided orchestration scripts.

#### Method A: Manual Service Launch
To debug individual services, launch each microservice in its own terminal window:
1. **ASR Service:**
   ```bash
   python asr/asr_service.py
   ```
2. **NLP Service:**
   ```bash
   python nlp/nlp_service.py
   ```
3. **Tool Service:**
   ```bash
   python tools/tool_service.py
   ```
4. **TTS Service:**
   ```bash
   python tts/tts_service.py
   ```
5. **Vision Service:**
   ```bash
   python vision/vision_service.py
   ```
6. **Gateway Service:**
   ```bash
   python gateway/app.py
   ```

#### Method B: Batch Script Orchestration
On Windows, you can start all services at once by double-clicking the launcher script:
```bash
./start/start_aura.bat
```
This script opens a new command prompt window for each service, making it easy to monitor logs and errors.

#### Method C: Unified Python Launch
Alternatively, run the Python spawner script:
```bash
python start/run_all.py
```
This script runs each service as a background subprocess, outputting: `"All AURA services started."`

---

### 59. Installation Guide

#### Prerequisites:
1. **Python 3.8 to 3.11:** Ensure Python is installed and added to the system PATH.
2. **Git:** Required to clone the repository.
3. **FFmpeg:** Required by Whisper to process audio streams.

#### Installation Steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/codeWithNitin-cwn/aura.git
   cd aura
   ```

2. **Install FFmpeg:**
   - **On Windows:** Run the following command in PowerShell with administrator permissions:
     ```powershell
     winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
     ```
   - **On macOS (using Homebrew):**
     ```bash
     brew install ffmpeg
     ```
   - **On Linux (Debian/Ubuntu):**
     ```bash
     sudo apt update && sudo apt install ffmpeg -y
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   - Create a `.env` file in the root directory.
   - Add your Groq API key:
     ```ini
     GROQ_API_KEY=your_groq_api_key_here
     ```

---

### 60. Future Enhancements

- **Local LLM Offline Cascade:** Configure the system to fallback to a local Ollama server running `Llama-3.2-3B` and `Llama-3.2-11B-Vision` if the internet connection is lost.
- **Biometric Wake-Word Engine:** Integrate a local wake-word listener (e.g., using PocketSphinx or Porcupine) to trigger voice recording without clicking the UI microphone button.
- **Relational Logging Database:** Replace the local CSV logs with an SQLite database to store execution logs, system state history, and user settings.
- **Dynamic Capabilities Loader:** Allow the Tool Service to automatically register new scripts placed in the `/plugins` directory without restarting the service mesh.

---

### 61. Risks and Limitations

- **Groq API Dependency:** Since semantic parsing and screen descriptions rely on cloud models, these services are subject to external API downtime and rate limiting.
- **Brittle Vision Coordinates:** If the host screen resolution shifts during visual clicking tasks, coordinate scaling calculations can fail.
- **Security Sandboxing Gaps:** The Tool Service executes low-level Python scripts directly on the host operating system. Unauthorized users with access to the local network could potentially execute destructive commands.

---

### 62. Glossary

- **ASR:** Automatic Speech Recognition (converts speech inputs into written text).
- **TTS:** Text-to-Speech (converts text strings into synthesized speech).
- **NLP:** Natural Language Processing (semantic intent parsing and entity extraction).
- **LLM:** Large Language Model (deep learning model trained on text data).
- **MoE:** Mixture of Experts (machine learning architecture that routes inputs to specialized sub-networks).
- **REST:** Representational State Transfer (architectural style for web services).
- **CORS:** Cross-Origin Resource Sharing (mechanism allowing web pages to request resources from different domains).
- **PID:** Process Identifier (unique numerical ID assigned to active OS processes).
- **WAN:** Wide Area Network (public internet connection).
- **GUI:** Graphical User Interface (visual layout of application windows and elements).

---

### 63. References

- [1] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, and I. Sutskever, "Robust Speech Recognition via Large-Scale Weak Supervision," in *International Conference on Machine Learning (ICML)*, 2023, pp. 28490-28518.
- [2] A. Vaswani et al., "Attention Is All You Need," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017, pp. 5998-6008.
- [3] R. Fielding, "Architectural Styles and the Design of Network-based Software Architectures," Ph.D. dissertation, University of California, Irvine, 2000.
- [4] "IEEE Recommended Practice for Software Requirements Specifications," IEEE Std 830-1998, 1998.
- [5] "ISO/IEC/IEEE International Standard for Systems and Software Engineering - Life Cycle Processes - Requirements Engineering," ISO/IEC/IEEE Std 29148-2018, 2018.
- [6] "IEEE Standard for Software Design Descriptions," IEEE Std 1016-2009, 2009.
