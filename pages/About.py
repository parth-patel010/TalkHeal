import streamlit as st
import base64

st.set_page_config(page_title="About TalkHeal", layout="wide")

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
set_background("./mint.png")

# ------------ About Page Content ------------
st.title("About TalkHeal")
st.markdown("---")

st.markdown("""
**ℹ️ About TalkHeal**  
Your compassionate mental health companion, designed to provide:

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
