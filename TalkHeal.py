import streamlit as st

# ✅ MUST be the first Streamlit command
st.set_page_config(
    page_title="TalkHeal",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state=st.session_state.get("sidebar_state", "expanded")
)

import google.generativeai as genai
from core.utils import save_conversations, load_conversations
from core.config import configure_gemini, PAGE_CONFIG
from core.utils import get_current_time, create_new_conversation
from css.styles import apply_custom_css
from components.header import render_header
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface, handle_chat_input

# from components.emergency_page import render_emergency_page
from components.focus_session import render_focus_session

from components.emergency_page import render_emergency_page
from components.profile import apply_global_font_size


# --- 1. INITIALIZE SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()
if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = -1
# if "show_emergency_page" not in st.session_state:
#     st.session_state.show_emergency_page = False
if "show_focus_session" not in st.session_state:
    st.session_state.show_focus_session = False
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"
if "mental_disorders" not in st.session_state:
    st.session_state.mental_disorders = [
        "Depression & Mood Disorders", "Anxiety & Panic Disorders", "Bipolar Disorder",
        "PTSD & Trauma", "OCD & Related Disorders", "Eating Disorders",
        "Substance Use Disorders", "ADHD & Neurodevelopmental", "Personality Disorders",
        "Sleep Disorders"
    ]
if "selected_tone" not in st.session_state:
    st.session_state.selected_tone = "Compassionate Listener"

# --- 2. SET PAGE CONFIG ---
apply_global_font_size()


# --- 3. APPLY STYLES & CONFIGURATIONS ---
apply_custom_css()
model = configure_gemini()

# --- 4. TONE SELECTION DROPDOWN IN SIDEBAR ---
TONE_OPTIONS = {
    "Compassionate Listener": "You are a compassionate listener — soft, empathetic, patient — like a therapist who listens without judgment.",
    "Motivating Coach": "You are a motivating coach — energetic, encouraging, and action-focused — helping the user push through rough days.",
    "Wise Friend": "You are a wise friend — thoughtful, poetic, and reflective — giving soulful responses and timeless advice.",
    "Neutral Therapist": "You are a neutral therapist — balanced, logical, and non-intrusive — asking guiding questions using CBT techniques.",
    "Mindfulness Guide": "You are a mindfulness guide — calm, slow, and grounding — focused on breathing, presence, and awareness."
}

with st.sidebar:
    st.header("🧠 Choose Your AI Tone")
    selected_tone = st.selectbox(
        "Select a personality tone:",
        options=list(TONE_OPTIONS.keys()),
        index=0
    )
    st.session_state.selected_tone = selected_tone

# --- 5. DEFINE FUNCTION TO GET TONE PROMPT ---
def get_tone_prompt():
    return TONE_OPTIONS.get(st.session_state.get("selected_tone", "Compassionate Listener"), TONE_OPTIONS["Compassionate Listener"])

# --- 6. RENDER SIDEBAR ---
render_sidebar()

# --- 7. PAGE ROUTING ---
main_area = st.container()

if not st.session_state.conversations:
    saved_conversations = load_conversations()
    if saved_conversations:
        st.session_state.conversations = saved_conversations
        if st.session_state.active_conversation == -1:
            st.session_state.active_conversation = 0
    else:
        create_new_conversation()
        st.session_state.active_conversation = 0
    st.rerun()

# --- 8. RENDER PAGE ---
# if st.session_state.get("show_emergency_page"):
#     with main_area:
#         render_emergency_page()
# else:
if st.session_state.get("show_focus_session"):
    with main_area:
        render_focus_session()
else:
    with main_area:
        render_header()
        st.markdown(f"""
<div style="text-align: center; margin: 20px 0;">
    <h3>🗣️ Current Chatbot Tone: <strong>{st.session_state['selected_tone']}</strong></h3>
</div>
""", unsafe_allow_html=True)
        render_chat_interface()
        handle_chat_input(model, system_prompt=get_tone_prompt())

# --- 9. SCROLL SCRIPT ---
st.markdown("""
<script>
    function scrollToBottom() {
        var chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    setTimeout(scrollToBottom, 100);
</script>
""", unsafe_allow_html=True) 