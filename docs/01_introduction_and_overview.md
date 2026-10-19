# AURA: TECHNICAL SPECIFICATION & SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## CHAPTER 1: INTRODUCTION & PROJECT OVERVIEW

---

### 1. Cover Page

**TITLE OF THE PROJECT**  
**AURA – A Microservice-Based Autonomous Universal Response Assistant for Voice-Driven Intelligent Desktop Automation**

**A Major Project Report / Technical Specification Document**  
Submitted in partial fulfillment of the requirements for the degree of  
**Bachelor of Technology (B.Tech) in Computer Science & Engineering**

**Submitted By:**  
Nitin (Roll No: BTECH-CSE-2026-N1)  

**Department of Computer Science & Engineering**  
**July 2026**  

---

### 2. Version History

The following table documents the revision history of this specification. All changes must be approved by the lead architect.

| Version | Date | Author | Description of Changes | Approved By |
| :--- | :--- | :--- | :--- | :--- |
| v0.1.0 | 2026-05-10 | Nitin | Initial project proposal and service layout diagram. | Academic Board |
| v1.0.0 | 2026-06-15 | Nitin | Initial microservice implementation (ASR, Gateway, Tools, TTS). | Technical Advisor |
| v2.0.0 | 2026-07-08 | Nitin | Integrated Vision capability (`llama-4-scout-17b`) and created `.env` routing. | Lead Architect |

---

### 3. Table of Contents

- **CHAPTER 1: INTRODUCTION & PROJECT OVERVIEW**
  - 1. Cover Page
  - 2. Version History
  - 3. Table of Contents
  - 4. Executive Summary
  - 5. Project Overview
  - 6. Problem Statement
  - 7. Objectives
  - 8. Scope
- **CHAPTER 2: EXISTING SYSTEM & USER SPECIFICATION**
  - 9. Existing System Analysis
  - 10. Proposed System
  - 11. System Overview
  - 12. Stakeholders
  - 13. User Roles
  - 14. User Requirements
- **CHAPTER 3: FUNCTIONAL REQUIREMENTS**
  - 15. Functional Requirements (FR-001 to FR-045)
- **CHAPTER 4: SYSTEM QUALITIES & OPERATIONAL RULES**
  - 16. Non-Functional Requirements
  - 17. Business Rules
  - 18. Assumptions
  - 19. Constraints
  - 20. Use Cases
  - 21. User Stories
  - 22. Acceptance Criteria
- **CHAPTER 5: SOFTWARE ARCHITECTURE & SERVICE DESIGN**
  - 23. System Context Diagram
  - 24. Software Architecture
  - 25. Microservice Architecture
  - 26. Component Diagram
  - 27. Service Responsibilities
  - 28. Gateway Service Design
  - 29. ASR Service Design
  - 30. NLP Service Design
  - 31. Tool Execution Service Design
  - 32. Vision Service Design
  - 33. Text-to-Speech Service Design
  - 34. Communication Flow
- **CHAPTER 6: REST API SPECIFICATIONS & BEHAVIORAL DIAGRAMS**
  - 35. REST API Specifications
  - 36. Sequence Diagrams
  - 37. Activity Diagrams
  - 38. State Diagrams
  - 39. Deployment Architecture
- **CHAPTER 7: SYSTEM IMPLEMENTATION & QUALITY ASSURANCE**
  - 40. Technology Stack
  - 41. Folder Structure
  - 42. Configuration Management
  - 43. Security Requirements
  - 44. Privacy Requirements
  - 45. Error Handling Strategy
  - 46. Logging Strategy
  - 47. Performance Requirements
  - 48. Scalability Considerations
  - 49. Reliability Requirements
  - 50. Availability Requirements
  - 51. Maintainability Requirements
  - 52. Extensibility Plan
- **CHAPTER 8: VERIFICATION, DEPLOYMENT & OPERATION**
  - 53. Testing Strategy
  - 54. Unit Testing
  - 55. Integration Testing
  - 56. System Testing
  - 57. Test Cases
  - 58. Deployment Guide
  - 59. Installation Guide
  - 60. Future Enhancements
  - 61. Risks and Limitations
  - 62. Glossary
  - 63. References

---

### 4. Executive Summary

AURA (Autonomous Universal Response Assistant) is a modern, voice-activated AI assistant running on a local microservices architecture. Designed for developers and power users, it automates common operating system interactions—such as file editing, media control, calendar scheduling, web search, active window management, and visual screen control—using natural language.

The application leverages a hybrid edge-cloud pipeline. An offline, local Whisper instance processes audio inputs, while complex semantic parsing and screen-image understanding are offloaded to cloud-hosted Large Language Models (LLMs) via the Groq API. Actions are executed locally on the host machine using low-level OS shell commands and coordinate-based mouse/keyboard simulations. By splitting these tasks into independent Flask microservices, AURA achieves modularity, fault tolerance, and a clear separation of concerns.

---

### 5. Project Overview

AURA is developed as a final year B.Tech project in Computer Science & Engineering. The project demonstrates the application of distributed systems engineering, computer vision, and machine learning to build an intelligent OS controller. 

Unlike traditional monolith voice applications, AURA decomposes the processing lifecycle into distinct stages:
1. **ASR (Speech-to-Text):** Runs locally via OpenAI's Whisper `base` model.
2. **NLP (Intent Parser):** Evaluates user instructions using `llama-3.3-70b-versatile` to produce JSON schemas representing commands.
3. **Orchestrator (Gateway):** Routes requests to specialized local services.
4. **Tools Executor:** Interacts with the local file system, process manager, and active application windows.
5. **Vision Service:** Captures the display buffer and uses `llama-4-scout-17b-16e-instruct` to perform visual search and mouse clicks.
6. **TTS (Text-to-Speech):** Converts text output back to audio streams for playback.

---

### 6. Problem Statement

Existing consumer-grade voice assistants (e.g., Apple Siri, Amazon Alexa, Google Assistant) are closed cloud ecosystems. They suffer from three core limitations:
1. **System Control Gaps:** They cannot perform fine-grained desktop automation, such as editing local text files, checking system RAM, launching specific developer tools, or clicking arbitrary screen locations.
2. **Privacy Vulnerabilities:** They continuously stream ambient voice capture and personal system metadata to centralized cloud servers.
3. **Rigid API Integrations:** They struggle to automate legacy or GUI-only desktop applications that lack public APIs or command-line developer hooks.

AURA addresses these issues by implementing a local microservices runtime that combines private local ASR with lightweight visual screen automation.

---

### 7. Objectives

#### Primary Objectives:
- Implement a functional, low-latency microservice pipeline that automates operating system tasks from voice and text inputs.
- Integrate a local Whisper ASR engine to handle speech-to-text without sending raw audio to cloud servers.
- Develop a vision-based GUI automation pipeline that allows the agent to locate and double-click interface elements by name.
- Maintain a clean separation of concerns by hosting services on dedicated local loopback ports.

#### Secondary Objectives:
- Provide an ambient, interactive user interface utilizing modern CSS layouts.
- Keep resource usage low on standard laptop hardware (under 2GB RAM overhead for the entire suite of services).
- Structure the codebase to allow developers to easily add custom Python tools.

---

### 8. Scope

#### In-Scope:
- **Local File System Operations:** Creating, reading, editing (append/overwrite), finding, and deleting files on the host PC.
- **System Monitoring:** Reading active RAM usage, CPU load, active windows, and battery status.
- **Process Orchestration:** Launching and closing common desktop applications (Chrome, Notepad, VS Code, Command Prompt).
- **GUI Control:** Capturing host screenshots, detecting visual icon coordinates, and executing click operations.
- **Web Search:** Fetching results from DuckDuckGo and reading summaries.

#### Out-of-Scope:
- Multi-user concurrency or user account synchronization.
- Voice biometric verification (speaker identification).
- Direct control of mobile operating systems (iOS/Android).
- Complex network vulnerability scanning.
