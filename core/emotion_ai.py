import streamlit as st
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import numpy as np
from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    ANXIETY = "anxiety"
    CALM = "calm"
    EXCITEMENT = "excitement"
    CONFUSION = "confusion"
    HOPELESSNESS = "hopelessness"
    GRATITUDE = "gratitude"

class CrisisLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EmotionalState:
    primary_emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    context: Dict[str, Any]
    crisis_level: CrisisLevel = CrisisLevel.NONE

@dataclass
class UserProfile:
    communication_style: str
    cultural_background: str
    emotional_triggers: List[str]
    preferred_responses: Dict[str, str]
    crisis_contacts: List[str]
    last_crisis_check: datetime

class EmotionSenseAI:
    def __init__(self):
        self.emotion_history: List[EmotionalState] = []
        self.user_profile: Optional[UserProfile] = None
        self.crisis_patterns: Dict[str, int] = {}
        self.response_templates: Dict[str, Dict[str, str]] = self._load_response_templates()
        
    def _load_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Load emotion-specific response templates"""
        return {
            EmotionType.JOY.value: {
                "low": "I'm so glad you're feeling good! What's bringing you this joy?",
                "medium": "Your positive energy is wonderful! How can we build on this feeling?",
                "high": "This is amazing! Your joy is contagious. What's making you feel so wonderful?"
            },
            EmotionType.SADNESS.value: {
                "low": "I sense you're feeling a bit down. Would you like to talk about what's on your mind?",
                "medium": "I can feel the weight of your sadness. You don't have to carry this alone. What's happening?",
                "high": "I'm here with you in this difficult moment. Your feelings are valid and important. Can you tell me more?"
            },
            EmotionType.ANXIETY.value: {
                "low": "I notice you might be feeling a bit anxious. Let's take a moment to breathe together.",
                "medium": "Your anxiety is real and I'm here to help you through it. What's making you feel this way?",
                "high": "I can see you're experiencing intense anxiety. Let's focus on getting you grounded. Can you tell me what you're feeling?"
            },
            EmotionType.FEAR.value: {
                "low": "It's okay to feel afraid. What's making you feel this way?",
                "medium": "Fear can be overwhelming. I'm here to help you work through it. What's happening?",
                "high": "I can sense your fear is intense right now. You're safe here. Let's work through this together."
            },
            EmotionType.ANGER.value: {
                "low": "I can see you're feeling frustrated. What's been bothering you?",
                "medium": "Your anger is understandable. It's okay to feel this way. What's been happening?",
                "high": "I can feel the intensity of your anger. You have every right to feel this way. What triggered this?"
            },
            EmotionType.HOPELESSNESS.value: {
                "low": "I hear you're feeling discouraged. Let's explore what's making you feel this way.",
                "medium": "I can feel the weight of your hopelessness. You're not alone in this. What's happening?",
                "high": "I'm very concerned about how you're feeling. Your life has value and meaning. Can we talk about getting you some immediate support?"
            },
            EmotionType.CALM.value: {
                "low": "It's wonderful that you're feeling peaceful. How are you maintaining this sense of calm?",
                "medium": "Your calm energy is really grounding. What's helping you stay centered?",
                "high": "This sense of peace you're experiencing is beautiful. How can we nurture this feeling?"
            },
            EmotionType.EXCITEMENT.value: {
                "low": "I can sense your enthusiasm! What's got you feeling excited?",
                "medium": "Your excitement is contagious! Tell me more about what's bringing you this energy!",
                "high": "Wow, you're absolutely buzzing with excitement! I'd love to hear all about it!"
            },
            EmotionType.GRATITUDE.value: {
                "low": "It's beautiful that you're feeling grateful. What are you thankful for today?",
                "medium": "Your gratitude is inspiring! What's bringing you this sense of appreciation?",
                "high": "Your gratitude is radiating! It's wonderful to see you recognizing the good in your life!"
            }
        }
    
    def detect_emotion_from_text(self, text: str, typing_patterns: Dict[str, Any] = None) -> EmotionalState:
        """Analyze text for emotional content using advanced NLP techniques"""
        text_lower = text.lower()
        
        # Check for medical emergencies first
        medical_emergency = self._detect_medical_emergency(text)
        
        # Emotion keyword analysis with intensity scoring
        emotion_scores = {
            EmotionType.JOY: 0.0,
            EmotionType.SADNESS: 0.0,
            EmotionType.ANXIETY: 0.0,
            EmotionType.FEAR: 0.0,
            EmotionType.ANGER: 0.0,
            EmotionType.HOPELESSNESS: 0.0,
            EmotionType.GRATITUDE: 0.0,
            EmotionType.CALM: 0.0
        }
        
        # Joy indicators
        joy_words = ["happy", "excited", "great", "wonderful", "amazing", "blessed", "grateful", "joy", "smile", "laugh", "like", "love", "enjoy", "fun", "good", "awesome", "fantastic"]
        for word in joy_words:
            if word in text_lower:
                emotion_scores[EmotionType.JOY] += 0.3
        
        # Sadness indicators
        sadness_words = ["sad", "depressed", "down", "blue", "miserable", "hopeless", "lonely", "empty", "worthless", "unhappy", "upset", "disappointed", "hurt", "pain", "suffering", "loss", "grief", "tears", "crying"]
        for word in sadness_words:
            if word in text_lower:
                emotion_scores[EmotionType.SADNESS] += 0.4
        
        # Anxiety indicators
        anxiety_words = ["anxious", "worried", "nervous", "stressed", "overwhelmed", "panic", "fear", "scared", "terrified", "concerned", "uneasy", "restless", "tense", "jittery", "on edge"]
        for word in anxiety_words:
            if word in text_lower:
                emotion_scores[EmotionType.ANXIETY] += 0.4
        
        # Fear indicators (including accident-related and injury-related)
        fear_words = ["afraid", "frightened", "terrified", "scared", "horrified", "alarmed", "startled", "shocked", "accident", "crash", "injury", "injured", "injuring", "hurt", "hurting", "pain", "painful", "emergency", "danger", "threat", "attack", "violence", "death", "dying"]
        for word in fear_words:
            if word in text_lower:
                emotion_scores[EmotionType.FEAR] += 0.5
        
        # Anger indicators
        anger_words = ["angry", "mad", "furious", "rage", "irritated", "annoyed", "frustrated", "outraged", "hate", "disgusted", "bitter", "resentful", "hostile", "aggressive"]
        for word in anger_words:
            if word in text_lower:
                emotion_scores[EmotionType.ANGER] += 0.4
        
        # Hopelessness indicators
        hopelessness_words = ["hopeless", "desperate", "helpless", "powerless", "defeated", "broken", "destroyed", "ruined", "finished", "end", "give up", "can't", "impossible", "never", "always", "nothing", "everything"]
        for word in hopelessness_words:
            if word in text_lower:
                emotion_scores[EmotionType.HOPELESSNESS] += 0.5
        
        # Crisis indicators
        crisis_words = ["kill myself", "want to die", "end it all", "no point", "give up", "can't take it", "suicide", "self harm", "cut myself", "overdose", "end my life", "better off dead"]
        crisis_detected = any(phrase in text_lower for phrase in crisis_words)
        
        # Typing pattern analysis
        if typing_patterns:
            if typing_patterns.get("typing_speed", 0) < 10:  # Very slow typing
                emotion_scores[EmotionType.SADNESS] += 0.2
            if typing_patterns.get("typing_speed", 0) > 50:  # Very fast typing
                emotion_scores[EmotionType.ANXIETY] += 0.2
            if typing_patterns.get("backspace_count", 0) > 5:  # Many corrections
                emotion_scores[EmotionType.ANXIETY] += 0.1
        
        # Punctuation and formatting analysis
        if "!!!" in text:
            emotion_scores[EmotionType.ANXIETY] += 0.2
        if "..." in text:
            emotion_scores[EmotionType.SADNESS] += 0.1
        if text.count("?") > 2:
            emotion_scores[EmotionType.CONFUSION] += 0.2
        
        # Context-based scoring adjustments
        # If text contains accident-related words, boost fear and sadness
        accident_indicators = ["accident", "crash", "injury", "injured", "injuring", "hurt", "hurting", "pain", "painful", "emergency", "hospital", "doctor", "ambulance"]
        if any(word in text_lower for word in accident_indicators):
            emotion_scores[EmotionType.FEAR] += 0.3
            emotion_scores[EmotionType.SADNESS] += 0.2
            emotion_scores[EmotionType.ANXIETY] += 0.2
        
        # If text contains negative words, reduce joy score
        negative_words = ["not", "no", "never", "can't", "won't", "don't", "bad", "terrible", "awful", "horrible", "disaster"]
        if any(word in text_lower for word in negative_words):
            emotion_scores[EmotionType.JOY] = max(0.0, emotion_scores[EmotionType.JOY] - 0.2)
        
        # Past tense and time indicators that suggest negative experiences
        past_tense_indicators = ["got", "had", "was", "were", "been", "did", "went", "came", "fell", "broke", "hurt", "injured", "accident", "crash"]
        time_indicators = ["yesterday", "last week", "last month", "last year", "earlier", "before", "recently"]
        
        # If text contains past tense + negative experience indicators, boost negative emotions
        has_past_tense = any(word in text_lower for word in past_tense_indicators)
        has_time_indicator = any(word in text_lower for word in time_indicators)
        has_negative_experience = any(word in text_lower for word in accident_indicators + ["bad", "terrible", "awful", "horrible", "disaster", "problem", "issue", "trouble"])
        
        if has_past_tense and has_negative_experience:
            emotion_scores[EmotionType.FEAR] += 0.2
            emotion_scores[EmotionType.SADNESS] += 0.2
            emotion_scores[EmotionType.ANXIETY] += 0.1
            # Reduce joy significantly for past negative experiences
            emotion_scores[EmotionType.JOY] = max(0.0, emotion_scores[EmotionType.JOY] - 0.4)
        
        if has_time_indicator and has_negative_experience:
            emotion_scores[EmotionType.SADNESS] += 0.2
            emotion_scores[EmotionType.FEAR] += 0.1
            # Reduce joy for time-based negative experiences
            emotion_scores[EmotionType.JOY] = max(0.0, emotion_scores[EmotionType.JOY] - 0.3)
        
        # Determine primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = min(emotion_scores[primary_emotion], 1.0)
        
        # Crisis level assessment
        crisis_level = self._assess_crisis_level(text, emotion_scores, crisis_detected)
        
        # Context analysis
        context = {
            "word_count": len(text.split()),
            "has_questions": "?" in text,
            "has_exclamations": "!" in text,
            "time_of_day": datetime.now().hour,
            "crisis_detected": crisis_detected,
            "medical_emergency": medical_emergency
        }
        
        emotional_state = EmotionalState(
            primary_emotion=primary_emotion,
            intensity=intensity,
            confidence=min(intensity * 0.8 + 0.2, 1.0),
            timestamp=datetime.now(),
            context=context,
            crisis_level=crisis_level
        )
        
        # Store in history
        self.emotion_history.append(emotional_state)
        
        # Update crisis patterns
        if crisis_level != CrisisLevel.NONE:
            self._update_crisis_patterns(emotional_state)
        
        return emotional_state
    
    def _assess_crisis_level(self, text: str, emotion_scores: Dict[EmotionType, float], crisis_detected: bool) -> CrisisLevel:
        """Assess the level of crisis based on text content and emotion scores"""
        if crisis_detected:
            return CrisisLevel.CRITICAL
        
        # High hopelessness or sadness
        if emotion_scores[EmotionType.HOPELESSNESS] > 0.7 or emotion_scores[EmotionType.SADNESS] > 0.8:
            return CrisisLevel.HIGH
        
        # High anxiety or fear
        if emotion_scores[EmotionType.ANXIETY] > 0.8 or emotion_scores[EmotionType.FEAR] > 0.8:
            return CrisisLevel.MEDIUM
        
        # Moderate negative emotions
        if (emotion_scores[EmotionType.SADNESS] > 0.5 or 
            emotion_scores[EmotionType.ANXIETY] > 0.5 or 
            emotion_scores[EmotionType.FEAR] > 0.5):
            return CrisisLevel.LOW
        
        return CrisisLevel.NONE
    
    def _update_crisis_patterns(self, emotional_state: EmotionalState):
        """Track crisis patterns over time"""
        current_time = datetime.now()
        time_key = current_time.strftime("%Y-%m-%d")
        
        if time_key not in self.crisis_patterns:
            self.crisis_patterns[time_key] = 0
        
        if emotional_state.crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]:
            self.crisis_patterns[time_key] += 1
    
    def generate_adaptive_response(self, emotional_state: EmotionalState, user_input: str) -> str:
        """Generate emotionally intelligent responses based on detected state"""
        emotion = emotional_state.primary_emotion.value
        intensity = emotional_state.intensity
        
        # Check for medical emergency first
        if emotional_state.context.get("medical_emergency"):
            return self._generate_medical_emergency_response()
        
        # Determine intensity level for response selection
        if intensity < 0.3:
            intensity_level = "low"
        elif intensity < 0.7:
            intensity_level = "medium"
        else:
            intensity_level = "high"
        
        # Get base response template
        base_response = self.response_templates.get(emotion, {}).get(intensity_level, 
            "I'm here to listen and support you. Can you tell me more about what you're experiencing?")
        
        # Crisis intervention
        if emotional_state.crisis_level == CrisisLevel.CRITICAL:
            return self._generate_crisis_response()
        elif emotional_state.crisis_level == CrisisLevel.HIGH:
            return self._generate_high_crisis_response()
        
        # Special handling for accident-related situations
        user_input_lower = user_input.lower()
        accident_indicators = ["accident", "crash", "injury", "hurt", "pain", "emergency", "hospital", "doctor", "ambulance"]
        if any(word in user_input_lower for word in accident_indicators):
            if emotion in [EmotionType.FEAR.value, EmotionType.SADNESS.value, EmotionType.ANXIETY.value]:
                base_response = f"I'm so sorry to hear about your accident. This must be really frightening and overwhelming. {base_response}"
            elif emotion == EmotionType.JOY.value:
                # If joy is detected in accident context, provide more appropriate response
                base_response = "I want to make sure you're okay. Even if you're trying to stay positive, it's completely normal to feel scared, sad, or anxious after an accident. How are you really feeling right now?"
        
        # Emotional validation and support
        validation_phrases = {
            EmotionType.SADNESS: "It's completely normal to feel this way, and your feelings are valid.",
            EmotionType.ANXIETY: "Anxiety can be really challenging, and it's okay to feel overwhelmed.",
            EmotionType.FEAR: "Fear is a natural response, and it's okay to feel afraid.",
            EmotionType.ANGER: "Your anger is understandable, and it's okay to feel this way.",
            EmotionType.HOPELESSNESS: "I hear you, and your feelings matter. You're not alone in this."
        }
        
        validation = validation_phrases.get(emotional_state.primary_emotion, "")
        
        # Personalization based on user profile
        if self.user_profile:
            if self.user_profile.communication_style == "direct":
                base_response = base_response.replace("Would you like to talk about", "Tell me about")
            elif self.user_profile.communication_style == "gentle":
                base_response = base_response + " Take your time, I'm here to listen."
        
        # Combine elements
        response = f"{validation} {base_response}"
        
        # Add follow-up questions based on emotion
        follow_ups = {
            EmotionType.SADNESS: "What do you think might help you feel a bit better right now?",
            EmotionType.ANXIETY: "Can you identify what's making you feel most anxious?",
            EmotionType.FEAR: "What would make you feel safer in this moment?",
            EmotionType.ANGER: "What do you think triggered this feeling?",
            EmotionType.HOPELESSNESS: "What would help you feel a little more hopeful right now?"
        }
        
        follow_up = follow_ups.get(emotional_state.primary_emotion, "")
        if follow_up:
            response += f"\n\n{follow_up}"
        
        return response.strip()
    
    def _generate_crisis_response(self) -> str:
        """Generate immediate crisis intervention response"""
        return """🚨 I'm very concerned about what you're sharing and I want to make sure you're safe.

**Immediate Support Available:**
• **Crisis Helpline**: 988 (Suicide & Crisis Lifeline)
• **Emergency**: 911
• **Crisis Text Line**: Text HOME to 741741

**You are not alone.** Your life has value and meaning, and there are people who want to help you.

Would you like me to help you connect with professional support, or would you prefer to talk with someone you trust right now?

**Remember**: This feeling won't last forever, and help is available 24/7."""
    
    def _generate_high_crisis_response(self) -> str:
        """Generate response for high crisis level"""
        return """⚠️ I can sense you're going through something really difficult right now.

**Your feelings are valid** and it's okay to not be okay. You don't have to face this alone.

**Support Options:**
• Talk to a trusted friend or family member
• Contact a mental health professional
• Call 988 for crisis support
• Text HOME to 741741 for crisis text support

Would you like to talk about what's happening, or would you prefer help finding professional support?

**You matter, and there are people who care about you.**"""
    
    def analyze_emotional_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze emotional patterns over time"""
        if not self.emotion_history:
            return {"error": "No emotional data available"}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_emotions = [e for e in self.emotion_history if e.timestamp > cutoff_date]
        
        if not recent_emotions:
            return {"error": f"No emotional data in the last {days} days"}
        
        # Emotion frequency
        emotion_counts = {}
        for emotion in recent_emotions:
            emotion_name = emotion.primary_emotion.value
            emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
        
        # Average intensity
        avg_intensity = sum(e.intensity for e in recent_emotions) / len(recent_emotions)
        
        # Crisis frequency
        crisis_count = sum(1 for e in recent_emotions if e.crisis_level != CrisisLevel.NONE)
        
        # Time-based patterns
        morning_emotions = [e for e in recent_emotions if 6 <= e.timestamp.hour < 12]
        afternoon_emotions = [e for e in recent_emotions if 12 <= e.timestamp.hour < 18]
        evening_emotions = [e for e in recent_emotions if 18 <= e.timestamp.hour < 24]
        night_emotions = [e for e in recent_emotions if 0 <= e.timestamp.hour < 6]
        
        return {
            "total_emotions": len(recent_emotions),
            "emotion_distribution": emotion_counts,
            "average_intensity": round(avg_intensity, 2),
            "crisis_frequency": crisis_count,
            "time_patterns": {
                "morning": len(morning_emotions),
                "afternoon": len(afternoon_emotions),
                "evening": len(evening_emotions),
                "night": len(night_emotions)
            },
            "primary_emotion": max(emotion_counts, key=emotion_counts.get) if emotion_counts else "unknown",
            "trend": "improving" if avg_intensity < 0.5 else "stable" if avg_intensity < 0.7 else "concerning"
        }
    
    def get_wellness_recommendations(self, emotional_state: EmotionalState) -> List[str]:
        """Generate personalized wellness recommendations based on emotional state"""
        recommendations = []
        
        if emotional_state.primary_emotion == EmotionType.ANXIETY:
            if emotional_state.intensity > 0.7:
                recommendations.extend([
                    "🫁 Try the 4-7-8 breathing technique: Inhale for 4, hold for 7, exhale for 8",
                    "🧘‍♀️ Progressive muscle relaxation: Tense and release each muscle group",
                    "🌊 Grounding exercise: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste"
                ])
            else:
                recommendations.extend([
                    "📝 Write down your worries to get them out of your head",
                    "🚶‍♀️ Take a short walk to change your environment",
                    "☕ Practice mindful breathing with a warm drink"
                ])
        
        elif emotional_state.primary_emotion == EmotionType.SADNESS:
            if emotional_state.intensity > 0.7:
                recommendations.extend([
                    "🫂 Reach out to someone you trust - you don't have to be alone",
                    "🎵 Listen to music that matches your mood, then gradually shift to uplifting songs",
                    "🌅 Get some natural light - even 10 minutes can help"
                ])
            else:
                recommendations.extend([
                    "📚 Read something that brings you comfort",
                    "🎨 Express your feelings through art, writing, or music",
                    "🐕 Spend time with a pet or loved one"
                ])
        
        elif emotional_state.primary_emotion == EmotionType.ANGER:
            recommendations.extend([
                "💨 Take 10 deep breaths before responding",
                "🏃‍♀️ Physical activity can help release built-up energy",
                "📝 Write a letter (don't send it) to express your feelings"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "💧 Stay hydrated - dehydration can affect mood",
            "😴 Ensure you're getting enough sleep",
            "🍎 Eat regular, balanced meals"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def update_user_profile(self, profile_data: Dict[str, Any]):
        """Update or create user profile for personalization"""
        if not self.user_profile:
            self.user_profile = UserProfile(
                communication_style="compassionate",
                cultural_background="general",
                emotional_triggers=[],
                preferred_responses={},
                crisis_contacts=[],
                last_crisis_check=datetime.now()
            )
        
        # Update profile fields
        for key, value in profile_data.items():
            if hasattr(self.user_profile, key):
                setattr(self.user_profile, key, value)
    
    def export_emotional_data(self) -> Dict[str, Any]:
        """Export emotional data for analysis or backup"""
        return {
            "emotion_history": [
                {
                    "emotion": e.primary_emotion.value,
                    "intensity": e.intensity,
                    "confidence": e.confidence,
                    "timestamp": e.timestamp.isoformat(),
                    "crisis_level": e.crisis_level.value,
                    "context": e.context
                }
                for e in self.emotion_history
            ],
            "crisis_patterns": self.crisis_patterns,
            "user_profile": {
                "communication_style": self.user_profile.communication_style if self.user_profile else "default",
                "cultural_background": self.user_profile.cultural_background if self.user_profile else "default"
            } if self.user_profile else None,
            "export_timestamp": datetime.now().isoformat()
        }

    def _detect_medical_emergency(self, text: str) -> bool:
        """Detect if the text indicates a medical emergency that requires immediate attention"""
        text_lower = text.lower()
        
        emergency_indicators = [
            "chest pain", "heart attack", "stroke", "unconscious", "not breathing",
            "severe bleeding", "broken bone", "head injury", "concussion",
            "allergic reaction", "anaphylaxis", "seizure", "overdose",
            "suicide attempt", "self harm", "cut myself", "bleeding"
        ]
        
        return any(phrase in text_lower for phrase in emergency_indicators)
    
    def _generate_medical_emergency_response(self) -> str:
        """Generate response for medical emergencies"""
        return """🚨 MEDICAL EMERGENCY DETECTED

**IMMEDIATE ACTION REQUIRED:**
• **Call 911 or your local emergency number immediately**
• **Do not wait** - this requires professional medical attention

**While waiting for help:**
• Stay calm and follow emergency dispatcher instructions
• Keep the person comfortable and safe
• Do not give food, drink, or medication unless instructed

**Your safety is the top priority.** Please get medical help right away.

I'm here to support you, but this situation requires immediate professional medical attention."""

# Global instance
emotion_ai = EmotionSenseAI()
