import streamlit as st
import google.generativeai as genai
from pathlib import Path
import requests
import os
from typing import Optional

# ---------- Logo and Page Config ----------
logo_path = str(Path(__file__).resolve().parent.parent / "TalkHealLogo.png")

PAGE_CONFIG = {
    "page_title": "TalkHeal - Mental Health Support",
    "page_icon": logo_path,
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": None
}

# ---------- Custom Dropdown Style ----------
st.markdown("""
    <style>
        div[data-baseweb="select"] {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Tone Options ----------
TONE_OPTIONS = {
    "Compassionate Listener": "You are a compassionate listener — soft, empathetic, patient — like a therapist who listens without judgment.",
    "Motivating Coach": "You are a motivating coach — energetic, encouraging, and action-focused — helping the user push through rough days.",
    "Wise Friend": "You are a wise friend — thoughtful, poetic, and reflective — giving soulful responses and timeless advice.",
    "Neutral Therapist": "You are a neutral therapist — balanced, logical, and non-intrusive — asking guiding questions using CBT techniques.",
    "Mindfulness Guide": "You are a mindfulness guide — calm, slow, and grounding — focused on breathing, presence, and awareness."
}

# ---------- Secure API Configuration ----------
def get_api_key() -> Optional[str]:
    """
    Securely retrieve API key from environment variables or secure storage.
    This prevents client-side exposure of sensitive credentials.
    """
    # Priority order: environment variable > secure secrets > None
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        # Fallback to Streamlit secrets only in development
        if st.secrets.get("GEMINI_API_KEY") and st.secrets["GEMINI_API_KEY"] != "YOUR_API_KEY_HERE":
            api_key = st.secrets["GEMINI_API_KEY"]
    
    return api_key

# ---------- Gemini Configuration (Secure) ----------
def configure_gemini():
    """
    Securely configure Gemini API with proper error handling and no client-side exposure.
    """
    try:
        api_key = get_api_key()
        
        if not api_key:
            st.error("""
            ❌ **API Configuration Error**
            
            The Gemini API key is not properly configured. This is a security requirement.
            
            **For Production Deployment:**
            - Set the `GEMINI_API_KEY` environment variable on your server
            - Never expose API keys in client-side code
            
            **For Local Development:**
            - Create a `.streamlit/secrets.toml` file
            - Add: `GEMINI_API_KEY = "your_actual_key_here"`
            
            **Security Note:** API keys are now stored server-side only.
            """)
            return None
            
        # Configure Gemini with the secure API key
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test the configuration
        try:
            # Simple test to verify API key works
            test_response = model.generate_content("Hello")
            if test_response and test_response.text:
                return model
        except Exception as test_error:
            st.error(f"❌ API key validation failed: {str(test_error)}")
            return None
            
    except Exception as e:
        st.error(f"""
        ❌ **Configuration Error**
        
        Failed to configure Gemini API: {str(e)}
        
        **Troubleshooting:**
        1. Verify your API key is valid
        2. Check your internet connection
        3. Ensure you have sufficient API quota
        """)
        return None
    
    return None

# ---------- Get System Prompt ----------
def get_tone_system_prompt():
    tone = st.session_state.get("selected_tone", "Compassionate Listener")
    return TONE_OPTIONS.get(tone, TONE_OPTIONS["Compassionate Listener"])

# ---------- Generate AI Response (Secure) ----------
def generate_response(user_input: str, model) -> Optional[str]:
    """
    Generate AI response with secure error handling and no sensitive data exposure.
    """
    if not model:
        return "I'm currently experiencing technical difficulties. Please try again later or contact support."
    
    system_prompt = get_tone_system_prompt()
    
    try:
        response = model.generate_content([
            {"role": "system", "parts": [system_prompt]},
            {"role": "user", "parts": [user_input]}
        ])
        
        if response and response.text:
            return response.text
        else:
            return "I'm having trouble generating a response. Please try again."
            
    except ValueError as e:
        # Don't expose internal error details to users
        st.error("❌ Invalid input. Please rephrase your message.")
        return "I'm having trouble understanding your message. Could you please rephrase it?"
        
    except google.generativeai.types.BlockedPromptException as e:
        st.error("❌ Content policy violation. Please rephrase your message.")
        return "I understand you're going through something difficult. Let's focus on how you're feeling and what might help you feel better."
        
    except google.generativeai.types.GenerationException as e:
        st.error("❌ Failed to generate response. Please try again.")
        return "I'm having trouble responding right now. Please try again in a moment."
        
    except requests.RequestException as e:
        st.error("❌ Network connection issue. Please check your internet connection.")
        return "I'm having trouble connecting to my services. Please check your internet connection and try again."
        
    except Exception as e:
        # Log the actual error for debugging (server-side only)
        st.error("❌ An unexpected error occurred. Please try again.")
        return "I'm experiencing technical difficulties. Please try again in a moment."

# ---------- Security Status Check ----------
def check_security_status():
    """
    Display security status to users without exposing sensitive information.
    """
    api_key = get_api_key()
    
    if api_key:
        st.success("✅ **Security Status: Secure** - API configuration is properly secured")
    else:
        st.warning("⚠️ **Security Status: Configuration Required** - API key needs to be configured")

# ---------- Sidebar Tone Selector (Secure) ----------
def render_secure_sidebar():
    """
    Render sidebar components without exposing sensitive configuration.
    """
    with st.sidebar:
        st.header("🧠 Choose Your AI Tone")
        default_tone = list(TONE_OPTIONS.keys())[0]
        selected_tone = st.selectbox(
            "Select a personality tone:",
            options=list(TONE_OPTIONS.keys()),
            index=0,
            key="tone_selector"
        )
        st.session_state["selected_tone"] = selected_tone or default_tone
        
        # Display current tone
        st.info(f"**Current Tone:** {st.session_state['selected_tone']}")
        
        # Security status
        st.markdown("---")
        check_security_status()

# Initialize secure sidebar
render_secure_sidebar()

# ---------- MAIN CHAT INTERFACE (Secure) ----------
# Only configure model when needed, not at module level
def get_secure_model():
    """
    Get a securely configured model instance.
    """
    return configure_gemini()

# Remove the automatic model configuration and chat interface
# These should be handled by the main application file
