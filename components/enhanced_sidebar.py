import streamlit as st
from core.emotion_ai import emotion_ai, EmotionType, CrisisLevel
from datetime import datetime, timedelta
import json

def render_emotion_quick_actions():
    """Render quick emotion-based actions in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Quick Actions")
    
    # Quick mood check
    if st.sidebar.button("😊 Quick Mood Check", use_container_width=True):
        st.session_state.show_quick_mood_check = True
    
    # Crisis support
    if st.sidebar.button("🚨 Crisis Support", use_container_width=True):
        st.session_state.show_crisis_support = True
    
    # Wellness tips
    if st.sidebar.button("🌟 Get Wellness Tips", use_container_width=True):
        st.session_state.show_wellness_tips = True

def render_emotion_status():
    """Render current emotional status in sidebar"""
    if not emotion_ai.emotion_history:
        return
    
    current_emotion = emotion_ai.emotion_history[-1]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💭 Current Emotional State")
    
    # Emotion indicator
    emotion_emoji = {
        "joy": "😊",
        "sadness": "😢", 
        "anxiety": "😰",
        "fear": "😨",
        "anger": "😠",
        "calm": "😌",
        "excitement": "🤩",
        "gratitude": "🙏",
        "hopelessness": "😞"
    }
    
    emoji = emotion_emoji.get(current_emotion.primary_emotion.value, "😐")
    emotion_name = current_emotion.primary_emotion.value.title()
    intensity = current_emotion.intensity
    
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea0d, #764ba20d); 
                border-radius: 10px; margin: 10px 0;">
        <div style="font-size: 48px; margin-bottom: 10px;">{emoji}</div>
        <h4 style="margin: 0; color: #667eea;">{emotion_name}</h4>
        <p style="margin: 5px 0; color: #666;">Intensity: {intensity:.0%}</p>
        <div style="background: #eee; height: 6px; border-radius: 3px; overflow: hidden; margin: 10px 0;">
            <div style="background: #667eea; height: 100%; width: {intensity * 100}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Crisis level indicator
    if current_emotion.crisis_level != CrisisLevel.NONE:
        crisis_colors = {
            CrisisLevel.LOW: "#FFCC00",
            CrisisLevel.MEDIUM: "#FF6600",
            CrisisLevel.HIGH: "#FF3300",
            CrisisLevel.CRITICAL: "#FF0000"
        }
        crisis_color = crisis_colors.get(current_emotion.crisis_level, "#FF0000")
        
        st.sidebar.markdown(f"""
        <div style="background: {crisis_color}20; border: 2px solid {crisis_color}; 
                    border-radius: 8px; padding: 10px; margin: 10px 0; text-align: center;">
            <strong style="color: {crisis_color};">⚠️ Crisis Level: {current_emotion.crisis_level.value.upper()}</strong>
        </div>
        """, unsafe_allow_html=True)

def render_emotional_trends():
    """Render emotional trends in sidebar"""
    if not emotion_ai.emotion_history:
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Emotional Trends")
    
    # Analyze last 7 days
    trends = emotion_ai.analyze_emotional_trends(days=7)
    
    if "error" not in trends:
        # Overall trend
        trend = trends["trend"]
        trend_emoji = {
            "improving": "📈",
            "stable": "➡️",
            "concerning": "📉"
        }
        emoji = trend_emoji.get(trend, "➡️")
        
        st.sidebar.metric(
            f"{emoji} Overall Trend",
            trend.title(),
            delta=f"Last 7 days"
        )
        
        # Crisis frequency
        crisis_count = trends["crisis_frequency"]
        if crisis_count > 0:
            st.sidebar.markdown(f"""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; 
                        padding: 8px; margin: 5px 0; text-align: center;">
                <span style="color: #856404; font-size: 12px;">
                    ⚠️ {crisis_count} crisis event{'s' if crisis_count > 1 else ''} detected
                </span>
            </div>
            """, unsafe_allow_html=True)

def render_wellness_quick_tips():
    """Render quick wellness tips based on current emotional state"""
    if not emotion_ai.emotion_history:
        return
    
    current_emotion = emotion_ai.emotion_history[-1]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌟 Quick Wellness Tip")
    
    # Get a single quick tip
    recommendations = emotion_ai.get_wellness_recommendations(current_emotion)
    
    if recommendations:
        tip = recommendations[0]  # Show first recommendation
        
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea0d, #764ba20d); 
                    border-radius: 8px; padding: 12px; margin: 10px 0; 
                    border-left: 4px solid #667eea;">
            <p style="margin: 0; font-size: 13px; line-height: 1.4; color: #555;">
                {tip}
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_enhanced_sidebar():
    """Render enhanced sidebar with EmotionSense AI features"""
    
    # Main navigation
    st.sidebar.markdown("## 🧠 TalkHeal with EmotionSense AI")
    st.sidebar.markdown("Your intelligent mental health companion")
    
    # Navigation options
    page_options = {
        "💬 Enhanced Chat": "enhanced_chat",
        "📊 Emotion Dashboard": "emotion_dashboard", 
        "🎯 Focus Session": "focus_session",
        "📝 Journaling": "journaling",
        "🧘‍♀️ Yoga & Wellness": "yoga",
        "🚨 Emergency Support": "emergency",
        "👤 Profile": "profile"
    }
    
    selected_page = st.sidebar.selectbox(
        "Navigate to:",
        options=list(page_options.keys()),
        key="enhanced_sidebar_nav"
    )
    
    # Update session state
    st.session_state.selected_page = page_options[selected_page]
    
    # EmotionSense AI features
    render_emotion_status()
    render_emotional_trends()
    render_wellness_quick_tips()
    render_emotion_quick_actions()
    
    # User profile section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 User Profile")
    
    if "user_name" in st.session_state:
        st.sidebar.markdown(f"**Welcome, {st.session_state.user_name}!**")
        
        # Communication style preference
        communication_style = st.sidebar.selectbox(
            "Communication Style:",
            ["compassionate", "direct", "gentle", "professional"],
            key="communication_style"
        )
        
        # Update user profile
        emotion_ai.update_user_profile({
            "communication_style": communication_style
        })
        
        # Cultural background
        cultural_background = st.sidebar.selectbox(
            "Cultural Background:",
            ["general", "western", "eastern", "african", "latin", "middle_eastern", "other"],
            key="cultural_background"
        )
        
        emotion_ai.update_user_profile({
            "cultural_background": cultural_background
        })
    
    # Settings
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    
    # Emotion detection sensitivity
    sensitivity = st.sidebar.slider(
        "Emotion Detection Sensitivity:",
        min_value=0.1,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher sensitivity detects more subtle emotions"
    )
    
    # Crisis detection threshold
    crisis_threshold = st.sidebar.slider(
        "Crisis Detection Threshold:",
        min_value=0.3,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower threshold triggers crisis detection earlier"
    )
    
    # Export data
    if st.sidebar.button("📊 Export My Data", use_container_width=True):
        data = emotion_ai.export_emotional_data()
        st.sidebar.download_button(
            label="Download JSON",
            data=json.dumps(data, indent=2),
            file_name=f"talkheal_emotion_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # About EmotionSense AI
    with st.sidebar.expander("ℹ️ About EmotionSense AI"):
        st.markdown("""
        **EmotionSense AI** is TalkHeal's revolutionary emotional intelligence system that:
        
        • **Detects emotions** from your messages in real-time
        • **Adapts responses** based on your emotional state
        • **Provides crisis intervention** when needed
        • **Tracks patterns** to understand your emotional journey
        • **Offers personalized** wellness recommendations
        
        Your privacy is protected - all emotion analysis happens locally.
        """)
    
    # Crisis resources
    with st.sidebar.expander("🚨 Crisis Resources"):
        st.markdown("""
        **Immediate Help Available:**
        
        • **988** - Suicide & Crisis Lifeline
        • **911** - Emergency Services  
        • **Text HOME to 741741** - Crisis Text Line
        
        **You are not alone.** Help is available 24/7.
        """)
    
    return selected_page

def handle_sidebar_actions():
    """Handle sidebar actions and state changes"""
    
    # Quick mood check
    if st.session_state.get("show_quick_mood_check", False):
        st.session_state.show_quick_mood_check = False
        st.session_state.show_quick_mood_modal = True
    
    # Crisis support
    if st.session_state.get("show_crisis_support", False):
        st.session_state.show_crisis_support = False
        st.session_state.show_crisis_modal = True
    
    # Wellness tips
    if st.session_state.get("show_wellness_tips", False):
        st.session_state.show_wellness_tips = False
        st.session_state.show_wellness_modal = True

def render_quick_mood_modal():
    """Render quick mood check modal"""
    if st.session_state.get("show_quick_mood_modal", False):
        with st.modal("😊 Quick Mood Check"):
            st.markdown("### How are you feeling right now?")
            
            mood_options = {
                "😊 Great": "joy",
                "😌 Calm": "calm", 
                "😢 Sad": "sadness",
                "😰 Anxious": "anxiety",
                "😠 Angry": "anger",
                "😨 Scared": "fear",
                "😞 Hopeless": "hopelessness",
                "🙏 Grateful": "gratitude"
            }
            
            selected_mood = st.selectbox(
                "Choose your mood:",
                options=list(mood_options.keys()),
                key="quick_mood_select"
            )
            
            intensity = st.slider(
                "How intense is this feeling?",
                min_value=0.1,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit", use_container_width=True):
                    # Create emotional state
                    emotion_type = EmotionType(mood_options[selected_mood])
                    emotional_state = emotion_ai.EmotionalState(
                        primary_emotion=emotion_type,
                        intensity=intensity,
                        confidence=0.9,
                        timestamp=datetime.now(),
                        context={"source": "quick_mood_check"},
                        crisis_level=emotion_ai._assess_crisis_level("", {emotion_type: intensity}, False)
                    )
                    
                    emotion_ai.emotion_history.append(emotional_state)
                    st.session_state.show_quick_mood_modal = False
                    st.rerun()
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_quick_mood_modal = False
                    st.rerun()

def render_crisis_modal():
    """Render crisis support modal"""
    if st.session_state.get("show_crisis_modal", False):
        with st.modal("🚨 Crisis Support"):
            st.markdown("""
            ## You're Not Alone
            
            **Immediate Support Available:**
            
            • **988** - Suicide & Crisis Lifeline (24/7)
            • **911** - Emergency Services
            • **Text HOME to 741741** - Crisis Text Line
            
            **Talk to someone you trust:**
            • Family member or friend
            • Mental health professional
            • Religious/spiritual leader
            • School counselor or teacher
            
            **Remember:**
            • Your feelings are valid
            • This moment will pass
            • Help is available
            • You matter
            """)
            
            if st.button("I understand", use_container_width=True):
                st.session_state.show_crisis_modal = False
                st.rerun()

def render_wellness_modal():
    """Render wellness tips modal"""
    if st.session_state.get("show_wellness_modal", False):
        with st.modal("🌟 Wellness Tips"):
            st.markdown("## Personalized Wellness Recommendations")
            
            if emotion_ai.emotion_history:
                current_emotion = emotion_ai.emotion_history[-1]
                recommendations = emotion_ai.get_wellness_recommendations(current_emotion)
                
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.markdown("""
                **General Wellness Tips:**
                
                1. 🫁 Practice deep breathing exercises
                2. 🚶‍♀️ Take a short walk outside
                3. 💧 Stay hydrated throughout the day
                4. 😴 Ensure you get enough sleep
                5. 🎵 Listen to calming music
                6. 📝 Write down your thoughts
                7. 🧘‍♀️ Try simple meditation
                8. 🐕 Spend time with pets or loved ones
                """)
            
            if st.button("Got it!", use_container_width=True):
                st.session_state.show_wellness_modal = False
                st.rerun()
