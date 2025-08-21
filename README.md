# 🗣️ Text to Speech Web App

A simple and elegant text-to-speech web application built with Streamlit that converts your text into speech using macOS's built-in `say` command.

## ✨ Features

- **Clean, modern interface** with dark theme
- **Variable speed control** (0.75x to 2.0x)
- **Multi-line text support** with large text area
- **Real-time feedback** showing current reading speed
- **Start/Stop controls** for speech management
- **Responsive design** that works on different screen sizes

## 🚀 Quick Start

### Prerequisites

- macOS (required for the `say` command)
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aryarahimi1/Mac-text-to-speech.git
   cd Mac-text-to-speech
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

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

## 📁 Project Structure

```
Mac-text-to-speech/
│
├── streamlit_app.py    # Main application file
├── README.md          # Project documentation
└── requirements.txt   # Python dependencies (optional)
```

## 🛠️ Technical Details

- **Framework**: Streamlit for the web interface
- **Text-to-Speech**: macOS `say` command with adjustable rate
- **Styling**: Custom CSS for dark theme and modern appearance
- **State Management**: Streamlit session state for app persistence

## 📱 Screenshots



<img width="2000" height="1352" alt="CleanShot 2025-08-21 at 14 11 21@2x" src="https://github.com/user-attachments/assets/aad7932d-843a-4564-8638-10190ff22c62" />

## 🔮 Future Features

### 🎯 Planned Enhancements

- [ ] **Voice Selection** - Choose different voices (male/female, accents)
- [ ] **Audio Export** - Save speech as MP3/WAV files
- [ ] **Text Import** - Upload text files or paste from clipboard
- [ ] **Reading Progress Bar** - Visual progress indicator during speech
- [ ] **Bookmark System** - Save and organize frequently used texts
- [ ] **Pronunciation Guide** - Custom pronunciation for difficult words
- [ ] **Batch Processing** - Process multiple texts in queue
- [ ] **Cross-platform Support** - Windows and Linux compatibility
- [ ] **Mobile Optimization** - Better mobile interface and controls

### 🚀 Advanced Features

- [ ] **Word Highlighting** - Real-time word-by-word highlighting (improved sync)
- [ ] **Speech Analytics** - Reading time estimates and statistics
- [ ] **Theme Customization** - Multiple color themes and layouts
- [ ] **Keyboard Shortcuts** - Quick controls without mouse
- [ ] **API Integration** - Support for cloud TTS services (Google, AWS, Azure)
- [ ] **Language Support** - Multi-language text-to-speech
- [ ] **SSML Support** - Advanced speech markup for better control
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses macOS built-in `say` command for text-to-speech
- Inspired by the need for a simple, fast text-to-speech solution

## 📞 Support

If you have any questions or run into issues, please open an issue on GitHub or contact [your-email@example.com].

---

Made with ❤️ for better accessibility and productivity
