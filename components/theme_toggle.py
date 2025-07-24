import streamlit as st
from core.theme import toggle_theme, get_current_theme

def render_theme_toggle():
    """Render the theme toggle button in the top right corner."""
    current_theme = get_current_theme()
    is_dark = current_theme["name"] == "Dark"
    
    # Create a container for the theme toggle
    with st.container():
        # Use columns to position the toggle on the right
        col1, col2, col3 = st.columns([0.7, 0.2, 0.1])
        
        with col3:
            # Theme toggle button
            button_text = "🌙 Dark Mode" if is_dark else "☀️ Light Mode"
            button_color = "primary" if is_dark else "secondary"
            
            if st.button(
                button_text,
                key="theme_toggle",
                help="Toggle Light/Dark Mode",
                use_container_width=True,
                type=button_color
            ):
                toggle_theme()
        
        # Add some custom CSS to style the toggle button
        st.markdown("""
        <style>
        /* Theme toggle button styling - consistent with sidebar */
        [data-testid="stButton"] > button[key="theme_toggle"] {
            background: var(--light-transparent-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--light-transparent-border) !important;
            border-radius: var(--radius) !important;
            padding: 12px 16px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: 0 2px 8px var(--shadow) !important;
            backdrop-filter: blur(5px) !important;
            white-space: nowrap !important;
            text-overflow: ellipsis !important;
            overflow: hidden !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 0.9em !important;
            line-height: 1.2 !important;
            word-break: keep-all !important;
        }
        
        [data-testid="stButton"] > button[key="theme_toggle"]:hover {
            background: var(--light-transparent-bg-hover) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px var(--shadow-lg) !important;
        }
        
        /* Ensure button text doesn't wrap */
        [data-testid="stButton"] > button[key="theme_toggle"] span {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        </style>
        """, unsafe_allow_html=True) 