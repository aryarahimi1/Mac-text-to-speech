import streamlit as st
import os
import time
import datetime
import json
from pathlib import Path
import requests
import io
import subprocess
import threading
import wave
import numpy as np
import sys

st.set_page_config(
    page_title="Text to Speech",
    page_icon="🗣️",
    layout="centered"
)

st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stTextArea > div > div > textarea {
        font-size: 16px;
        min-height: 150px;
    }
    .stButton > button {
        font-size: 18px;
        height: 50px;
        width: 100%;
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .reading-text {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #333;
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
        font-size: 18px;
        line-height: 1.8;
        color: #ffffff;
        word-spacing: 2px;
    }
    .speaking-indicator {
        background-color: #28a745;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 15px 0;
        font-size: 18px;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'is_speaking' not in st.session_state:
    st.session_state.is_speaking = False
if 'last_spoken_text' not in st.session_state:
    st.session_state.last_spoken_text = ""
if 'speed_setting' not in st.session_state:
    st.session_state.speed_setting = 1.0
if 'tts_provider' not in st.session_state:
    st.session_state.tts_provider = "Mac (say command)"
if 'elevenlabs_api_key' not in st.session_state:
    st.session_state.elevenlabs_api_key = ""
if 'elevenlabs_voice_id' not in st.session_state:
    st.session_state.elevenlabs_voice_id = ""
if 'current_audio_file' not in st.session_state:
    st.session_state.current_audio_file = None
if 'kokoro_voice' not in st.session_state:
    st.session_state.kokoro_voice = 'af_heart'
if 'kokoro_lang' not in st.session_state:
    st.session_state.kokoro_lang = 'a'  # 'a' American English, 'b' British English

def ensure_audio_directory():
    audio_dir = Path("saved_audio")
    audio_dir.mkdir(exist_ok=True)
    return audio_dir

def get_elevenlabs_voices(api_key):
    """Get available voices from ElevenLabs"""
    try:
        headers = {"xi-api-key": api_key}
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
        if response.status_code == 200:
            voices = response.json()["voices"]
            return {voice["name"]: voice["voice_id"] for voice in voices}
        else:
            return None
    except:
        return None

def generate_elevenlabs_audio(text, api_key, voice_id, speed_setting, model_id=None, voice_settings_override=None):
    """Generate audio using ElevenLabs API"""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        # Determine voice settings
        if voice_settings_override is not None:
            voice_settings = voice_settings_override
        else:
            # Basic mapping of speed to stability/similarity if no override provided
            stability = max(0.1, min(1.0, 0.75 - (speed_setting - 1.0) * 0.2))
            similarity_boost = max(0.1, min(1.0, 0.75 + (speed_setting - 1.0) * 0.1))
            voice_settings = {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": 0.0,
                "use_speaker_boost": True,
            }

        data = {
            "text": text,
            "model_id": model_id or "eleven_monolingual_v1",
            "voice_settings": voice_settings,
        }

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return response.content
        else:
            return None
    except:
        return None

def audio_player_controls():
    """Display audio player controls using Streamlit's built-in audio player"""
    if not st.session_state.current_audio_file:
        return
    
    st.markdown("### 🎵 Audio Player")
    
    # Get current file info
    filepath = Path(st.session_state.current_audio_file)
    if not filepath.exists():
        st.error("Audio file not found")
        return
    
    # Use Streamlit's built-in audio player
    try:
        with open(filepath, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        # Determine format based on file extension
        file_extension = filepath.suffix.lower()
        if file_extension == '.mp3':
            audio_format = "audio/mpeg"
        elif file_extension == '.aiff' or file_extension == '.aif':
            # Some browsers don't play AIFF; we convert to WAV earlier now,
            # but keep this for robustness.
            audio_format = "audio/aiff"
        elif file_extension == '.wav':
            audio_format = "audio/wav"
        else:
            audio_format = "audio/mpeg"  # default
        
        st.audio(audio_bytes, format=audio_format)
        
        # Show file info
        st.caption(f"📁 File: {filepath.name}")
        
    except Exception as e:
        st.error(f"Error loading audio file: {str(e)}")

def save_audio_file(text, speed_setting, tts_provider, api_key=None, voice_id=None, model_id=None, voice_settings_override=None):
    """Save TTS audio to a file and return the filepath"""
    audio_dir = ensure_audio_directory()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if tts_provider == "Mac (say command)":
        # Generate AIFF then convert to WAV for browser-friendly playback
        tmp_aiff = audio_dir / f"tts_mac_{timestamp}.aiff"
        filename = f"tts_mac_{timestamp}.wav"
        filepath = audio_dir / filename

        base_rate = 150
        adjusted_rate = int(base_rate * speed_setting)

        # Create AIFF via say
        os.system(f'say -r {adjusted_rate} -o "{tmp_aiff}" "{text}"')
        # Convert to WAV (HTML5 audio friendly) and remove AIFF
        os.system(f'afconvert -f WAVE -d LEI16 "{tmp_aiff}" "{filepath}"')
        if tmp_aiff.exists():
            try:
                os.remove(tmp_aiff)
            except Exception:
                pass
        
    elif tts_provider == "ElevenLabs":
        filename = f"tts_elevenlabs_{timestamp}.mp3"
        filepath = audio_dir / filename
        
        audio_content = generate_elevenlabs_audio(
            text,
            api_key,
            voice_id,
            speed_setting,
            model_id=model_id,
            voice_settings_override=voice_settings_override,
        )
        if audio_content:
            with open(filepath, 'wb') as f:
                f.write(audio_content)
        else:
            return None, None
    else:  # Kokoro
        # Lazy import to avoid heavy import on non-Kokoro paths
        try:
            from kokoro import KPipeline
        except Exception as e:
            st.error(f"Kokoro not installed or failed to import: {e}")
            return None, None

        filename = f"tts_kokoro_{timestamp}.wav"
        filepath = audio_dir / filename

        # Configure language and voice
        kokoro_lang = st.session_state.get('kokoro_lang', 'a')
        kokoro_voice = st.session_state.get('kokoro_voice', 'af_heart')

        try:
            pipeline = KPipeline(lang_code=kokoro_lang)
            # Write 24kHz mono 16-bit PCM WAV as per Kokoro README
            with wave.open(str(filepath.resolve()), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(24000)

                for result in pipeline(text, voice=kokoro_voice, speed=speed_setting, split_pattern=r"\n+"):
                    if result.audio is None:
                        continue
                    audio_bytes = (result.audio.numpy() * 32767).astype(np.int16).tobytes()
                    wav_file.writeframes(audio_bytes)
        except Exception as e:
            st.error(f"Kokoro generation failed: {e}")
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception:
                    pass
            return None, None
    
    metadata = {
        "filename": filename,
        "text": text,
        "speed": speed_setting,
        "provider": tts_provider,
        "timestamp": timestamp,
        "created": datetime.datetime.now().isoformat(),
        "voice_id": voice_id if tts_provider == "ElevenLabs" else None,
        "kokoro_voice": st.session_state.get('kokoro_voice') if tts_provider == "Kokoro (local open model)" else None,
        "kokoro_lang": st.session_state.get('kokoro_lang') if tts_provider == "Kokoro (local open model)" else None,

    }
    
    metadata_file = audio_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            all_metadata = json.load(f)
    else:
        all_metadata = []
    
    all_metadata.append(metadata)
    
    with open(metadata_file, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    # Set as current audio file for the player
    st.session_state.current_audio_file = str(filepath)
    
    return filepath, metadata

st.title("🗣️ Text to Speech")

# Navigation
page = st.sidebar.selectbox("Choose a page", ["🎤 Text to Speech", "📚 Audio History"])

def main_tts_page():
    st.markdown("---")
    
    # TTS Provider Selection
    st.markdown("### 🎙️ Text-to-Speech Provider")
    tts_provider = st.selectbox(
        "Choose TTS provider:",
        ["Mac (say command)", "ElevenLabs", "Kokoro (local open model)"],
        key="tts_provider_selector"
    )
    st.session_state.tts_provider = tts_provider
    
    # ElevenLabs Configuration
    if tts_provider == "ElevenLabs":
        st.markdown("#### 🔑 ElevenLabs Configuration")
        
        api_key = st.text_input(
            "ElevenLabs API Key:",
            type="password",
            placeholder="Enter your ElevenLabs API key",
            help="Get your API key from https://elevenlabs.io/",
            key="elevenlabs_api_input"
        )
        st.session_state.elevenlabs_api_key = api_key
        
        if api_key:
            with st.spinner("Loading voices..."):
                voices = get_elevenlabs_voices(api_key)
            
            if voices:
                selected_voice = st.selectbox(
                    "Choose voice:",
                    options=list(voices.keys()),
                    key="voice_selector"
                )
                st.session_state.elevenlabs_voice_id = voices[selected_voice]
                st.success(f"✅ Connected to ElevenLabs! Voice: {selected_voice}")

                # Advanced settings
                st.markdown("#### 🎚️ Advanced Voice Settings (optional)")
                model_id = st.selectbox(
                    "Model:",
                    options=[
                        "eleven_monolingual_v1",
                        "eleven_multilingual_v2",
                        "eleven_turbo_v2"
                    ],
                    index=0,
                    help="Choose the ElevenLabs model. Turbo is faster, multilingual supports many languages."
                )

                use_advanced = st.checkbox(
                    "Customize voice parameters (overrides speed mapping)",
                    value=False,
                )

                if use_advanced:
                    col_a1, col_a2 = st.columns(2)
                    with col_a1:
                        stability = st.slider("Stability", 0.0, 1.0, 0.75, 0.01,
                                              help="Lower = more varied; Higher = more stable")
                        style = st.slider("Style", 0.0, 1.0, 0.0, 0.01,
                                          help="Higher = more expressive delivery")
                    with col_a2:
                        similarity_boost = st.slider("Similarity Boost", 0.0, 1.0, 0.75, 0.01,
                                                     help="Higher = closer to the original voice timbre")
                        speaker_boost = st.checkbox("Use Speaker Boost", value=True,
                                                     help="Boost presence/clarity of the voice")

                    st.session_state.elevenlabs_settings = {
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": stability,
                            "similarity_boost": similarity_boost,
                            "style": style,
                            "use_speaker_boost": speaker_boost,
                        }
                    }
                else:
                    st.session_state.elevenlabs_settings = {
                        "model_id": model_id,
                        "voice_settings": None  # use speed mapping
                    }
            else:
                st.error("❌ Invalid API key or connection failed. Please check your API key.")
                return
        else:
            st.warning("⚠️ Please enter your ElevenLabs API key to continue.")
            return
    elif tts_provider == "Kokoro (local open model)":
        # Require Python 3.10+ for Kokoro package
        if sys.version_info < (3, 10):
            st.error("Kokoro requires Python 3.10+. Your environment is using Python %d.%d. Please recreate the venv with Python 3.10+ to use Kokoro." % (sys.version_info.major, sys.version_info.minor))
            return
        st.markdown("#### 🧠 Kokoro Configuration (Local, Open-Weight)")

        kokoro_lang_label = st.selectbox(
            "Language:",
            options=[
                "American English (a)",
                "British English (b)",
            ],
            index=0,
            key="kokoro_lang_selector",
            help="Kokoro currently supports English best. More languages may require extra installs."
        )
        st.session_state.kokoro_lang = 'a' if kokoro_lang_label.startswith('American') else 'b'

        # Voice input with sensible default
        default_voice = 'af_heart' if st.session_state.kokoro_lang == 'a' else 'bf_yuna'
        kokoro_voice = st.text_input(
            "Voice (e.g., af_heart)",
            value=st.session_state.get('kokoro_voice', default_voice) or default_voice,
            help="Enter a Kokoro voice ID, like af_heart (US) or bf_... (UK). See the Kokoro model card for samples.",
            key="kokoro_voice_input"
        )
        st.session_state.kokoro_voice = kokoro_voice.strip() or default_voice
    
    st.markdown("### ⚡ Speed Control")
    speed_options = {
        "0.75x (Slower)": 0.75,
        "1.0x (Normal)": 1.0,
        "1.25x (Faster)": 1.25,
        "1.5x (Much Faster)": 1.5,
        "2.0x (Very Fast)": 2.0
    }

    selected_speed_label = st.selectbox(
        "Choose reading speed:",
        options=list(speed_options.keys()),
        index=1,
        key="speed_selector"
    )

    st.session_state.speed_setting = speed_options[selected_speed_label]

    text_input = st.text_area(
        "Enter text to speak:",
        placeholder="Type your message here...\n\nThis is a larger text box where you can enter multiple lines of text.",
        height=150,
        key="text_input"
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🎤 Submit", type="primary"):
            if text_input.strip():
                if tts_provider == "Mac (say command)":
                    base_rate = 150
                    adjusted_rate = int(base_rate * st.session_state.speed_setting)
                    
                    # Save audio file
                    with st.spinner("Generating audio..."):
                        filepath, metadata = save_audio_file(
                            text_input, 
                            st.session_state.speed_setting, 
                            tts_provider
                        )
                    
                    if filepath and metadata:
                        # Do NOT auto-play; just show st.audio via current_audio_file
                        st.session_state.last_spoken_text = text_input
                        st.session_state.is_speaking = False
                        st.success(f"Audio generated at {st.session_state.speed_setting}x ({adjusted_rate} WPM)")
                        st.info(f"💾 Audio saved as: {metadata['filename']}")
                        # Force rerun to render audio player below
                        st.rerun()
                    else:
                        st.error("Failed to generate audio file")
                
                elif tts_provider == "ElevenLabs":
                    if not st.session_state.elevenlabs_api_key:
                        st.error("Please enter your ElevenLabs API key first!")
                        return
                    
                    with st.spinner("Generating audio with ElevenLabs..."):
                        filepath, metadata = save_audio_file(
                            text_input,
                            st.session_state.speed_setting,
                            tts_provider,
                            st.session_state.elevenlabs_api_key,
                            st.session_state.elevenlabs_voice_id,
                            model_id=st.session_state.get("elevenlabs_settings", {}).get("model_id"),
                            voice_settings_override=st.session_state.get("elevenlabs_settings", {}).get("voice_settings"),
                        )
                    
                    if filepath and metadata:
                        # Do NOT auto-play; just show st.audio via current_audio_file
                        st.session_state.last_spoken_text = text_input
                        st.session_state.is_speaking = False
                        st.success(f"Generated ElevenLabs audio at {st.session_state.speed_setting}x speed")
                        st.info(f"💾 Audio saved as: {metadata['filename']}")
                        # Force rerun to render audio player below
                        st.rerun()
                    else:
                        st.error("Failed to generate audio with ElevenLabs. Check your API key and quota.")
                elif tts_provider == "Kokoro (local open model)":
                    with st.spinner("Generating audio with Kokoro (local)..."):
                        filepath, metadata = save_audio_file(
                            text_input,
                            st.session_state.speed_setting,
                            tts_provider,
                        )

                    if filepath and metadata:
                        st.session_state.last_spoken_text = text_input
                        st.session_state.is_speaking = False
                        st.success(f"Generated Kokoro audio at {st.session_state.speed_setting}x speed")
                        st.info(f"💾 Audio saved as: {metadata['filename']}")
                        st.rerun()
                    else:
                        st.error("Failed to generate audio with Kokoro. Check logs and internet for first-time weights download.")
                
            else:
                st.error("Please enter some text to speak!")

    with col2:
        if st.button("⏹️ Stop TTS"):
            if tts_provider == "Mac (say command)":
                os.system("killall say")
            st.session_state.is_speaking = False
            st.session_state.last_spoken_text = ""
            st.info("Stopped TTS generation")

    with col3:
        if st.button("📚 View History"):
            st.session_state.page = "📚 Audio History"
            st.rerun()

    if st.session_state.is_speaking:
        if tts_provider == "Mac (say command)":
            result = os.system("pgrep say > /dev/null 2>&1")
        else:
            result = os.system("pgrep afplay > /dev/null 2>&1")
        
        if result != 0:
            st.session_state.is_speaking = False
            st.session_state.last_spoken_text = ""

    if st.session_state.is_speaking and st.session_state.last_spoken_text:
        st.markdown('<div class="speaking-indicator">🎤 Currently Speaking...</div>', unsafe_allow_html=True)
        
        st.markdown(f"**Speed:** {st.session_state.speed_setting}x")
        
        st.markdown("### Text Being Read:")
        st.markdown(f'<div class="reading-text">{st.session_state.last_spoken_text}</div>', unsafe_allow_html=True)
        
        time.sleep(2)
        st.rerun()
    
    # Show audio player and transcript immediately after any audio file is generated
    if st.session_state.current_audio_file:
        audio_player_controls()

        # Pretty transcript under the player
        if st.session_state.last_spoken_text:
            st.markdown("### 📝 Text read")
            text = st.session_state.last_spoken_text
            words = len(text.split())
            chars = len(text)
            st.caption(f"{words} words • {chars} characters")
            st.markdown(f'<div class="reading-text">{text}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    ### Instructions:
    1. **Choose your TTS provider** — Mac (free, built-in), ElevenLabs (premium, API required), or Kokoro (local, open)
    2. **For ElevenLabs**: Enter your API key and select a voice
    3. **For Kokoro**: Choose language and voice (runs locally, no API key)
    4. **Choose your speed** — Select from 0.75x (slower) to 2.0x (very fast)
    5. **Type your message** in the large text box above (supports multiple lines)
    6. **Click Submit** to start speaking your text at the selected speed
    7. **Audio is automatically saved** and can be accessed in Audio History
    8. **Click Stop** to interrupt the speech at any time

    **TTS Providers:**
    - **Mac (say command)**: Free, built-in macOS voices, works offline
    - **ElevenLabs**: Premium AI voices, requires API key, online connection needed
    - **Kokoro (local, open-weight)**: Free, runs entirely on your machine, no API key, high‑quality neural TTS

    **Speed Options:**
    - **0.75x**: Slower, good for learning or difficult text
    - **1.0x**: Normal reading speed
    - **1.25x**: Slightly faster
    - **1.5x**: Much faster, good for familiar content  
    - **2.0x**: Very fast, for quick playback
    """)

def audio_history_page():
    st.markdown("---")
    st.markdown("### 📚 Audio History")
    
    audio_dir = Path("saved_audio")
    metadata_file = audio_dir / "metadata.json"
    
    if not metadata_file.exists():
        st.info("No audio files saved yet. Go back to the Text to Speech page to create some!")
        return
    
    with open(metadata_file, 'r') as f:
        all_metadata = json.load(f)
    
    if not all_metadata:
        st.info("No audio files found.")
        return
    
    # Sort by timestamp (newest first)
    all_metadata.sort(key=lambda x: x['timestamp'], reverse=True)
    
    st.markdown(f"**Total saved audio files: {len(all_metadata)}**")
    
    for i, metadata in enumerate(all_metadata):
        with st.expander(f"🎵 {metadata['timestamp']} - Speed: {metadata['speed']}x"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Text:** {metadata['text'][:100]}{'...' if len(metadata['text']) > 100 else ''}")
                st.markdown(f"**Speed:** {metadata['speed']}x")
                st.markdown(f"**Provider:** {metadata.get('provider', 'Mac (say command)')}")
                if metadata.get('voice_id'):
                    st.markdown(f"**Voice ID:** {metadata['voice_id']}")
                st.markdown(f"**Created:** {datetime.datetime.fromisoformat(metadata['created']).strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Show full text if long
                if len(metadata['text']) > 100:
                    if st.button(f"Show full text", key=f"show_text_{i}"):
                        st.text_area("Full text:", metadata['text'], height=100, key=f"full_text_{i}")
            
            with col2:
                filepath = audio_dir / metadata['filename']
                if filepath.exists():
                    # Play button
                    if st.button(f"▶️ Play", key=f"play_{i}"):
                        if metadata['filename'].endswith('.aiff'):
                            os.system(f'afplay "{filepath}" &')
                        else:  # mp3 or other formats
                            os.system(f'afplay "{filepath}" &')
                        st.success("Playing audio...")
                    
                    # Download button
                    with open(filepath, 'rb') as f:
                        audio_bytes = f.read()
                    
                    if metadata['filename'].endswith('.aiff'):
                        mime_type = "audio/aiff"
                    elif metadata['filename'].endswith('.mp3'):
                        mime_type = "audio/mpeg"
                    elif metadata['filename'].endswith('.wav'):
                        mime_type = "audio/wav"
                    else:
                        mime_type = "audio/mpeg"
                    
                    st.download_button(
                        label="⬇️ Download",
                        data=audio_bytes,
                        file_name=metadata['filename'],
                        mime=mime_type,
                        key=f"download_{i}"
                    )
                else:
                    st.error("File not found")
            
            # Delete button
            if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                if filepath.exists():
                    filepath.unlink()
                all_metadata.remove(metadata)
                with open(metadata_file, 'w') as f:
                    json.dump(all_metadata, f, indent=2)
                st.success("Audio file deleted!")
                st.rerun()

if page == "🎤 Text to Speech":
    main_tts_page()
elif page == "📚 Audio History":
    audio_history_page()