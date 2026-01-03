<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/AI-Groq%20LLM-orange?style=for-the-badge&logo=ai&logoColor=white" alt="AI"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">SENTINEL-X</h1>
<h3 align="center">Voice-Controlled Desktop Automation with AI</h3>

<p align="center">
  <em>Transform your Windows PC into an intelligent assistant that executes complex tasks through natural voice commands</em>
</p>

---

## Overview

**SENTINEL-X** is a sophisticated voice-controlled desktop automation system that leverages Large Language Models (LLMs) to understand natural language commands and translate them into precise desktop actions. Built with a modular OOP architecture, it combines speech recognition, AI-powered intent parsing, and OS-level automation.

### Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language Processing** | Speak naturally - the AI understands context and intent |
| **LLM-Powered Brain** | Uses Groq's Llama 3.1 for intelligent command parsing |
| **Full Desktop Control** | Launch apps, manage files, control browser, and more |
| **Music Integration** | Play any song via voice command |
| **Screenshot Capture** | Hands-free screen capture |
| **System Monitoring** | Real-time CPU, memory, and battery reports |
| **Sci-Fi HUD Interface** | Immersive tactical-style GUI |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       SENTINEL-X SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   GUI Layer  │───▶│  Bot Engine  │───▶│   Nova OS    │       │
│  │   (Tkinter)  │    │  (Async I/O) │    │  (Executor)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Voice Input  │    │  Nova Brain  │    │  OS Actions  │       │
│  │  (Google SR) │    │  (Groq LLM)  │    │ (PyAutoGUI)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Module | Purpose | Technologies |
|--------|---------|--------------|
| `app/gui.py` | Sci-Fi tactical interface with real-time status | Tkinter, Canvas Graphics |
| `app/main.py` | Async bot engine, voice capture, TTS | AsyncIO, Edge-TTS, Pygame |
| `app/nova_brain.py` | LLM integration for intent recognition | Groq API, Llama 3.1 |
| `app/nova_os.py` | OS-level automation (OOP design) | PyAutoGUI, PyWin32, PSUtil |
| `app/nova_actions.py` | Action library (functional design) | Subprocess, OS |

---

## Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8+
- Microphone
- Internet connection
- [Groq API Key](https://console.groq.com) (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/Shehzad3684/SENTINEL-X.git
cd SENTINEL-X

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the Application

```bash
# GUI Mode (recommended)
python -m app.gui

# Console Mode (legacy)
python -m app.main
```

---

## Usage Examples

### Voice Commands

| Command | Action |
|---------|--------|
| *"Open Notepad"* | Launches Notepad |
| *"Go to YouTube"* | Opens YouTube in browser |
| *"Play Blinding Lights"* | Plays song on YouTube |
| *"Create a folder called Projects on Desktop"* | Creates folder + opens it |
| *"Take a screenshot"* | Captures screen to Desktop |
| *"Status report"* | Reports CPU, memory, battery |
| *"Download VLC"* | Opens VLC download page |
| *"Initiate coding mode"* | Opens VS Code + GitHub + Lo-Fi music |

### Multi-Step Commands

The AI breaks down complex requests automatically:

```
User: "Open Notepad and write a poem about coding"

AI Plan:
1. LAUNCH_SYS → notepad
2. TYPE_STRING → "Code flows like rivers..."
3. RESPONSE → "Typed poem in Notepad"
```

---

## Technical Highlights

### AI Integration
- **Model**: Llama 3.1 8B Instant via Groq
- **Response Format**: Structured JSON action plans
- **Temperature**: 0.0 for deterministic outputs

### Voice Processing
- **Speech Recognition**: Google Speech API
- **Text-to-Speech**: Microsoft Edge TTS (neural voices)
- **Audio**: Low-latency Pygame mixer (24kHz, 512 buffer)

### Desktop Automation
- **GUI Control**: PyAutoGUI for mouse/keyboard
- **Window Management**: PyGetWindow
- **System Info**: PSUtil for hardware metrics
- **Office Integration**: PyWin32 COM automation

### Design Patterns
- **OOP Architecture**: Modular, extensible class design
- **Async/Await**: Non-blocking voice and TTS operations
- **Action Dispatcher**: Clean separation of concerns

---

## Project Structure

```
SENTINEL-X/
├── app/                      # Main application package
│   ├── __init__.py          # Package initialization
│   ├── gui.py               # Sci-Fi HUD interface (1100 lines)
│   ├── main.py              # Bot engine with async voice loop
│   ├── nova_brain.py        # LLM integration layer
│   ├── nova_os.py           # OS automation (OOP)
│   └── nova_actions.py      # Action library (functional)
├── assets/                   # Static resources
│   └── audio/               # Sound effects
├── main.py                  # Legacy console entry point
├── nova_brain.py            # Legacy brain module
├── nova_os.py               # Legacy OS module
├── nova_actions.py          # Legacy actions module
├── requirements.txt         # Python dependencies
├── build_exe.py             # PyInstaller build script
├── .env.example             # Environment template
└── README.md                # Documentation
```

---

## Configuration

### Environment Variables

```bash
# .env
GROQ_API_KEY=your_api_key_here
```

### Extending the Bot

**Add Custom Sites** (`nova_actions.py`):
```python
KNOWN_SITES = {
    "github": "github.com",
    "mysite": "example.com",
}
```

**Add Custom Protocols** (`nova_os.py`):
```python
def protocol_custom(self):
    self.launch_app("code")
    self.open_browser("localhost:3000")
```

---

## Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone EXE
python build_exe.py

# Output: dist/SENTINEL-X.exe
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pyautogui` | >=0.9.54 | GUI automation |
| `pygetwindow` | >=0.0.9 | Window management |
| `psutil` | >=5.9.0 | System monitoring |
| `pygame` | >=2.5.0 | Audio playback |
| `SpeechRecognition` | >=3.10.0 | Voice recognition |
| `edge-tts` | >=6.1.0 | Text-to-speech |
| `groq` | >=0.4.0 | LLM API client |
| `customtkinter` | >=5.2.0 | Modern UI widgets |
| `pywin32` | >=306 | Windows COM automation |

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Google Speech Recognition** - Voice input processing
- **Microsoft Edge TTS** - Natural text-to-speech
- **Groq** - Lightning-fast LLM inference
- **PyAutoGUI** - Cross-platform GUI automation

---

<p align="center">
  <strong>Built for automation enthusiasts</strong>
</p>

<p align="center">
  <a href="https://github.com/Shehzad3684/SENTINEL-X/issues">Report Bug</a>
  ·
  <a href="https://github.com/Shehzad3684/SENTINEL-X/issues">Request Feature</a>
</p>
