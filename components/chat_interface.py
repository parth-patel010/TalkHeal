import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from core.utils import get_current_time, get_ai_response, save_conversations
import requests

# Inject JS to get user's local time zone
def set_user_time_in_session():
    if "user_time_offset" not in st.session_state:
        components.html("""
            <script>
            const offset = new Date().getTimezoneOffset(); 
            const time = new Date().toLocaleString();      
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

set_user_time_in_session()

# Display chat messages
def render_chat_interface():    
    if st.session_state.active_conversation >= 0:
        active_convo = st.session_state.conversations[st.session_state.active_conversation]

        if not active_convo["messages"]:
            st.markdown(f"""
            <div class="welcome-message">
                <strong>Hello! I'm TalkHeal, your mental health companion 🤗</strong><br>
                How are you feeling today? You can write below or start a new topic.
                <div class="message-time">{get_current_time()}</div>
            </div>
            """, unsafe_allow_html=True)

        for msg in active_convo["messages"]:
            css_class = "user-message" if msg["sender"] == "user" else "bot-message"
            st.markdown(f"""
            <div class="{css_class}">
                {msg["message"]}
                <div class="message-time">{msg["time"]}</div>
            </div>
            """, unsafe_allow_html=True)

# Handle chat input and generate AI response
def handle_chat_input(model, system_prompt):
    if "pre_filled_chat_input" not in st.session_state:
        st.session_state.pre_filled_chat_input = ""
    initial_value = st.session_state.pre_filled_chat_input
    st.session_state.pre_filled_chat_input = ""

    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Share your thoughts...",
                key="message_input",
                label_visibility="collapsed",
                placeholder="Type your message here...",
                value=initial_value
            )
        with col2:
            send_pressed = st.form_submit_button("Send", use_container_width=True)

    if (send_pressed or st.session_state.get("send_chat_message", False)) and user_input.strip():
        if 'send_chat_message' in st.session_state:
            st.session_state.send_chat_message = False

        if st.session_state.active_conversation >= 0:
            current_time = get_current_time()
            active_convo = st.session_state.conversations[st.session_state.active_conversation]

            # Save user message
            active_convo["messages"].append({
                "sender": "user",
                "message": user_input.strip(),
                "time": current_time
            })

            # Set title if it's the first message
            if len(active_convo["messages"]) == 1:
                title = user_input[:30] + "..." if len(user_input) > 30 else user_input
                active_convo["title"] = title

            save_conversations(st.session_state.conversations)

            # Format memory
            def format_memory(convo_history, max_turns=10):
                context = ""
                for msg in convo_history[-max_turns*2:]:  # user + bot per turn
                    sender = "User" if msg["sender"] == "user" else "Bot"
                    context += f"{sender}: {msg['message']}\n"
                return context

            try:
                with st.spinner("TalkHeal is thinking..."):
                    memory = format_memory(active_convo["messages"])
                    prompt = f"{system_prompt}\n\n{memory}\nUser: {user_input.strip()}\nBot:"
                    ai_response = get_ai_response(prompt, model)

                    active_convo["messages"].append({
                        "sender": "bot",
                        "message": ai_response,
                        "time": get_current_time()
                    })

            except ValueError as e:
                st.error("I'm having trouble understanding your message. Could you please rephrase it?")
                active_convo["messages"].append({
                    "sender": "bot",
                    "message": "I'm having trouble understanding your message. Could you please rephrase it?",
                    "time": get_current_time()
                })
            except requests.RequestException as e:
                st.error("Network connection issue. Please check your internet connection.")
                active_convo["messages"].append({
                    "sender": "bot",
                    "message": "I'm having trouble connecting to my services. Please check your internet connection and try again.",
                    "time": get_current_time()
                })
            except Exception as e:
                st.error(f"An unexpected error occurred. Please try again.")
                active_convo["messages"].append({
                    "sender": "bot",
                    "message": "I'm having trouble responding right now. Please try again in a moment.",
                    "time": get_current_time()
                })

            save_conversations(st.session_state.conversations)
            st.rerun()
