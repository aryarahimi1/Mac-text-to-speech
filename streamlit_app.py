import streamlit as st
import os
import time

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

if 'last_spoken_text' not in st.session_state:
    st.session_state.last_spoken_text = ""
if 'is_speaking' not in st.session_state:
    st.session_state.is_speaking = False
if 'speed_setting' not in st.session_state:
    st.session_state.speed_setting = 1.0

st.title("🗣️ Text to Speech")
st.markdown("---")

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

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🎤 Submit", type="primary"):
        if text_input.strip():
            base_rate = 150
            adjusted_rate = int(base_rate * st.session_state.speed_setting)
            
            os.system(f'say -r {adjusted_rate} "{text_input}" &')
            st.session_state.last_spoken_text = text_input
            st.session_state.is_speaking = True
            st.success(f"Started speaking at {st.session_state.speed_setting}x speed ({adjusted_rate} WPM)...")
            time.sleep(0.3)
            st.rerun()
        else:
            st.error("Please enter some text to speak!")

with col2:
    if st.button("⏹️ Stop"):
        os.system("killall say")
        st.session_state.is_speaking = False
        st.session_state.last_spoken_text = ""
        st.info("Stopped speaking")

if st.session_state.is_speaking:
    result = os.system("pgrep say > /dev/null 2>&1")
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

st.markdown("---")
st.markdown("""
### Instructions:
1. **Choose your speed** - Select from 0.75x (slower) to 2.0x (very fast)
2. **Type your message** in the large text box above (supports multiple lines)
3. **Click Submit** to start speaking your text at the selected speed
4. **See the text being read** displayed below with current speed
5. **Click Stop** to interrupt the speech at any time

**Speed Options:**
- **0.75x**: Slower, good for learning or difficult text
- **1.0x**: Normal reading speed
- **1.25x**: Slightly faster
- **1.5x**: Much faster, good for familiar content  
- **2.0x**: Very fast, for quick playback
""")
