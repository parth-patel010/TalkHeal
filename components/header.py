import streamlit as st

def render_header():
    with st.container():
        # Top bar with hamburger menu and theme toggle
        col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
        
        with col1:
            if st.button("☰", key="top_hamburger_menu", help="Toggle Sidebar", use_container_width=True):
                if st.session_state.sidebar_state == "expanded":
                    st.session_state.sidebar_state = "collapsed"
                else:
                    st.session_state.sidebar_state = "expanded"
                st.rerun()
        
        with col3:
            is_dark = st.session_state.get('dark_mode', False)
            if st.button("🌙" if is_dark else "☀️", key="top_theme_toggle", help="Toggle Light/Dark Mode", use_container_width=True):
                st.session_state.dark_mode = not is_dark
                st.session_state.theme_changed = True
                st.rerun()
        
        st.markdown("""
        <div class="main-header">
            <h1>TalkHeal</h1>
            <p>Your Mental Health Companion 💙</p>
        </div>
        """, unsafe_allow_html=True)
        ## Commented out this part of the header because the 'emergency button' functionality is quite similar, hence causing redundancy. ##

        # with st.expander("📍 Find Help Nearby"):
        #     location_input = st.text_input("Enter your city", key="header_location_search")
        #     if st.button("🔍 Search Centers", key="header_search_nearby"):
        #         if location_input:
        #             search_url = f"https://www.google.com/maps/search/mental+health+centers+{location_input.replace(' ', '+')}"
        #             st.markdown(f'<a href="{search_url}" target="_blank">🗺️ View Mental Health Centers Near {location_input}</a>', unsafe_allow_html=True)
        #             st.success("Opening search results in a new tab...")
        #         else:
        #             st.warning("Please enter a city name")
