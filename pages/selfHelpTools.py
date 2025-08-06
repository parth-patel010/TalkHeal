import streamlit as st
import webbrowser
from datetime import datetime
from core.utils import create_new_conversation, get_current_time
from core.theme import get_current_theme, toggle_theme, set_palette, PALETTES
from components.mood_dashboard import render_mood_dashboard, MoodTracker
from components.profile import initialize_profile_state, render_profile_section
from components.focus_session import render_focus_session
from streamlit_js_eval import streamlit_js_eval
import requests
import base64

def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Entire app background */
        html, body, [data-testid="stApp"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Main content transparency */
        .block-container {{
            background-color: rgba(255, 255, 255, 0);
        }}

        /* Sidebar: brighter translucent background */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.6);  /* Brighter and translucent */
            color: black;  /* Adjusted for light background */
        }}

        /* Header bar: fully transparent */
        [data-testid="stHeader"] {{
            background-color: rgba(0, 0, 0, 0);
        }}

        
        /* Hide left/right arrow at sidebar bottom */
        button[title="Close sidebar"],
        button[title="Open sidebar"] {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Set your background image
set_background("./lavender.png")


# --- Structured Emergency Resources ---
GLOBAL_RESOURCES = [
    {"name": "Befrienders Worldwide", "desc": "Emotional support to prevent suicide worldwide.",
        "url": "https://www.befrienders.org/"},
    {"name": "International Association for Suicide Prevention (IASP)", "desc": "Find a crisis center anywhere in the world.",
     "url": "https://www.iasp.info/resources/Crisis_Centres/"},
    {"name": "Crisis Text Line", "desc": "Text-based support available in the US, UK, Canada, and Ireland.",
     "url": "https://www.crisistextline.org/"},
    {"name": "The Trevor Project", "desc": "Crisis intervention and suicide prevention for LGBTQ young people.",
     "url": "https://www.thetrevorproject.org/"},
    {"name": "Child Helpline International", "desc": "A global network of child helplines for young people in need of help.",
     "url": "https://www.childhelplineinternational.org/"}
]


def get_country_from_coords(lat, lon):
    try:
        url = f"https://geocode.maps.co/reverse?lat={lat}&lon={lon}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("address", {}).get("country_code", "").upper()
    except:
        pass
    return None

def get_user_country():
    # 1. Try to get user's actual browser location (via JS)
    coords = streamlit_js_eval(
        js_expressions="""
            new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    position => resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    }),
                    error => resolve(null)
                );
            });
        """,
        key="get_coords"
    )

    if coords and "latitude" in coords and "longitude" in coords:
        country = get_country_from_coords(coords["latitude"], coords["longitude"])
        if country:
            return country

    # 2. Fallback to IP-based location using ipapi.co (no key required)
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=3)
        if resp.status_code == 200:
            return resp.json().get("country_code", "").upper()
    except:
        pass

    return None  # final fallback if everything fails

country_helplines = {
    "US": [
        "National Suicide Prevention Lifeline: 988",
        "Crisis Text Line: Text HOME to 741741",
        "SAMHSA National Helpline: 1-800-662-4357"
    ],
    "IN": [
        "AASRA: 9152987821",
        "Sneha Foundation: 044-24640050"
    ],
    "GB": [
        "Samaritans: 116 123"
    ],
    "AU": [
        "Lifeline: 13 11 14"
    ]
}
IASP_LINK = "https://findahelpline.com/"

mental_health_resources_full = {
    "Depression & Mood Disorders": {
        "description": "Information on understanding and coping with depression, persistent depressive disorder, and other mood-related challenges.",
        "links": [
            {"label": "NIMH - Depression",
                "url": "https://www.nimh.nih.gov/health/topics/depression"},
            {"label": "Mayo Clinic - Depression",
                "url": "https://www.mayoclinic.org/diseases-conditions/depression/symptoms-causes/syc-20356007"}
        ]
    },
    "Anxiety & Panic Disorders": {
        "description": "Guidance on managing generalized anxiety, social anxiety, panic attacks, and phobias.",
        "links": [
            {"label": "ADAA - Anxiety & Depression", "url": "https://adaa.org/"},
            {"label": "NIMH - Anxiety Disorders",
                "url": "https://www.nimh.nih.gov/health/topics/anxiety-disorders"}
        ]
    },
    "Bipolar Disorder": {
        "description": "Understanding the complexities of bipolar disorder, including mood swings and treatment options.",
        "links": [
            {"label": "NIMH - Bipolar Disorder",
                "url": "https://www.nimh.nih.gov/health/topics/bipolar-disorder"}
        ]
    },
    "PTSD & Trauma": {
        "description": "Resources for individuals experiencing post-traumatic stress disorder and other trauma-related conditions.",
        "links": [
            {"label": "PTSD: National Center", "url": "https://www.ptsd.va.gov/"}
        ]
    },
    "OCD & Related Disorders": {
        "description": "Support and information for obsessive-compulsive disorder, body dysmorphic disorder, and hoarding disorder.",
        "links": [
            {"label": "IOCDF - OCD", "url": "https://iocdf.org/"}
        ]
    },
    "Coping Skills & Self-Care": {
        "description": "Practical strategies and techniques for stress management, emotional regulation, and daily well-being.",
        "links": [
            {"label": "HelpGuide - Stress Management",
                "url": "https://www.helpguide.org/articles/stress/stress-management.htm"}
        ]
    },
    "Therapy & Treatment Options": {
        "description": "Overview of various therapeutic approaches, including CBT, DBT, and finding a therapist.",
        "links": [
            {"label": "APA - Finding a Therapist",
                "url": "https://www.apa.org/helpcenter/choose-therapist"}
        ]
    }
}
st.title("🧰 Self Help Tools")

# Button states
if "active_tool" not in st.session_state:
    st.session_state.active_tool = ""

col1, col2 = st.columns(3)[0:2]
with col1:
    if st.button("🧘 Focus Session", use_container_width=True):
        st.session_state.active_tool = "focus"
with col2:
    if st.button("📊 Mood Dashboard", use_container_width=True):
        st.session_state.active_tool = "mood_dashboard"

col3, col4 = st.columns(3)[0:2]
with col3:
    if st.button("🧠 Mental Health Check", use_container_width=True):
        st.session_state.active_tool = "mental_check"
with col4:
    if st.button("📚 Knowledge Base", use_container_width=True):
        st.session_state.active_tool = "knowledge"

col5, col6 = st.columns(3)[0:2]
with col5:
    if st.button("☎️ Crisis Support", use_container_width=True):
        st.session_state.active_tool = "crisis"
with col6:
    if st.button("🧪 PsyToolkit Quizzes", use_container_width=True):
        st.session_state.active_tool = "quizzes"

st.markdown("---")

# --- RENDER SELECTED TOOL ---
if st.session_state.active_tool == "focus":
    st.header("🧘 Focus Session")
    render_focus_session()
    # st.session_state.show_focus_session = True
    

elif st.session_state.active_tool == "mood_dashboard":
    render_mood_dashboard()

elif st.session_state.active_tool == "mental_check":
    st.header("🧠 Mental Health Check")
    mood_options_map = {
        "😔 Very Low": "very_low",
        "😐 Low": "low",
        "😊 Okay": "okay",
        "😄 Good": "good",
        "🌟 Great": "great"
    }
    mood_labels = list(mood_options_map.keys())
    selected_mood_label = st.radio("Mood Scale", options=mood_labels, index=mood_labels.index("😊 Okay"), horizontal=True)
    st.session_state.current_mood_val = mood_options_map[selected_mood_label]

    journal_prompt_text = {
        "very_low": "What's weighing on your mind today?",
        "low": "What are your thoughts right now?",
        "okay": "Anything specific on your mind today?",
        "good": "What made you feel good today?",
        "great": "What's making you shine today?"
    }.get(st.session_state.current_mood_val, "Reflect on your mood:")

    if "mood_journal_entry" not in st.session_state:
        st.session_state.mood_journal_entry = ""
    if "mood_tip_display" not in st.session_state:
        st.session_state.mood_tip_display = ""
    if "mood_entry_status" not in st.session_state:
        st.session_state.mood_entry_status = ""

    st.text_area(f"✏️ {journal_prompt_text}", key="mood_journal_area", value=st.session_state.mood_journal_entry, height=70)

    st.markdown("**Why are you feeling this way?**")
    context_reasons = ["No specific reason", "Work", "Family", "Health", "Relationships", "Financial", "Social", "Personal goals", "Weather", "Other"]
    selected_reason = st.selectbox("Select a reason (optional):", options=context_reasons)

    st.markdown("**What did you do today?** (optional)")
    activities = []
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("✅ Exercise"):
            activities.append("Exercise")
        if st.checkbox("✅ Socialized"):
            activities.append("Socialized")
    with col2:
        if st.checkbox("✅ Ate healthy"):
            activities.append("Ate healthy")
        if st.checkbox("✅ Slept well"):
            activities.append("Slept well")

    tips_for_mood = {
        "very_low": "Remember, it's okay not to be okay. Consider connecting with a professional.",
        "low": "Even small steps help. Try a brief mindful moment or gentle activity.",
        "okay": "Keep nurturing your well-being. What's one thing you can do to maintain this?",
        "good": "That's wonderful! Savor this feeling and perhaps share your positivity.",
        "great": "Fantastic! How can you carry this energy forward into your day?"
    }.get(st.session_state.current_mood_val, "A general tip for your mood.")

    col_tip, col_talk = st.columns(2)
    with col_tip:
        if st.button("Get Tip & Save Entry"):
            if "mood_tracker" not in st.session_state:
                st.session_state.mood_tracker = MoodTracker()
            st.session_state.mood_tracker.add_mood_entry(
                st.session_state.current_mood_val,
                st.session_state.get("mood_journal_area", ""),
                selected_reason,
                activities
            )
            st.session_state.mood_tip_display = tips_for_mood
            st.session_state.mood_entry_status = f"Mood entry for '{selected_mood_label}' saved."
            st.session_state.mood_journal_entry = ""

    with col_talk:
        if st.button("Ask TalkHeal"):
            if st.session_state.mood_journal_area.strip():
                st.session_state.pre_filled_chat_input = st.session_state.mood_journal_area
                st.session_state.send_chat_message = True
                st.session_state.mood_journal_entry = ""
                st.session_state.mood_tip_display = ""
                st.session_state.mood_entry_status = ""
                st.rerun()
            else:
                st.warning("Please enter your thoughts before asking TalkHeal.")

    if st.session_state.mood_tip_display:
        st.success(st.session_state.mood_tip_display)
    if st.session_state.mood_entry_status:
        st.info(st.session_state.mood_entry_status)

elif st.session_state.active_tool == "knowledge":
    st.header("📚 Resources & Knowledge Base")
    query = st.text_input("Search resources...", placeholder="e.g., anxiety tips, therapy")
    if query:
        filtered = [k for k in mental_health_resources_full if query.lower() in k.lower()]
        if not filtered:
            st.info("No matching resources found.")
        for topic in filtered:
            st.markdown(f"**{topic}**")
            st.info(mental_health_resources_full[topic]['description'])
            for link in mental_health_resources_full[topic]['links']:
                st.markdown(f"• [{link['label']}]({link['url']})")
            st.markdown("---")
    else:
        tabs = st.tabs(list(mental_health_resources_full.keys()))
        for i, topic in enumerate(mental_health_resources_full):
            with tabs[i]:
                st.markdown(f"**{topic}**")
                st.info(mental_health_resources_full[topic]['description'])
                for link in mental_health_resources_full[topic]['links']:
                    st.markdown(f"• [{link['label']}]({link['url']})")

elif st.session_state.active_tool == "crisis":
    st.header("☎️ Crisis Support")
    for r in GLOBAL_RESOURCES:
        st.markdown(f"**{r['name']}**: {r['desc']} [Visit Website]({r['url']})")
    user_country = get_user_country()
    st.markdown("### 🚨 Emergency Help")
    if user_country and user_country in country_helplines:
        st.markdown(f"**Helplines for {user_country}:**")
        for line in country_helplines[user_country]:
            st.markdown(f"• {line}")
    else:
        st.markdown(f"[Find help worldwide via IASP]({IASP_LINK})")

elif st.session_state.active_tool == "quizzes":
    st.header("🧪 Take PsyToolkit Verified Quizzes")
    quizzes = [
        {
            "name": "GAD-7 (Anxiety Assessment)",
            "desc": "Measures severity of generalized anxiety symptoms.",
            "url": "https://www.psytoolkit.org/cgi-bin/3.6.0/survey?s=u8bAf",
            "score": "0–4: Minimal, 5–9: Mild, 10–14: Moderate, 15–21: Severe"
        },
        {
            "name": "PHQ-9 (Depression Assessment)",
            "desc": "Screens for presence and severity of depression.",
            "url": "https://www.psytoolkit.org/cgi-bin/3.6.0/survey?s=Hj32b",
            "score": "0–4: Mild, 5–9: Moderate, 10–14: Moderately Severe, 15–19: Severe"
        },
        {
            "name": "WHO-5 Well-Being Index",
            "desc": "Five simple questions to assess well-being. 0 (poor) to 100 (excellent).",
            "url": "https://www.psytoolkit.org/cgi-bin/3.6.0/survey?s=POqLJ",
            "score": "Score <= 50 may indicate need for further assessment."
        },
        {
            "name": "DASS (Depression, Anxiety, Stress Scale)",
            "desc": "Measures all three using one combined form.",
            "url": "https://www.psytoolkit.org/cgi-bin/3.6.0/survey?s=HvfDY",
            "score": "Normal to Extremely Severe per subscale"
        }
    ]
    for q in quizzes:
        st.markdown(f"**{q['name']}**\n\n*{q['desc']}*\n\n[Take Quiz]({q['url']})\n\nScore Info: {q['score']}")
        st.markdown("---")
