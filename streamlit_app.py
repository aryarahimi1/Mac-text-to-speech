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
    st.session_state.kokoro_lang = 'a'  # Default to American English
if 'chatterbox_exaggeration' not in st.session_state:
    st.session_state.chatterbox_exaggeration = 0.5
if 'chatterbox_cfg_weight' not in st.session_state:
    st.session_state.chatterbox_cfg_weight = 0.5
if 'chatterbox_temperature' not in st.session_state:
    st.session_state.chatterbox_temperature = 0.8
if 'chatterbox_audio_prompt' not in st.session_state:
    st.session_state.chatterbox_audio_prompt = None

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

def save_audio_file(text, speed_setting, tts_provider, api_key=None, voice_id=None, model_id=None, voice_settings_override=None, audio_prompt_path=None):
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
    elif tts_provider == "Chatterbox (open-source)":
        # Lazy import to avoid heavy import on non-Chatterbox paths
        try:
            import torch
            import torchaudio as ta
            from chatterbox.tts import ChatterboxTTS
        except Exception as e:
            st.error(f"Chatterbox not installed or failed to import: {e}")
            return None, None

        filename = f"tts_chatterbox_{timestamp}.wav"
        filepath = audio_dir / filename

        try:
            # Determine best device
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

            # Load model (this might take time on first run)
            model = ChatterboxTTS.from_pretrained(device=device)

            # Get settings from session state
            exaggeration = st.session_state.get('chatterbox_exaggeration', 0.5)
            cfg_weight = st.session_state.get('chatterbox_cfg_weight', 0.5)
            temperature = st.session_state.get('chatterbox_temperature', 0.8)
            
            # Generate audio
            wav = model.generate(
                text,
                audio_prompt_path=audio_prompt_path,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
                temperature=temperature,
                repetition_penalty=1.2,
                min_p=0.05,
                top_p=1.0,
            )
            
            # Save audio file
            ta.save(str(filepath), wav, model.sr)
            
        except Exception as e:
            st.error(f"Chatterbox generation failed: {e}")
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception:
                    pass
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
        "title": generate_title_from_text(text),
        "speed": speed_setting,
        "provider": tts_provider,
        "timestamp": timestamp,
        "created": datetime.datetime.now().isoformat(),
        "voice_id": voice_id if tts_provider == "ElevenLabs" else None,
        "kokoro_voice": st.session_state.get('kokoro_voice') if tts_provider == "Kokoro (local open model)" else None,
        "kokoro_lang": st.session_state.get('kokoro_lang') if tts_provider == "Kokoro (local open model)" else None,
        "chatterbox_exaggeration": st.session_state.get('chatterbox_exaggeration') if tts_provider == "Chatterbox (open-source)" else None,
        "chatterbox_cfg_weight": st.session_state.get('chatterbox_cfg_weight') if tts_provider == "Chatterbox (open-source)" else None,
        "chatterbox_temperature": st.session_state.get('chatterbox_temperature') if tts_provider == "Chatterbox (open-source)" else None,
        "audio_prompt_path": audio_prompt_path if tts_provider == "Chatterbox (open-source)" else None,
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
        ["Mac (say command)", "ElevenLabs", "Kokoro (local open model)", "Chatterbox (open-source)"],
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

        # Define available voices for each language
        kokoro_voices = {
            "🇺🇸 American English (en-us)": {
                "code": "a",
                "female": ["af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky"],
                "male": ["am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx", "am_puck"]
            },
            "🇬🇧 British English (en-gb)": {
                "code": "b",
                "female": ["bf_alice", "bf_emma", "bf_isabella", "bf_lily"],
                "male": ["bm_daniel", "bm_fable", "bm_george", "bm_lewis"]
            },
            "🇫🇷 French (fr-fr)": {
                "code": "fr",
                "female": ["ff_siwis"],
                "male": []
            },
            "🇮🇹 Italian (it)": {
                "code": "it",
                "female": ["if_sara"],
                "male": ["im_nicola"]
            },
            "🇯🇵 Japanese (ja)": {
                "code": "ja",
                "female": ["jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro"],
                "male": ["jm_kumo"]
            },
            "🇨🇳 Chinese (cmn)": {
                "code": "cmn",
                "female": ["zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi", "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang"],
                "male": []
            }
        }

        # Language selection
        selected_lang = st.selectbox(
            "🌍 Select Language:",
            options=list(kokoro_voices.keys()),
            index=0,
            key="kokoro_lang_selector",
            help="Choose the language for text-to-speech generation"
        )
        
        # Update session state with language code
        st.session_state.kokoro_lang = kokoro_voices[selected_lang]["code"]
        
        # Voice selection based on selected language
        available_voices = kokoro_voices[selected_lang]
        all_voices = []
        voice_labels = []
        
        # Add female voices
        if available_voices["female"]:
            voice_labels.append("👩 Female Voices")
            for voice in available_voices["female"]:
                all_voices.append(voice)
                voice_labels.append(f"  👩 {voice}")
        
        # Add male voices
        if available_voices["male"]:
            if available_voices["female"]:  # Only add separator if there are female voices
                voice_labels.append("👨 Male Voices")
            for voice in available_voices["male"]:
                all_voices.append(voice)
                voice_labels.append(f"  👨 {voice}")
        
        # Create a mapping from display labels to actual voice IDs
        voice_mapping = {}
        voice_index = 0
        for i, label in enumerate(voice_labels):
            if not label.startswith("  "):  # Skip category headers
                continue
            voice_mapping[label] = all_voices[voice_index]
            voice_index += 1
        
        # Default voice selection
        current_voice = st.session_state.get('kokoro_voice', available_voices["female"][0] if available_voices["female"] else available_voices["male"][0])
        
        # Find current voice in the labels
        current_label = None
        for label, voice_id in voice_mapping.items():
            if voice_id == current_voice:
                current_label = label
                break
        
        # If current voice not found in current language, use first available
        if current_label is None and voice_mapping:
            current_label = list(voice_mapping.keys())[0]
            current_voice = voice_mapping[current_label]
        
        # Voice selection dropdown
        if voice_mapping:
            selected_voice_label = st.selectbox(
                "🎤 Select Voice:",
                options=list(voice_mapping.keys()),
                index=list(voice_mapping.keys()).index(current_label) if current_label in voice_mapping else 0,
                key="kokoro_voice_selector",
                help="Choose a voice for the selected language"
            )
            st.session_state.kokoro_voice = voice_mapping[selected_voice_label]
        else:
            st.warning(f"No voices available for {selected_lang}")
            st.session_state.kokoro_voice = "af_heart"  # fallback
    
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
                elif tts_provider == "Chatterbox (open-source)":
                    # Get the audio prompt path from the current upload
                    chatterbox_audio_path = None
                    if 'chatterbox_audio_prompt_uploader' in st.session_state and st.session_state.chatterbox_audio_prompt_uploader is not None:
                        temp_dir = Path("temp_audio")
                        temp_dir.mkdir(exist_ok=True)
                        temp_audio_path = temp_dir / f"temp_{st.session_state.chatterbox_audio_prompt_uploader.name}"
                        with open(temp_audio_path, "wb") as f:
                            f.write(st.session_state.chatterbox_audio_prompt_uploader.getvalue())
                        chatterbox_audio_path = str(temp_audio_path)
                    
                    with st.spinner("Generating audio with Chatterbox (first run may take longer)..."):
                        filepath, metadata = save_audio_file(
                            text_input,
                            st.session_state.speed_setting,
                            tts_provider,
                            audio_prompt_path=chatterbox_audio_path,
                        )

                    if filepath and metadata:
                        st.session_state.last_spoken_text = text_input
                        st.session_state.is_speaking = False
                        st.success(f"Generated Chatterbox audio with exaggeration={st.session_state.chatterbox_exaggeration}")
                        st.info(f"💾 Audio saved as: {metadata['filename']}")
                        st.rerun()
                    else:
                        st.error("Failed to generate audio with Chatterbox. Check logs and ensure model can be downloaded.")
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
    1. **Choose your TTS provider** — Mac (free, built-in), ElevenLabs (premium, API required), Kokoro (local, open), or Chatterbox (state-of-the-art, open-source)
    2. **For ElevenLabs**: Enter your API key and select a voice
    3. **For Kokoro**: Choose language and voice (runs locally, no API key)
    4. **For Chatterbox**: Upload reference audio for voice cloning, adjust emotion exaggeration and pacing
    5. **Choose your speed** — Select from 0.75x (slower) to 2.0x (very fast)
    6. **Type your message** in the large text box above (supports multiple lines)
    7. **Click Submit** to start speaking your text at the selected speed
    8. **Audio is automatically saved** and can be accessed in Audio History
    9. **Click Stop** to interrupt the speech at any time

    **TTS Providers:**
    - **Mac (say command)**: Free, built-in macOS voices, works offline
    - **ElevenLabs**: Premium AI voices, requires API key, online connection needed
    - **Kokoro (local, open-weight)**: Free, runs entirely on your machine, no API key, high‑quality neural TTS
    - **Chatterbox (open-source)**: State-of-the-art TTS with emotion control and voice cloning, runs locally, watermarked outputs

    **Speed Options:**
    - **0.75x**: Slower, good for learning or difficult text
    - **1.0x**: Normal reading speed
    - **1.25x**: Slightly faster
    - **1.5x**: Much faster, good for familiar content  
    - **2.0x**: Very fast, for quick playback
    """)

def generate_title_from_text(text, max_length=50):
    """Generate a meaningful title from the text"""
    # Remove extra whitespace and normalize
    clean_text = ' '.join(text.strip().split())
    
    # If text is short enough, use it as title
    if len(clean_text) <= max_length:
        return clean_text
    
    # Try to find a good breaking point (sentence end, comma, etc.)
    sentences = clean_text.split('.')
    if len(sentences) > 1 and len(sentences[0]) <= max_length:
        return sentences[0].strip() + '.'
    
    # Try breaking at comma
    parts = clean_text.split(',')
    if len(parts) > 1 and len(parts[0]) <= max_length:
        return parts[0].strip() + '...'
    
    # Try breaking at natural word boundaries
    words = clean_text.split()
    title_words = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_length - 3:  # Leave space for "..."
            break
        title_words.append(word)
        current_length += len(word) + 1
    
    if title_words:
        return ' '.join(title_words) + '...'
    else:
        # Fallback: just truncate
        return clean_text[:max_length-3] + '...'

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
    st.markdown("---")
    
    for i, metadata in enumerate(all_metadata):
        # Use saved title if available, otherwise generate one (backward compatibility)
        title = metadata.get('title') or generate_title_from_text(metadata['text'])
        
        # Get provider icon
        provider_icons = {
            "Mac (say command)": "🖥️",
            "ElevenLabs": "🤖",
            "Kokoro (local open model)": "🧠",
            "Chatterbox (open-source)": "💬"
        }
        provider = metadata.get('provider', 'Mac (say command)')
        icon = provider_icons.get(provider, "🎵")
        
        # Create expander with title
        with st.expander(f"{icon} {title}", expanded=False):
            # Check if file exists
            filepath = audio_dir / metadata['filename']
            if not filepath.exists():
                st.error("❌ Audio file not found")
                continue
            
            # Audio player section
            st.markdown("#### 🎵 Audio Player")
            try:
                with open(filepath, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/wav' if filepath.suffix == '.wav' else 'audio/mpeg')
            except Exception as e:
                st.error(f"Error loading audio: {e}")
            
            # Metadata section
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📝 Details")
                st.markdown(f"**Full Text:**")
                st.text_area("", metadata['text'], height=100, key=f"text_display_{i}", disabled=True)
                
                st.markdown(f"**Speed:** {metadata['speed']}x")
                st.markdown(f"**Provider:** {provider}")
                
                # Provider-specific details
                if metadata.get('voice_id'):
                    st.markdown(f"**ElevenLabs Voice:** {metadata['voice_id']}")
                
                if metadata.get('kokoro_voice'):
                    st.markdown(f"**Kokoro Voice:** {metadata['kokoro_voice']}")
                    if metadata.get('kokoro_lang'):
                        lang_names = {
                            'a': 'American English',
                            'b': 'British English', 
                            'fr': 'French',
                            'it': 'Italian',
                            'ja': 'Japanese',
                            'cmn': 'Chinese'
                        }
                        lang_name = lang_names.get(metadata['kokoro_lang'], metadata['kokoro_lang'])
                        st.markdown(f"**Language:** {lang_name}")
                
                if metadata.get('chatterbox_exaggeration'):
                    st.markdown(f"**Chatterbox Exaggeration:** {metadata['chatterbox_exaggeration']}")
                    st.markdown(f"**CFG Weight:** {metadata.get('chatterbox_cfg_weight', 'N/A')}")
                    st.markdown(f"**Temperature:** {metadata.get('chatterbox_temperature', 'N/A')}")
                
                st.markdown(f"**Created:** {datetime.datetime.fromisoformat(metadata['created']).strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.markdown("#### 🛠️ Actions")
                
                # Download button
                try:
                    if metadata['filename'].endswith('.aiff'):
                        mime_type = "audio/aiff"
                    elif metadata['filename'].endswith('.mp3'):
                        mime_type = "audio/mpeg"
                    elif metadata['filename'].endswith('.wav'):
                        mime_type = "audio/wav"
                    else:
                        mime_type = "audio/mpeg"
                    
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=audio_bytes,
                        file_name=metadata['filename'],
                        mime=mime_type,
                        key=f"download_{i}",
                        use_container_width=True
                    )
                except:
                    st.error("Download not available")
                
                # Delete button
                if st.button(f"🗑️ Delete Audio", key=f"delete_{i}", use_container_width=True, type="secondary"):
                    # Confirm deletion
                    if f"confirm_delete_{i}" not in st.session_state:
                        st.session_state[f"confirm_delete_{i}"] = False
                    
                    if not st.session_state[f"confirm_delete_{i}"]:
                        st.session_state[f"confirm_delete_{i}"] = True
                        st.warning("⚠️ Click delete again to confirm!")
                        st.rerun()
                    else:
                        # Actually delete
                        if filepath.exists():
                            filepath.unlink()
                        all_metadata.remove(metadata)
                        with open(metadata_file, 'w') as f:
                            json.dump(all_metadata, f, indent=2)
                        st.success("✅ Audio file deleted!")
                        # Clear confirmation state
                        del st.session_state[f"confirm_delete_{i}"]
                        st.rerun()
            
            st.markdown("---")

if page == "🎤 Text to Speech":
    main_tts_page()
elif page == "📚 Audio History":
    audio_history_page()