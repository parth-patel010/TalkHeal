import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from core.emotion_ai import emotion_ai, EmotionType, CrisisLevel
from components.enhanced_chat_interface import render_emotion_dashboard
import json

def render_emotion_sense_ai_page():
    """Main EmotionSense AI page"""
    
    st.set_page_config(
        page_title="EmotionSense AI - TalkHeal",
        page_icon="🧠",
        layout="wide"
    )
    
    # Initialize session state variables if they don't exist
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    elif not isinstance(st.session_state.conversations, list):
        st.session_state.conversations = []
    
    if "active_conversation" not in st.session_state:
        st.session_state.active_conversation = -1
    elif not isinstance(st.session_state.active_conversation, int):
        st.session_state.active_conversation = -1
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    elif not isinstance(st.session_state.chat_history, list):
        st.session_state.chat_history = []
    
    # Page header
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea0d, #764ba20d); 
                border-radius: 20px; margin: 20px 0;">
        <h1 style="color: #667eea; margin-bottom: 15px; font-size: 3em;">🧠 EmotionSense AI</h1>
        <p style="font-size: 1.2em; color: #555; line-height: 1.6;">
            Your intelligent mental health companion that understands emotions, adapts responses, 
            and provides personalized support in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Enhanced Chat", "📊 Emotion Dashboard", "⚙️ Settings"])
    
    with tab1:
        render_enhanced_chat_tab()
    
    with tab2:
        render_emotion_dashboard_tab()
    
    with tab3:
        render_settings_tab()

def render_enhanced_chat_tab():
    """Enhanced chat interface tab"""
    st.markdown("## 💬 Enhanced Chat with Emotional Intelligence")
    
    # Add New Conversation button
    if st.button("🆕 Start New Conversation", type="primary"):
        from core.utils import create_new_conversation
        new_convo = create_new_conversation()
        st.session_state.conversations.append(new_convo)
        st.session_state.active_conversation = len(st.session_state.conversations) - 1
        st.rerun()
    
    # Chat interface
    if st.session_state.active_conversation >= 0 and st.session_state.active_conversation < len(st.session_state.conversations):
        active_convo = st.session_state.conversations[st.session_state.active_conversation]
        
        # Display chat messages
        if not active_convo["messages"]:
            st.info("Start a conversation to use the enhanced chat features!")
        else:
            for msg in active_convo["messages"]:
                if msg["sender"] == "user":
                    st.markdown(f"**You:** {msg['message']}")
                    if "emotion_analysis" in msg:
                        emotion_data = msg["emotion_analysis"]
                        st.info(f"EmotionSense AI detected: {emotion_data['emotion'].title()}")
                else:
                    st.markdown(f"**AI:** {msg['message']}")
        
        # Chat input
        st.markdown("---")
        with st.form(key="emotion_chat_form", clear_on_submit=True):
            user_input = st.text_area("Share your thoughts...", height=100)
            send_pressed = st.form_submit_button("Send Message")
        
        if send_pressed and user_input.strip():
            # Process message with EmotionSense AI
            emotional_state = emotion_ai.detect_emotion_from_text(user_input.strip())
            ai_response = emotion_ai.generate_adaptive_response(emotional_state, user_input.strip())
            
            # Save messages
            current_time = datetime.now().strftime("%H:%M")
            
            user_message = {
                "sender": "user",
                "message": user_input.strip(),
                "time": current_time,
                "emotion_analysis": {
                    "emotion": emotional_state.primary_emotion.value,
                    "intensity": emotional_state.intensity,
                    "confidence": emotional_state.confidence,
                    "crisis_level": emotional_state.crisis_level.value
                }
            }
            
            ai_message = {
                "sender": "bot",
                "message": ai_response,
                "time": current_time
            }
            
            active_convo["messages"].extend([user_message, ai_message])
            
            # Save conversations
            from core.utils import save_conversations
            save_conversations(st.session_state.conversations)
            
            st.rerun()
    
    else:
        st.info("Please start a new conversation to use the enhanced chat features.")
        st.markdown("Click the 'Start New Conversation' button above to begin chatting with EmotionSense AI.")

def render_emotion_dashboard_tab():
    """Emotion dashboard tab"""
    st.markdown("## 📊 EmotionSense AI Dashboard")
    
    if not emotion_ai.emotion_history:
        st.info("No emotional data available yet. Start chatting to see your emotional insights!")
        return
    
    # Current emotional state
    current_emotion = emotion_ai.emotion_history[-1]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Emotional State")
        st.info(f"**Emotion:** {current_emotion.primary_emotion.value.title()}")
        st.info(f"**Intensity:** {current_emotion.intensity:.1%}")
        st.info(f"**Crisis Level:** {current_emotion.crisis_level.value}")
    
    with col2:
        st.markdown("### Quick Stats")
        st.metric("Total Emotions", len(emotion_ai.emotion_history))
        
        today = datetime.now().date()
        today_emotions = [e for e in emotion_ai.emotion_history if e.timestamp.date() == today]
        st.metric("Today's Emotions", len(today_emotions))
    
    # Emotional trends
    st.markdown("### 📈 Emotional Trends (Last 7 Days)")
    
    trends = emotion_ai.analyze_emotional_trends(days=7)
    
    if "error" not in trends:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Emotions", trends["total_emotions"])
        
        with col2:
            st.metric("Average Intensity", f"{trends['average_intensity']:.1%}")
        
        with col3:
            st.metric("Crisis Frequency", trends["crisis_frequency"])
        
        # Overall trend
        trend = trends["trend"]
        st.success(f"Overall Trend: {trend.title()}")

def render_settings_tab():
    """Settings tab"""
    st.markdown("## ⚙️ Settings & Profile")
    
    # Communication preferences
    st.markdown("### Communication Preferences")
    
    communication_style = st.selectbox(
        "Preferred Communication Style:",
        ["compassionate", "direct", "gentle", "professional"]
    )
    
    cultural_background = st.selectbox(
        "Cultural Background:",
        ["general", "western", "eastern", "african", "latin", "middle_eastern", "other"]
    )
    
    # Update profile
    if st.button("Save Profile Settings"):
        emotion_ai.update_user_profile({
            "communication_style": communication_style,
            "cultural_background": cultural_background
        })
        st.success("Profile settings saved successfully!")
    
    # Export data
    st.markdown("### Data Management")
    if st.button("Export My Data"):
        data = emotion_ai.export_emotional_data()
        st.download_button(
            label="Download JSON",
            data=json.dumps(data, indent=2),
            file_name=f"emotion_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    render_emotion_sense_ai_page()
