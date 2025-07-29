import streamlit as st
from datetime import datetime
import os
import json
import google.generativeai as genai

# ---- Gemini API Setup ----
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")

# ---- File Setup ----
JOURNAL_DIR = "journal_entries"
os.makedirs(JOURNAL_DIR, exist_ok=True)

# Get user ID (customize this logic for actual user login)
user_id = st.session_state.get("user_id", "default_user")
user_file = os.path.join(JOURNAL_DIR, f"{user_id}_journal.json")

# Load past entries
if os.path.exists(user_file):
    with open(user_file, "r") as f:
        journal_entries = json.load(f)
else:
    journal_entries = []

# ---- UI ----
st.title("📝 Journaling")
st.markdown("Reflect on your thoughts. Gemini will help you analyze your emotional tone.")

# New entry input
st.markdown("### ✍️ New Entry")
entry = st.text_area("What's on your mind today?", height=200)

if st.button("Save Entry", type="primary"):
    if entry.strip():
        # Add entry
        journal_entries.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": entry.strip()
        })
        with open(user_file, "w") as f:
            json.dump(journal_entries, f, indent=2)
        st.success("Journal entry saved.")
        st.experimental_rerun()
    else:
        st.warning("Please write something before saving.")

# ---- View Past Entries ----
if journal_entries:
    st.markdown("### 📖 Your Journal History")
    for i, item in enumerate(reversed(journal_entries)):
        with st.expander(item["timestamp"]):
            st.markdown(item["content"])

            if st.button(f"Analyze Emotional Tone #{i}", key=f"analyze_{i}"):
                with st.spinner("Analyzing with Gemini..."):
                    prompt = f"""
You are a helpful emotional assistant. Analyze the emotional tone of the following journal entry. 
Provide a 1-line mood summary and then a short encouraging message.

Journal Entry: {item['content']}
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("🧠 **Gemini Insight:**")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")
else:
    st.info("No journal entries yet.")
