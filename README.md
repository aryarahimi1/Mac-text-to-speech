# 🗣️ Text to Speech Web App

A comprehensive text-to-speech web application built with Streamlit that converts your text into speech using multiple providers:

- **macOS `say` command** (free, offline)
- **ElevenLabs API** (premium AI voices)
- **Kokoro** (local, open-weight neural TTS — runs entirely on your machine)
- **Chatterbox** (state-of-the-art open-source TTS with emotion control and voice cloning)

## 📋 System Requirements

### Python Version
- **Minimum:** Python 3.10+ (required for Kokoro TTS)
- **Recommended:** Python 3.12 (fully tested and compatible)

### pip Version
- **Minimum:** pip 21.0+
- **Recommended:** pip 25.2+

### Check Your Versions
```bash
python3 --version  # Should show Python 3.10+ for full compatibility
pip3 --version     # Should show pip 21.0 or higher
```

## ✨ Features

### Core Features
- **Clean, modern interface** with dark theme
- **Variable speed control** (0.75x → 2.0x)
- **Multi-line text input** with large text area
- **Built-in audio player** with no auto-play
- **Text transcript display** with word/character counts
- **Audio history management** with enhanced browsing

### 🆕 Recent Updates (v2.1)
- **🎯 Enhanced Kokoro Voice Selection**: Choose from 6 languages and 30+ voices
  - 🇺🇸 American English (11 female, 8 male voices)
  - 🇬🇧 British English (4 female, 4 male voices)
  - 🇫🇷 French (1 female voice)
  - 🇮🇹 Italian (1 female, 1 male voice)
  - 🇯🇵 Japanese (4 female, 1 male voice)
  - 🇨🇳 Chinese (8 voices)

- **📚 Improved Audio History**:
  - **Smart titles** automatically generated from text content
  - **Built-in audio player** using `st.audio` for seamless playback
  - **Better organization** with provider icons and detailed metadata
  - **Enhanced UI** with improved layout and confirmation dialogs

### 🎭 Advanced Features
- **Emotion Controls** (Chatterbox): Adjust emotional intensity and speech pacing
- **Voice Cloning** (Chatterbox): Upload reference audio for custom voice replication
- **Neural Watermarking** (Chatterbox): Responsible AI features
- **Multi-language Support** (Kokoro): Natural voices across 6 languages

## 🚀 Quick Start

### Prerequisites
- macOS (for `say` command) OR any OS for other providers
- **Python 3.10+** (Python 3.12 recommended)
- (Optional) ElevenLabs account and API key: https://elevenlabs.io

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aryarahimi1/Mac-text-to-speech.git
   cd Mac-text-to-speech
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 🎤 Provider Guide

### 🖥️ Mac (say command)
- **Pros**: Free, offline, built into macOS
- **Setup**: No configuration needed
- **Output**: WAV format for browser compatibility
- **Languages**: English (system voices)

### 🤖 ElevenLabs
- **Pros**: Premium AI voices, many options
- **Setup**: Requires API key from elevenlabs.io
- **Output**: MP3 format
- **Languages**: Multiple languages supported

### 🧠 Kokoro (Local Neural TTS)
- **Pros**: Free, runs locally, no API key, high quality
- **Setup**: Automatic model download on first use
- **Output**: WAV format
- **Languages**: 6 languages with 30+ voices
- **Voice Selection**: 
  - Choose language first
  - Select from categorized male/female voices
  - Real-time voice switching

### 🎭 Chatterbox (Advanced Open Source)
- **Pros**: State-of-the-art quality, emotion control, voice cloning
- **Setup**: Automatic model download (~1GB on first use)
- **Output**: WAV format with neural watermarking
- **Features**: Emotion adjustment, voice cloning from audio samples

## 🎮 Usage

1. **Select Provider**: Choose from Mac, ElevenLabs, Kokoro, or Chatterbox
2. **Configure Voice** (Kokoro): 
   - Select your preferred language
   - Choose from available male/female voices
3. **Set Speed**: Choose from 0.75x to 2.0x reading speed
4. **Enter Text**: Type or paste your content in the text area
5. **Generate Audio**: Click Submit to create speech
6. **Play & Manage**: Use the built-in player or visit Audio History

### 📚 Audio History Features
- **Smart Titles**: Automatically generated from your text
- **Easy Playback**: Built-in audio player for each recording
- **Detailed Metadata**: See provider, voice, speed, and creation time
- **Quick Actions**: Download or delete with confirmation
- **Provider Icons**: Visual identification of TTS provider used

## 📦 Dependencies

```txt
streamlit>=1.28.0           # Web interface
requests>=2.31.0            # HTTP requests for ElevenLabs
torch>=2.6.0                # PyTorch for ML models
torchaudio>=2.6.0           # Audio processing
numpy>=1.21.0               # Numerical computing
chatterbox-tts>=0.1.2       # Chatterbox TTS with emotion control
kokoro @ git+https://github.com/hexgrad/kokoro.git     # Kokoro local TTS
misaki[en] @ git+https://github.com/hexgrad/misaki.git # Text processing
```

## 📁 Project Structure

```
Mac-text-to-speech/
│
├── streamlit_app.py    # Main application file
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── saved_audio/        # Generated audio files + metadata.json
└── temp_audio/         # Temporary files for processing
```

## 🛠️ Technical Details

- **Framework**: Streamlit for web interface
- **macOS TTS**: `say` command → AIFF → WAV conversion for browser compatibility
- **ElevenLabs**: REST API integration returning MP3
- **Kokoro**: Local neural pipeline with 24kHz mono 16-bit WAV output
- **Chatterbox**: PyTorch-based neural TTS with watermarking
- **Audio Storage**: All files saved to `saved_audio/` with JSON metadata
- **History Management**: Smart title generation and enhanced playback interface

## 🧩 Troubleshooting

### Python Version Issues
```bash
# Check Python version
python3 --version  # Should show 3.10+ for Kokoro support

# Verify Kokoro compatibility
python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
```

### Installation Issues
```bash
# Force reinstall if needed
pip install --force-reinstall -r requirements.txt

# Check for dependency conflicts
pip check

# Update pip
pip install --upgrade pip
```

### Audio Issues
- **Browser playback errors**: Files are now saved as WAV for better compatibility
- **macOS conversion issues**: Ensure Xcode command line tools are installed
- **Kokoro import errors**: Verify Python ≥ 3.10 and successful requirements installation
- **Model download issues**: Ensure stable internet connection for initial setup

## 🆕 Changelog

### v2.1 (Latest)
- ✨ **Enhanced Kokoro Voice Selection**: Language-first selection with 30+ voices across 6 languages
- 📚 **Improved Audio History**: Smart titles, built-in audio player, better organization
- 🎯 **Better UX**: Provider icons, confirmation dialogs, enhanced metadata display
- 🔧 **Code Quality**: Improved title generation algorithm and backward compatibility

### v2.0
- Added Chatterbox TTS with emotion control and voice cloning
- Added Kokoro as local, open-weight TTS provider
- Implemented audio history with download/delete functionality
- Improved browser audio compatibility (WAV format)

### v1.0
- Initial release with macOS say command and ElevenLabs integration
- Basic speed controls and text input
- Simple audio playback and saving

## 🔮 Future Features

### 🎯 Short Term
- [ ] **Batch Processing**: Generate multiple audio files from text list
- [ ] **Voice Favorites**: Save and quick-select preferred voices
- [ ] **Export Options**: Different audio formats and quality settings
- [ ] **Keyboard Shortcuts**: Quick controls without mouse interaction

### 🚀 Long Term  
- [ ] **Real-time Streaming**: Play audio as it's being generated
- [ ] **SSML Support**: Advanced speech markup for fine control
- [ ] **Multi-language Auto-detect**: Automatic language detection and voice selection
- [ ] **Voice Training**: Custom voice creation and fine-tuning
- [ ] **API Integration**: Additional cloud TTS providers (Google, AWS, Azure)
- [ ] **Mobile App**: React Native companion app

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Install development dependencies: `pip install -r requirements.txt`
4. Make your changes and test thoroughly
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Areas for Contribution
- 🌍 **Internationalization**: UI translations and language support
- 🎨 **UI/UX**: Interface improvements and accessibility features
- 🔧 **Performance**: Optimization and caching improvements
- 📱 **Mobile**: Responsive design enhancements
- 🧪 **Testing**: Unit tests and integration tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the amazing web framework
- [ElevenLabs](https://elevenlabs.io/) for premium AI voice technology
- [Kokoro](https://github.com/hexgrad/kokoro) for open-weight neural TTS
- [Chatterbox](https://github.com/chatterbox-org/chatterbox) for advanced open-source TTS
- macOS `say` command for reliable offline text-to-speech
- The open-source community for continuous inspiration and support

---

**Made with ❤️ for better accessibility and productivity**

*Star ⭐ this repo if you find it useful!*hat's New

- **Added Chatterbox**: State-of-the-art open-source TTS with emotion control and voice cloning
- **Emotion Controls**: Adjust emotional intensity and speech pacing
- **Voice Cloning**: Upload reference audio for custom voice replication
- **Neural Watermarking**: Responsible AI features built into Chatterbox
- Added Kokoro as a local, open‑weight TTS provider (no API key)
- Updated in‑app Instructions and README to reflect provider choices and usage
- Saved audio now consistently uses WAV for Mac/Kokoro/Chatterbox and MP3 for ElevenLabsion Issues
```bash
# Check if you have the right Python version
python3 --version  # Should be 3.10 or higher

# Check if Kokoro can import (requires 3.10+)
python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
```

### Installation Issues
```bash
# Reinstall with force
pip install --force-reinstall -r requirements.txt

# Check for conflicts
pip check

# Update pip if needed
pip install --upgrade pip
```

### Audio Issues
- If the browser audio player shows "Error" for Mac output, regenerate after this update (files are now WAV).
- `afconvert` is part of macOS. If conversion fails, ensure you're on macOS and try installing Xcode command line tools.
- Kokoro import errors: ensure Python ≥ 3.10 and that requirements installed successfully. First run may download weights.
- Chatterbox model download: First run downloads ~1GB model; ensure stable internet connection.offline)
- ElevenLabs API (premium AI voices)
- Kokoro (local, open‑weight neural TTS — runs entirely on your machine)
- Chatterbox (state-of-the-art open-source TTS with emotion control and voice cloning)

## 📋 System Requirements

### Python Version
- **Minimum:** Python 3.10+ (required for Kokoro TTS)
- **Tested & Compatible:** Python 3.12

### pip Version
- **Minimum:** pip 21.0+
- **Tested & Compatible:** pip 25.2

### Check Your Versions
```bash
python3 --version  # Should show Python 3.12 for best compatibility
pip3 --version     # Should show pip 25.2 or higher
```

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
- **Chatterbox provider**: state-of-the-art TTS with emotion control, voice cloning, and neural watermarking

### 🎭 Chatterbox Advanced Features
- **Emotion Exaggeration**: Control emotional intensity (0.25-2.0x)
- **CFG Weight**: Adjust speech pacing (0.0-1.0)
- **Temperature**: Control speech variation (0.1-2.0)
- **Voice Cloning**: Upload 3-10 second audio clips for voice replication
- **Neural Watermarking**: Built-in responsible AI features

## 🚀 Quick Start

### Prerequisites

- macOS (required for the `say` command) OR any OS for ElevenLabs/Kokoro/Chatterbox
- **Python 3.12** (tested and fully compatible)
- **pip 25.2** (tested and fully compatible)
- (Optional) ElevenLabs account and API key: https://elevenlabs.io

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aryarahimi1/Mac-text-to-speech.git
   cd Mac-text-to-speech
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Upgrade pip and install dependencies**
   ```bash
   pip install --upgrade pip
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

## 🎭 Using Chatterbox (State-of-the-Art Open Source)

1. Select "Chatterbox (open-source)" as the provider.
2. **Optional**: Upload a 3-10 second reference audio file for voice cloning.
3. Adjust emotion exaggeration (0.25-2.0) for dramatic or subdued speech.
4. Fine-tune CFG weight (0.0-1.0) to control speech pacing.
5. Type your text and click Submit. High-quality WAV will be saved.

Notes:
- First run downloads the model (may take a few minutes).
- Runs fully locally with neural watermarking for responsible AI.
- Best results with clear, short reference audio for voice cloning.

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
- **Mac**: free and offline; uses built‑in voices; output is WAV.
- **ElevenLabs**: requires API key; returns MP3; great quality and many voices.
- **Kokoro**: local neural TTS; no API key; returns WAV.
- **Chatterbox**: state-of-the-art local TTS; emotion control; voice cloning; returns WAV.

## � Dependencies

```txt
streamlit>=1.28.0           # Web interface
requests>=2.31.0            # HTTP requests for ElevenLabs
torch>=2.6.0                # PyTorch for ML models (Chatterbox)
torchaudio>=2.6.0           # Audio processing (Chatterbox)
numpy>=1.21.0               # Numerical computing
chatterbox-tts>=0.1.2       # Chatterbox TTS with emotion control
kokoro @ git+https://github.com/hexgrad/kokoro.git     # Kokoro local TTS
misaki[en] @ git+https://github.com/hexgrad/misaki.git # Text processing
```

## �📁 Project Structure

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
- **macOS TTS**: `say -r <rate>` generates AIFF; app converts to WAV using `afconvert` for browser playback
- **ElevenLabs**: REST API via `requests`; returns MP3
- **Kokoro**: Python pipeline (KPipeline) streams audio; writes 24 kHz mono 16‑bit WAV
- **Chatterbox**: PyTorch-based neural TTS with emotion control; writes WAV with watermarking
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
