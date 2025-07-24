import streamlit as st
from core.utils import get_current_time, get_ai_response

import streamlit.components.v1 as components
import streamlit as st
from datetime import datetime, timedelta
import json
from core.utils import save_conversations, load_conversations

def set_user_time_in_session():
    if "user_time_offset" not in st.session_state:
        # Embed JS to send local timezone offset in minutes
        components.html("""
            <script>
            const offset = new Date().getTimezoneOffset(); // in minutes
            const time = new Date().toLocaleString();      // full readable local time
            const data = {offset: offset, time: time};
            window.parent.postMessage({type: 'USER_TIME', data: data}, '*');
            </script>
        """, height=0)

        st.markdown("""
        <script>
        window.addEventListener("message", (event) => {
            if (event.data.type === "USER_TIME") {
                const payload = JSON.stringify(event.data.data);
                fetch("/", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: payload
                }).then(() => location.reload());
            }
        });
        </script>
        """, unsafe_allow_html=True)

    else:
        # Already set, do nothing
        pass

set_user_time_in_session()

def render_chat_interface():    
    if st.session_state.active_conversation >= 0:
        active_convo = st.session_state.conversations[st.session_state.active_conversation]
        
        # Show welcome message if no messages exist
        if not active_convo["messages"]:
            st.markdown(f"""
            <div class="welcome-message">
                <strong>Hello! I'm TalkHeal, your mental health companion</strong><br>
                How are you feeling today? You can write it down below or for a fresh start click on "➕ New Chat" on the left and choose a common topic😊               <div class="message-time">{get_current_time()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Render all messages directly without any wrapper container
        for msg in active_convo["messages"]:
            if msg["sender"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    {msg["message"]}
                    <div class="message-time">{msg["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bot-message">
                    {msg["message"]}
                    <div class="message-time">{msg["time"]}</div>
                </div>
                """, unsafe_allow_html=True)

def handle_chat_input(model):   
    if "pre_filled_chat_input" not in st.session_state:
        st.session_state.pre_filled_chat_input = ""
    initial_chat_value = st.session_state.pre_filled_chat_input
    st.session_state.pre_filled_chat_input = "" 

    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Share your thoughts...", 
                key="message_input", 
                label_visibility="collapsed",
                placeholder="Type your message here...",
                value=initial_chat_value
            )
        
        with col2:
            send_pressed = st.form_submit_button("Send", use_container_width=True)
    
    if (send_pressed or st.session_state.get('send_chat_message', False)) and user_input.strip():
        if 'send_chat_message' in st.session_state:
            st.session_state.send_chat_message = False

        if st.session_state.active_conversation >= 0:
            current_time = get_current_time()
            active_convo = st.session_state.conversations[st.session_state.active_conversation]
            active_convo["messages"].append({
                "sender": "user", 
                "message": user_input.strip(), 
                "time": current_time
            })
            save_conversations(st.session_state.conversations)
            if len(active_convo["messages"]) == 1:
                title = user_input[:30] + "..." if len(user_input) > 30 else user_input
                active_convo["title"] = title
            with st.spinner("TalkHeal is thinking..."):
                try:
                    def format_memory_for_prompt(convo_history, max_turns=10):
                        context = ""
                        for msg in convo_history[-max_turns*2:]:  # user+bot per turn
                            sender = "User" if msg["sender"] == "user" else "Bot"
                            context += f"{sender}: {msg['message']}\n"
                        return context

                    context = format_memory_for_prompt(active_convo["messages"])
                    full_prompt = context + f"User: {user_input.strip()}\nBot:"

                    ai_response = get_ai_response(full_prompt, model)
                    
                    active_convo["messages"].append({
                        "sender": "bot", 
                        "message": ai_response, 
                        "time": get_current_time()
                    })
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    active_convo["messages"].append({
                        "sender": "bot", 
                        "message": "I apologise, but I'm having trouble responding right now. Please try again in a moment.", 
                        "time": get_current_time()
                    })
                    save_conversations(st.session_state.conversations)
            st.rerun()