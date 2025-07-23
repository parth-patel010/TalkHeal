import streamlit as st
import webbrowser
from datetime import datetime
from core.utils import create_new_conversation, get_current_time
import requests

# Get the user's country based on their IP address
# This is used to provide localized resources and emergency contacts.
def get_user_country():
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("country", None)
    except Exception:
        pass
    return None

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
            {"label": "NIMH - Depression", "url": "https://www.nimh.nih.gov/health/topics/depression"},
            {"label": "Mayo Clinic - Depression", "url": "https://www.mayoclinic.org/diseases-conditions/depression/symptoms-causes/syc-20356007"}
        ]
    },
    "Anxiety & Panic Disorders": {
        "description": "Guidance on managing generalized anxiety, social anxiety, panic attacks, and phobias.",
        "links": [
            {"label": "ADAA - Anxiety & Depression", "url": "https://adaa.org/"},
            {"label": "NIMH - Anxiety Disorders", "url": "https://www.nimh.nih.gov/health/topics/anxiety-disorders"}
        ]
    },
    "Bipolar Disorder": {
        "description": "Understanding the complexities of bipolar disorder, including mood swings and treatment options.",
        "links": [
            {"label": "NIMH - Bipolar Disorder", "url": "https://www.nimh.nih.gov/health/topics/bipolar-disorder"}
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
            {"label": "HelpGuide - Stress Management", "url": "https://www.helpguide.org/articles/stress/stress-management.htm"}
        ]
    },
    "Therapy & Treatment Options": {
        "description": "Overview of various therapeutic approaches, including CBT, DBT, and finding a therapist.",
        "links": [
            {"label": "APA - Finding a Therapist", "url": "https://www.apa.org/helpcenter/choose-therapist"}
        ]
    }
}


def render_sidebar():
    """Renders the left and right sidebars."""
    with st.sidebar:
        st.markdown("### 💬 Conversations")
        if "show_quick_start_prompts" not in st.session_state:
            st.session_state.show_quick_start_prompts = False
        if "pre_filled_chat_input" not in st.session_state:
            st.session_state.pre_filled_chat_input = ""
        if "send_chat_message" not in st.session_state:
            st.session_state.send_chat_message = False

        if st.button("➕ New Chat", key="new_chat", use_container_width=True):
            create_new_conversation()
            st.session_state.show_quick_start_prompts = True
            st.rerun()
        if st.session_state.show_quick_start_prompts:
            st.markdown("---")
            st.markdown("**Start with a common topic:**")
            quick_prompts = [
                "Feeling overwhelmed",
                "Need to vent about my day",
                "How to manage stress?",
                "Tell me about anxiety"
            ]
            qp_cols = st.columns(2)
            for i, prompt in enumerate(quick_prompts):
                with qp_cols[i % 2]:
                    if st.button(f"✨ {prompt}", key=f"qp_{i}", use_container_width=True):
                        st.session_state.pre_filled_chat_input = prompt
                        st.session_state.send_chat_message = True
                        st.session_state.show_quick_start_prompts = False 
                        st.rerun()

            st.markdown("---")

        if st.session_state.conversations:
            if "delete_candidate" not in st.session_state:
                for i, convo in enumerate(st.session_state.conversations):
                    is_active = i == st.session_state.active_conversation
                    button_style_icon = "🟢" if is_active else "📝"

                    col1, col2 = st.columns([5, 1])
                    with col1:
                        if st.button(
                            f"{button_style_icon} {convo['title'][:22]}...",
                            key=f"convo_{i}",
                            help=f"Started: {convo['date']}",
                            use_container_width=True
                        ):
                            st.session_state.active_conversation = i
                            st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"delete_{i}"):
                            st.session_state.delete_candidate = i
                            st.rerun()

            else:
                st.warning("⚠️ Are you sure you want to delete this conversation?")
                col_confirm, col_cancel = st.columns(2)

                if col_confirm.button("Yes, delete", key="confirm_delete"):
                    del st.session_state.conversations[st.session_state.delete_candidate]
                    del st.session_state.delete_candidate
                    st.session_state.active_conversation = -1
                    st.rerun()

                if "cancel_clicked" not in st.session_state:
                    st.session_state.cancel_clicked = False

                if col_cancel.button("Cancel", key="cancel_delete"):
                    if not st.session_state.cancel_clicked:
                        st.session_state.cancel_clicked = True
                        del st.session_state.delete_candidate
                        st.rerun()
                else:
                    st.session_state.cancel_clicked = False

        else:
            st.info("No conversations yet. Start a new chat!")

        st.markdown("---")
        
        st.markdown(
            """
            <a href="#" target="_blank" class="emergency_button">
                🚨 Emergency Help
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown("")

        # --- 3. Dynamic Mood Tracker & Micro-Journal (Fixed Tip & New Button) ---
        with st.expander("🧠 Mental Health Check"):
            st.markdown("**How are you feeling today?**")

            mood_options_map = {
                "😔 Very Low": "very_low",
                "😐 Low": "low",
                "😊 Okay": "okay",
                "😄 Good": "good",
                "🌟 Great": "great"
            }
            mood_labels = list(mood_options_map.keys())

            selected_mood_label = st.radio(
                "Mood Scale",
                options=mood_labels,
                index=mood_labels.index("😊 Okay") if "😊 Okay" in mood_labels else 2,
                key="mood_selector_radio",
                horizontal=True,
                label_visibility="collapsed"
            )

            st.session_state.current_mood_val = mood_options_map[selected_mood_label]
            if st.session_state.current_mood_val:
                st.markdown("")
                journal_prompt_text = {
                    "very_low": "What's weighing on your mind today?",
                    "low": "What are your thoughts right now?",
                    "okay": "Anything specific on your mind today?",
                    "good": "What made you feel good today?",
                    "great": "What's making you shine today?"
                }.get(st.session_state.current_mood_val, "Reflect on your mood:")

                # Initialize journal entry for the current session
                if "mood_journal_entry" not in st.session_state:
                    st.session_state.mood_journal_entry = ""
                # Initialize state for displaying tips and status
                if "mood_tip_display" not in st.session_state:
                    st.session_state.mood_tip_display = ""
                if "mood_entry_status" not in st.session_state:
                    st.session_state.mood_entry_status = ""


                st.text_area(
                    f"✏️ {journal_prompt_text}",
                    key="mood_journal_area",
                    value=st.session_state.mood_journal_entry,
                    height=70
                )

                tips_for_mood = {
                    "very_low": "Remember, it's okay not to be okay. Consider connecting with a professional.",
                    "low": "Even small steps help. Try a brief mindful moment or gentle activity.",
                    "okay": "Keep nurturing your well-being. What's one thing you can do to maintain this?",
                    "good": "That's wonderful! Savor this feeling and perhaps share your positivity.",
                    "great": "Fantastic! How can you carry this energy forward into your day?"
                }.get(st.session_state.current_mood_val, "A general tip for your mood.")

                st.markdown("")
                col_tip_save, col_ask_TalkHeal = st.columns(2)

                with col_tip_save:
                    if st.button("Get Tip & Save Entry", key="save_mood_entry", use_container_width=True):
                        st.session_state.mood_tip_display = tips_for_mood
                        st.session_state.mood_entry_status = f"Your mood entry for '{selected_mood_label}' has been noted for this session."
                        st.session_state.mood_journal_entry = ""

                with col_ask_TalkHeal:
                    if st.button("Ask TalkHeal", key="ask_peace_pulse_from_mood", use_container_width=True):
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
                    st.session_state.mood_tip_display = ""
                if st.session_state.mood_entry_status:
                    st.info(st.session_state.mood_entry_status)
                    st.session_state.mood_entry_status = ""

        # --- 4. Resource Hub with Categories & Search ---
        with st.expander("📚 Resources & Knowledge Base"):
            st.markdown("**Explore topics or search for help:**")

            resource_search_query = st.text_input("Search resources...", key="resource_search", placeholder="e.g., 'anxiety tips', 'therapy'", label_visibility="collapsed")

            if resource_search_query: 
                filtered_topics = [
                    topic for topic in mental_health_resources_full
                    if resource_search_query.lower() in topic.lower() or \
                        any(resource_search_query.lower() in link['label'].lower() for link in mental_health_resources_full[topic]['links']) or \
                        resource_search_query.lower() in mental_health_resources_full[topic]['description'].lower()
                ]

                if not filtered_topics:
                    st.info("No resources found matching your search.")
                else:
                    st.markdown("---")
                    st.markdown("**Matching Resources:**")
                    for topic in filtered_topics:
                        st.markdown(f"**{topic}**")
                        st.info(mental_health_resources_full[topic]['description'])
                        for link in mental_health_resources_full[topic]['links']:
                            st.markdown(f"• [{link['label']}]({link['url']})")
                        st.markdown("---")
            else:
                resource_tabs = st.tabs(list(mental_health_resources_full.keys()))

                for i, tab_title in enumerate(mental_health_resources_full.keys()):
                    with resource_tabs[i]:
                        topic_data = mental_health_resources_full[tab_title]
                        st.markdown(f"**{tab_title}")
                        st.info(topic_data['description'])
                        for link in topic_data['links']:
                            st.markdown(f"• [{link['label']}]({link['url']})")
                        st.markdown("---")

        with st.expander("☎️ Crisis Support"):
            # Provide localized helplines based on user's country
            user_country = get_user_country()
            country_label = user_country if user_country else "your country"
            st.markdown("### 🚨 Emergency Help")
            if user_country and user_country in country_helplines:
                st.markdown(f"**Helplines for {country_label}:**")
                for line in country_helplines[user_country]:
                    st.markdown(f"• {line}")
            else:
                st.markdown(
                    f"Couldn't detect a local helpline for {country_label}. [Find help worldwide via IASP]({IASP_LINK})"
                )

            st.markdown("---")

        with st.expander("ℹ️ About TalkHeal"):
            st.markdown("""
            **TalkHeal** is your compassionate mental health companion, designed to provide:

            • 24/7 emotional support
            • Resource guidance
            • Crisis intervention
            • Professional referrals

            **Remember:** This is not a substitute for professional mental health care.

            ---

            **Created with ❤️ by [Eccentric Explorer](https://eccentriccoder01.github.io/Me)**

            *"It's absolutely okay not to be okay :)"*

            📅 Enhanced Version - May 2025
            """)