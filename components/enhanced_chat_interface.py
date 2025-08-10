import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import time
from typing import Dict, Any
from core.utils import get_current_time, save_conversations
from core.emotion_ai import emotion_ai, EmotionType, CrisisLevel

class TypingPatternTracker:
    def __init__(self):
        self.start_time = None
        self.typing_speed = 0
        self.backspace_count = 0
        self.pause_count = 0
        self.last_keystroke = None
    
    def start_typing(self):
        self.start_time = time.time()
        self.typing_speed = 0
        self.backspace_count = 0
        self.pause_count = 0
    
    def record_keystroke(self, is_backspace=False):
        current_time = time.time()
        
        if is_backspace:
            self.backspace_count += 1
        
        if self.last_keystroke:
            pause = current_time - self.last_keystroke
            if pause > 2.0:  # Pause longer than 2 seconds
                self.pause_count += 1
        
        self.last_keystroke = current_time
    
    def finish_typing(self, text_length: int) -> Dict[str, Any]:
        if not self.start_time:
            return {}
        
        duration = time.time() - self.start_time
        if duration > 0 and text_length > 0:
            self.typing_speed = text_length / duration  # characters per second
        
        return {
            "typing_speed": round(self.typing_speed, 2),
            "backspace_count": self.backspace_count,
            "pause_count": self.pause_count,
            "typing_duration": round(duration, 2),
            "text_length": text_length
        }

def render_emotion_visualization(emotional_state):
    """Render visual representation of detected emotions"""
    if not emotional_state:
        return
    
    emotion = emotional_state.primary_emotion.value
    intensity = emotional_state.intensity
    crisis_level = emotional_state.crisis_level
    
    # Color coding based on emotion and crisis level
    if crisis_level == CrisisLevel.CRITICAL:
        color = "#FF0000"  # Red for critical
        emoji = "🚨"
    elif crisis_level == CrisisLevel.HIGH:
        color = "#FF6600"  # Orange for high
        emoji = "⚠️"
    elif emotion in ["sadness", "anxiety", "fear", "hopelessness"]:
        color = "#0066FF"  # Blue for negative emotions
        emoji = "💙"
    elif emotion in ["joy", "gratitude", "calm"]:
        color = "#00CC00"  # Green for positive emotions
        emoji = "💚"
    else:
        color = "#FFCC00"  # Yellow for neutral
        emoji = "💛"
    
    # Emotion intensity bar
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {color}20, {color}80); 
                border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 5px solid {color};">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">{emoji}</span>
            <div style="flex-grow: 1;">
                <h4 style="margin: 0; color: {color}; text-transform: capitalize;">{emotion}</h4>
                <p style="margin: 5px 0; color: #666;">Intensity: {intensity:.1%}</p>
                <div style="background: #eee; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: {color}; height: 100%; width: {intensity * 100}%; transition: width 0.3s ease;"></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Crisis level indicator
    if crisis_level != CrisisLevel.NONE:
        crisis_colors = {
            CrisisLevel.LOW: "#FFCC00",
            CrisisLevel.MEDIUM: "#FF6600", 
            CrisisLevel.HIGH: "#FF3300",
            CrisisLevel.CRITICAL: "#FF0000"
        }
        crisis_color = crisis_colors.get(crisis_level, "#FF0000")
        
        st.markdown(f"""
        <div style="background: {crisis_color}20; border: 2px solid {crisis_color}; 
                    border-radius: 8px; padding: 10px; margin: 10px 0; text-align: center;">
            <strong style="color: {crisis_color};">Crisis Level: {crisis_level.value.upper()}</strong>
        </div>
        """, unsafe_allow_html=True)

def render_wellness_recommendations(emotional_state):
    """Render personalized wellness recommendations"""
    if not emotional_state:
        return
    
    recommendations = emotion_ai.get_wellness_recommendations(emotional_state)
    
    if recommendations:
        st.markdown("### 🌟 Personalized Wellness Tips")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea0d, #764ba20d); 
                        border-radius: 8px; padding: 12px; margin: 8px 0; 
                        border-left: 4px solid #667eea;">
                <p style="margin: 0; font-size: 14px;">{rec}</p>
            </div>
            """, unsafe_allow_html=True)

def render_emotional_insights():
    """Render emotional insights and trends"""
    if not emotion_ai.emotion_history:
        return
    
    st.markdown("### 📊 Emotional Insights")
    
    # Recent emotions
    recent_emotions = emotion_ai.emotion_history[-5:]  # Last 5 emotions
    
    for emotion in recent_emotions:
        time_ago = datetime.now() - emotion.timestamp
        if time_ago.days > 0:
            time_str = f"{time_ago.days} day{'s' if time_ago.days > 1 else ''} ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600} hour{'s' if time_ago.seconds // 3600 > 1 else ''} ago"
        else:
            time_str = f"{time_ago.seconds // 60} minute{'s' if time_ago.seconds // 60 > 1 else ''} ago"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0; padding: 8px; 
                    background: #f8f9fa; border-radius: 6px;">
            <span style="font-size: 16px;">{emotion.primary_emotion.value.upper()}</span>
            <span style="color: #666; font-size: 12px;">{time_str}</span>
            <span style="margin-left: auto; color: #999; font-size: 12px;">{emotion.intensity:.0%}</span>
        </div>
        """, unsafe_allow_html=True)

def render_enhanced_chat_interface():
    """Enhanced chat interface with EmotionSense AI integration"""
    if st.session_state.active_conversation >= 0:
        active_convo = st.session_state.conversations[st.session_state.active_conversation]
        
        # Initialize typing tracker
        if "typing_tracker" not in st.session_state:
            st.session_state.typing_tracker = TypingPatternTracker()
        
        # Display welcome message
        if not active_convo["messages"]:
            st.markdown(f"""
            <div class="welcome-message" style="background: linear-gradient(135deg, #667eea0d, #764ba20d); 
                        border-radius: 15px; padding: 25px; margin: 20px 0; text-align: center;">
                <h3 style="color: #667eea; margin-bottom: 15px;">🤗 Hello! I'm TalkHeal with EmotionSense AI</h3>
                <p style="font-size: 16px; line-height: 1.6; color: #555;">
                    I'm here to listen, understand your emotions, and provide personalized support. 
                    How are you feeling today?
                </p>
                <div style="margin-top: 15px; padding: 10px; background: #fff; border-radius: 8px; 
                            border: 2px dashed #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 14px;">
                        💡 <strong>Tip:</strong> I can detect emotions from your messages and adapt my responses accordingly
                    </p>
                </div>
                <div class="message-time" style="margin-top: 15px; color: #999; font-size: 12px;">
                    {get_current_time()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display chat messages with emotion analysis
        for i, msg in enumerate(active_convo["messages"]):
            css_class = "user-message" if msg["sender"] == "user" else "bot-message"
            
            # Add emotion analysis for user messages
            emotion_info = ""
            if msg["sender"] == "user" and "emotion_analysis" in msg:
                emotion_data = msg["emotion_analysis"]
                emotion_info = f"""
                <div style="background: #f0f8ff; border-radius: 6px; padding: 8px; margin: 5px 0; 
                            border-left: 3px solid #4a90e2; font-size: 12px;">
                    <strong>EmotionSense AI detected:</strong> {emotion_data['emotion'].title()} 
                    (Confidence: {emotion_data['confidence']:.0%})
                </div>
                """
            
            st.markdown(f"""
            <div class="{css_class}">
                {msg["message"]}
                {emotion_info}
                <div class="message-time">{msg["time"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show wellness recommendations after user messages with high negative emotions
            if msg["sender"] == "user" and "emotion_analysis" in msg:
                emotion_data = msg["emotion_analysis"]
                if emotion_data["crisis_level"] in ["high", "critical"]:
                    st.markdown("""
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; 
                                padding: 15px; margin: 10px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #856404;">⚠️ Support Available</h4>
                        <p style="margin: 0; color: #856404;">
                            I'm here to support you. If you need immediate help, please reach out to:
                        </p>
                        <ul style="margin: 10px 0; color: #856404;">
                            <li><strong>988</strong> - Suicide & Crisis Lifeline</li>
                            <li><strong>911</strong> - Emergency Services</li>
                            <li><strong>Text HOME to 741741</strong> - Crisis Text Line</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

def handle_enhanced_chat_input(model, system_prompt):
    """Enhanced chat input handler with emotion detection"""
    if "pre_filled_chat_input" not in st.session_state:
        st.session_state.pre_filled_chat_input = ""
    
    initial_value = st.session_state.pre_filled_chat_input
    st.session_state.pre_filled_chat_input = ""
    
    # Typing pattern tracking
    if "typing_tracker" not in st.session_state:
        st.session_state.typing_tracker = TypingPatternTracker()
    
    with st.form(key="enhanced_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Share your thoughts... (I'll analyze your emotions and respond accordingly)",
                key="enhanced_message_input",
                label_visibility="collapsed",
                placeholder="Type your message here... I'm listening with emotional intelligence...",
                value=initial_value,
                on_change=lambda: st.session_state.typing_tracker.start_typing()
            )
        with col2:
            send_pressed = st.form_submit_button("Send", use_container_width=True)
    
    if (send_pressed or st.session_state.get("send_chat_message", False)) and user_input.strip():
        if 'send_chat_message' in st.session_state:
            st.session_state.send_chat_message = False
        
        if st.session_state.active_conversation >= 0:
            current_time = get_current_time()
            active_convo = st.session_state.conversations[st.session_state.active_conversation]
            
            # Get typing patterns
            typing_patterns = st.session_state.typing_tracker.finish_typing(len(user_input))
            
            # Analyze emotions using EmotionSense AI
            emotional_state = emotion_ai.detect_emotion_from_text(user_input, typing_patterns)
            
            # Generate emotionally intelligent response
            ai_response = emotion_ai.generate_adaptive_response(emotional_state, user_input)
            
            # Save user message with emotion analysis
            user_message = {
                "sender": "user",
                "message": user_input.strip(),
                "time": current_time,
                "emotion_analysis": {
                    "emotion": emotional_state.primary_emotion.value,
                    "intensity": emotional_state.intensity,
                    "confidence": emotional_state.confidence,
                    "crisis_level": emotional_state.crisis_level.value,
                    "typing_patterns": typing_patterns
                }
            }
            
            active_convo["messages"].append(user_message)
            
            # Set title if it's the first message
            if len(active_convo["messages"]) == 1:
                title = user_input[:30] + "..." if len(user_input) > 30 else user_input
                active_convo["title"] = title
            
            # Save AI response
            ai_message = {
                "sender": "bot",
                "message": ai_response,
                "time": get_current_time(),
                "emotion_analysis": {
                    "responding_to_emotion": emotional_state.primary_emotion.value,
                    "crisis_level": emotional_state.crisis_level.value
                }
            }
            
            active_convo["messages"].append(ai_message)
            
            # Save conversations
            save_conversations(st.session_state.conversations)
            
            # Reset typing tracker
            st.session_state.typing_tracker = TypingPatternTracker()
            
            # Rerun to show new messages
            st.rerun()

def render_emotion_dashboard():
    """Render comprehensive emotion dashboard"""
    st.markdown("## 🧠 EmotionSense AI Dashboard")
    
    # Current emotional state
    if emotion_ai.emotion_history:
        current_emotion = emotion_ai.emotion_history[-1]
        st.markdown("### Current Emotional State")
        render_emotion_visualization(current_emotion)
        
        # Wellness recommendations
        render_wellness_recommendations(current_emotion)
    
    # Emotional trends
    st.markdown("### 📈 Emotional Trends")
    trends = emotion_ai.analyze_emotional_trends(days=7)
    
    if "error" not in trends:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Emotions", trends["total_emotions"])
        
        with col2:
            st.metric("Average Intensity", f"{trends['average_intensity']:.1%}")
        
        with col3:
            st.metric("Crisis Frequency", trends["crisis_frequency"])
        
        # Emotion distribution chart
        if trends["emotion_distribution"]:
            st.markdown("#### Emotion Distribution (Last 7 Days)")
            emotion_data = trends["emotion_distribution"]
            
            # Create a simple bar chart
            chart_data = ""
            for emotion, count in emotion_data.items():
                bar_width = min(count * 20, 200)  # Scale the bar width
                chart_data += f"""
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <span style="width: 80px; font-size: 12px;">{emotion.title()}</span>
                    <div style="background: #667eea; height: 20px; width: {bar_width}px; 
                                border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 10px; font-weight: bold;">{count}</span>
                    </div>
                </div>
                """
            
            st.markdown(f"""
            <div style="background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 10px 0;">
                {chart_data}
            </div>
            """, unsafe_allow_html=True)
        
        # Time patterns
        st.markdown("#### Time-Based Patterns")
        time_patterns = trends["time_patterns"]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌅 Morning", time_patterns["morning"])
        with col2:
            st.metric("☀️ Afternoon", time_patterns["afternoon"])
        with col3:
            st.metric("🌆 Evening", time_patterns["evening"])
        with col4:
            st.metric("🌙 Night", time_patterns["night"])
        
        # Overall trend
        trend_color = "#00CC00" if trends["trend"] == "improving" else "#FFCC00" if trends["trend"] == "stable" else "#FF6600"
        st.markdown(f"""
        <div style="background: {trend_color}20; border: 2px solid {trend_color}; 
                    border-radius: 8px; padding: 15px; margin: 15px 0; text-align: center;">
            <h4 style="margin: 0; color: {trend_color};">
                Overall Trend: {trends["trend"].title()}
            </h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent emotional insights
    render_emotional_insights()
    
    # Export data option
    if st.button("📊 Export Emotional Data", use_container_width=True):
        data = emotion_ai.export_emotional_data()
        st.download_button(
            label="Download JSON",
            data=json.dumps(data, indent=2),
            file_name=f"emotion_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
