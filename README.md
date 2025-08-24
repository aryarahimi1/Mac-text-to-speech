# 🗣️ Text to Speech Web App

A simple and elegant text-to-speech web application built with Streamlit that converts your text into speech using:

- macOS's built‑in `say` command (free, offline)
- ElevenLabs API (premium AI voices)
- Kokoro (local, open‑weight neural TTS — runs entirely on your machine)

## ✨ Features

- Clean, modern interface (dark theme)
- Variable speed control (0.75x → 2.0x)
- Multi‑line text input
- Submit shows a built‑in audio player (no auto‑play)
- Transcript displayed under the player with word/character counts
- Start/Stop TTS controls (Stop affects macOS `say`; player controls are separate)
- Audio saving with history page (play, download, delete)
- macOS output saved as WAV for browser compatibility (AIFF → WAV conversion)
- ElevenLabs integration: enter API key and pick a voice (+ optional advanced params)
- Kokoro provider: high‑quality local TTS, no API key, saves WAV

## 🚀 Quick Start

### Prerequisites

- macOS (required for the `say` command) OR any OS for ElevenLabs (internet required)
- Python 3.10+ recommended (Kokoro requires Python ≥ 3.10)
- pip package manager
- (Optional) ElevenLabs account and API key: https://elevenlabs.io

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aryarahimi1/Mac-text-to-speech.git
   cd Mac-text-to-speech
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 🔑 Using ElevenLabs

1. Select "ElevenLabs" as the provider.
2. Enter your ElevenLabs API key (stored only in the current session).
3. Pick a voice from your account.
4. Type your text and click Submit. The generated MP3 will be saved in `saved_audio/` and appear in Audio History.

Notes:
- Default model is `eleven_monolingual_v1`. You can optionally choose other models and tweak voice parameters in the UI.

## 🧠 Using Kokoro (Local, Open‑weight)

1. Select "Kokoro (local open model)" as the provider.
2. Choose language (American/British English) and provide a voice ID (defaults like `af_heart`).
3. Pick your speed and enter text, then click Submit. Output is saved as WAV.

Notes:
- Requires Python 3.10+. On first use, it may download model weights; this can take a minute.
- Runs fully locally (no API key). Performance depends on your machine.

## 🎮 Usage

1. **Choose your reading speed** from the dropdown menu:
   - 0.75x (Slower) - Good for learning or difficult text
   - 1.0x (Normal) - Standard reading speed
   - 1.25x (Faster) - Slightly quicker pace
   - 1.5x (Much Faster) - Rapid reading for familiar content
   - 2.0x (Very Fast) - Quick playback

2. **Enter your text** in the large text area (supports multiple lines)

3. **Click Submit** to start speaking at your selected speed

4. **Monitor progress** with the speaking indicator and speed display

5. **Click Stop** to interrupt speech at any time

Provider quick tips:
- Mac: free and offline; uses built‑in voices; output is WAV.
- ElevenLabs: requires API key; returns MP3; great quality and many voices.
- Kokoro: local neural TTS; no API key; returns WAV.

## 📁 Project Structure

```
Mac-text-to-speech/
│
├── streamlit_app.py    # Main application file
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
└── saved_audio/        # Generated audio files + metadata.json
```

## 🛠️ Technical Details

- Framework: Streamlit
- macOS TTS: `say -r <rate>` generates AIFF; app converts to WAV using `afconvert` for browser playback
- ElevenLabs: REST API via `requests`; returns MP3
- Kokoro: Python pipeline (KPipeline) streams audio; writes 24 kHz mono 16‑bit WAV
- Styling: custom CSS
- State: Streamlit session_state

## 📦 Where files are saved

- Audio files are saved to `saved_audio/` in the app folder.
- A `metadata.json` file tracks entries for the History page.

## 🧩 Troubleshooting

- If the browser audio player shows “Error” for Mac output, regenerate after this update (files are now WAV).
- `afconvert` is part of macOS. If conversion fails, ensure you’re on macOS and try installing Xcode command line tools.
- Kokoro import errors: ensure Python ≥ 3.10 and that requirements installed successfully. First run may download weights.

## 🆕 What’s New

- Added Kokoro as a local, open‑weight TTS provider (no API key)
- Updated in‑app Instructions and README to reflect provider choices and usage
- Saved audio now consistently uses WAV for Mac/Kokoro and MP3 for ElevenLabs

## 🔮 Future Features

### 🎯 ElevenLabs-Specific Ideas (future)

- [ ] **Streaming TTS**: play audio chunks as they arrive for lower latency.
- [ ] **Optimize Latency Modes**: expose `optimize_streaming_latency` presets.
- [ ] **Emotion/Style Presets**: one-click presets that map to stability/style combos.
- [ ] **Voice Cloning**: upload samples to create custom voices, then select them.
- [ ] **Pronunciation Dictionaries**: manage `pronunciation_dictionary_ids` for names/terms.
- [ ] **SSML / Prosody Controls**: finer control over pauses, emphasis, breaks.
- [ ] **Multi-language Auto-detect**: swap to multilingual models when needed.
- [ ] **History & Reproducibility**: save all generation parameters alongside audio.
- [ ] **Usage & Cost Tracking**: estimate characters/s and show monthly usage.
- [ ] **Subtitles/SRT**: align text to timestamps and export captions.
- [ ] **Batch & Queue**: process many texts and zip outputs.
- [ ] **Share Links**: signed URLs or public pages to share clips.

### 🚀 Advanced (provider‑agnostic)

- [ ] **Word Highlighting** - Real-time word-by-word highlighting (improved sync)
- [ ] **Speech Analytics** - Reading time estimates and statistics
- [ ] **Theme Customization** - Multiple color themes and layouts
- [ ] **Keyboard Shortcuts** - Quick controls without mouse
- [ ] **API Integration** - Support for cloud TTS services (Google, AWS, Azure)
- [ ] **Language Support** - Multi-language text-to-speech
- [ ] **Plugin System** - Extensible architecture for custom features

### 🔧 Technical Improvements

- [ ] **Offline Mode** - Full functionality without internet
- [ ] **Performance Optimization** - Faster loading and smoother operation
- [ ] **Error Handling** - Better error messages and recovery
- [ ] **Configuration File** - User preferences and settings persistence
- [ ] **Docker Support** - Containerized deployment option
- [ ] **Unit Tests** - Comprehensive test coverage
- [ ] **Documentation** - API docs and developer guide

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses macOS built-in `say` command for text-to-speech
- Inspired by the need for a simple, fast text-to-speech solution

---

Made with ❤️ for better accessibility and productivity
