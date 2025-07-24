# styles.py:
import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def apply_custom_css():
    # Import theme configuration
    from core.theme import get_current_theme
    theme_config = get_current_theme()
    
    # Path to background image based on theme
    background_image_path = theme_config.get('background_image', 'Background.jpg')
    background_gradient = theme_config.get('background_gradient', None)
    
    base64_image = None
    if background_image_path:
        try:
            base64_image = get_base64_of_bin_file(background_image_path)
        except Exception:
            base64_image = None
    
    if base64_image:
        background_css = f'background-image: url("data:image/jpeg;base64,{base64_image}");'
    elif background_gradient:
        background_css = f'background-image: {background_gradient};'
    else:
        background_css = ''
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Root variables for consistent theming */
        :root {{
            --primary-color: {theme_config['primary']};
            --primary-light: {theme_config['primary_light']};
            --primary-dark: {theme_config['primary_dark']};
            --secondary-color: {theme_config['secondary']};
            --success-color: {theme_config['success']};
            --warning-color: {theme_config['warning']};
            --danger-color: {theme_config['danger']};
            --surface: {theme_config['surface']};
            --surface-alt: {theme_config['surface_alt']};
            --text-primary: {theme_config['text_primary']};
            --text-secondary: {theme_config['text_secondary']};
            --text-muted: {theme_config['text_muted']};
            --border: {theme_config['border']};
            --border-light: {theme_config['border_light']};
            --shadow: {theme_config['shadow']};
            --shadow-lg: {theme_config['shadow_lg']};
            --radius: 12px;
            --radius-lg: 16px;
            --light-transparent-bg: {theme_config['light_transparent_bg']};
            --light-transparent-bg-hover: {theme_config['light_transparent_bg_hover']};
            --light-transparent-border: {theme_config['light_transparent_border']};
            --active-conversation-bg: {theme_config['active_conversation_bg']};
            --active-conversation-border: {theme_config['active_conversation_border']};
            --active-conversation-shadow: {theme_config['active_conversation_shadow']};
            --background-overlay: {theme_config['background_overlay']};
            --main-text-color: {theme_config['main_text_color']};
            --sidebar-bg: {theme_config['sidebar_bg']};
            --sidebar-text: {theme_config['sidebar_text']};
            --input-bg: {theme_config['input_bg']};
            --input-text: {theme_config['input_text']};
        }}
        
        /* Global styles - Set the background image */
        .stApp {{
            {background_css}
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center center;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }}
        
        /* Apply an overlay to slightly fade the background image */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--background-overlay);
            z-index: -1;
        }}
        
        .main .block-container {{
            padding-top: 0rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}
        
        .main .block-container {{
            scroll-behavior: smooth;
        }}
        
        /* User message styling */
        .user-message {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(129, 140, 248, 0.8) 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 20px 20px 8px 20px;
            margin: 12px 0 12px auto;
            max-width: 75%;
            word-wrap: break-word;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.25);
            font-weight: 500;
            line-height: 1.5;
            position: relative;
            backdrop-filter: blur(5px);
            display: block;
            margin-left: auto;
            margin-right: 0;
        }}
        
        /* Bot message styling */
        .bot-message {{
            background: var(--surface-alt);
            color: var(--text-primary);
            padding: 16px 20px;
            border-radius: 20px 20px 20px 8px;
            margin: 12px 0;
            max-width: 75%;
            word-wrap: break-word;
            border: 1px solid var(--border);
            box-shadow: 0 2px 8px var(--shadow);
            line-height: 1.6;
            font-weight: 500;
            backdrop-filter: blur(10px);
            display: block;
            margin-left: 0;
            margin-right: auto;
        }}
        
        /* Welcome message */
        .welcome-message {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(236, 72, 153, 0.8) 100%);
            color: white;
            padding: 24px;
            border-radius: var(--radius-lg);
            margin: 24px auto;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            font-weight: 500;
            line-height: 1.6;
            backdrop-filter: blur(10px);
            display: block;
        }}
        
        /* Message time styling */
        .message-time {{
            font-size: 0.75em;
            opacity: 0.8;
            margin-top: 8px;
            text-align: right;
            font-weight: 400;
        }}
        
        .user-message .message-time {{
            color: rgba(255, 255, 255, 0.8);
        }}
        
        .bot-message .message-time {{
            color: var(--text-secondary);
        }}
        
        /* Banner */
        .banner {{
            text-align: center;
            background: var(--surface);
            color: white;
            border-radius: var(--radius-lg);
            margin-bottom: 16px;
            box-shadow: 0 8px 32px var(--shadow-lg);
            border: 1px solid var(--border-light);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}
        
        .banner::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }}
        
        .banner h3 {{
            margin: 0 0 0 0;
            font-size: 2em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .banner p {{
            margin: 0;
            font-size: 0.85em;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
        }}
        
        [data-testid="stVerticalBlock"] > div:has(h2:contains("TalkHeal")) {{ /* Targets the container with "TalkHeal" heading */
            text-align: center; 
            padding: 32px 24px;
            background: var(--surface);
            color: white; /* Ensure text is visible */
            border-radius: var(--radius-lg);
            margin-bottom: 24px;
            box-shadow: 0 8px 32px var(--transparent-box-shadow);
            border: 1px solid var(--transparent-box-border);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px); /* Frosted glass effect */
        }}
        
        [data-testid="stVerticalBlock"] > div:has(h2:contains("TalkHeal"))::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }}
        
        .main-header {{
            text-align: center;
            padding: 32px 24px;
            background: var(--surface);
            color: white;
            border-radius: var(--radius-lg);
            margin-bottom: 24px;
            border: 1px solid var(--border-light);
            position: relative;
            overflow: hidden;
        }}
        
        .main-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-color);
        }}
        
        .main-header h1 {{
            margin: 0 0 8px 0;
            font-size: 2.5em;
            font-weight: 700;
            color: #921A40;
        }}
        
        .main-header p {{
            margin: 0;
            font-size: 1.2em;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
        }}
        
        /* Emergency button */
        .emergency_button {{ 
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.9) 20%, rgba(220, 38, 38, 0.9) 80%) !important;
            color: white !important;
            padding: 18px 24px;
            display: block;
            border-radius: var(--radius);
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 600;
            font-size: 1.1em;
            border: 1px solid rgba(239, 68, 68, 0.8) !important;
            backdrop-filter: blur(5px);
            text-decoration: none !important;
        }}

        .emergency_button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            background: linear-gradient(135deg, rgba(220, 38, 38, 1) 0%, rgba(185, 28, 28, 1) 100%) !important;
        }}
        
        /* Sidebar section styling */
        .sidebar-section {{
            background: var(--light-transparent-bg) !important;
            border-radius: var(--radius-lg);
            padding: 16px !important;
            margin-bottom: 16px;
            border: 1px solid var(--light-transparent-border) !important;
            backdrop-filter: blur(10px);
        }}
        
        /* Theme section specific styling */
        .stApp [data-testid="stSidebar"] .streamlit-expanderHeader {{
            font-weight: 600 !important;
            color: var(--sidebar-text) !important;
        }}
        
        .stApp [data-testid="stSidebar"] .streamlit-expanderContent {{
            padding: 12px 0 !important;
        }}
        
        /* Theme preview circles */
        .theme-preview-circle {{
            width: 25px !important;
            height: 25px !important;
            border-radius: 50% !important;
            border: 2px solid var(--sidebar-text) !important;
            box-shadow: 0 2px 8px var(--shadow) !important;
            margin: 0 auto !important;
            display: block !important;
        }}
        
        /* Theme info box */
        .theme-info-box {{
            background: var(--light-transparent-bg) !important;
            border-radius: 8px !important;
            padding: 10px !important;
            margin-bottom: 15px !important;
            text-align: center !important;
            border: 1px solid var(--light-transparent-border) !important;
            backdrop-filter: blur(5px) !important;
        }}
        
        .theme-info-box strong {{
            color: var(--sidebar-text) !important;
            font-weight: 600 !important;
        }}
        
        .theme-info-box span {{
            font-size: 1.1em !important;
            color: var(--primary-color) !important;
            font-weight: 600 !important;
        }}
        
        /* Dark mode specific adjustments */
        .stApp [data-testid="stSidebar"] .streamlit-expanderHeader {{
            background: transparent !important;
            border: none !important;
            padding: 8px 12px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }}
        
        .stApp [data-testid="stSidebar"] .streamlit-expanderHeader:hover {{
            background: var(--light-transparent-bg) !important;
            backdrop-filter: blur(5px) !important;
        }}
        
        .stApp [data-testid="stSidebar"] .streamlit-expanderHeader[aria-expanded="true"] {{
            background: var(--light-transparent-bg) !important;
            border-radius: 8px 8px 0 0 !important;
            backdrop-filter: blur(5px) !important;
        }}
        
        .stApp [data-testid="stSidebar"] .streamlit-expanderContent {{
            background: var(--light-transparent-bg) !important;
            border-radius: 0 0 8px 8px !important;
            border: 1px solid var(--light-transparent-border) !important;
            border-top: none !important;
            backdrop-filter: blur(5px) !important;
            margin-top: 0 !important;
        }}
        
        /* Info box styling for better dark mode visibility */
        .stApp [data-testid="stSidebar"] .stAlert {{
            background: var(--light-transparent-bg) !important;
            border: 1px solid var(--light-transparent-border) !important;
            color: var(--sidebar-text) !important;
            backdrop-filter: blur(5px) !important;
        }}
        
        /* Theme toggle button specific styling - both top and sidebar */
        .stApp button[key="theme_toggle"],
        .stApp button[key="sidebar_theme_toggle"] {{
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
        }}
        
        .stApp button[key="theme_toggle"]:hover,
        .stApp button[key="sidebar_theme_toggle"]:hover {{
            background: var(--light-transparent-bg-hover) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px var(--shadow-lg) !important;
        }}
        
        /* Ensure button text doesn't wrap */
        .stApp button[key="theme_toggle"] span,
        .stApp button[key="sidebar_theme_toggle"] span {{
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        

        
        /* Button styling*/
        button, 
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button,
        [data-baseweb="button"] {{
            background: var(--light-transparent-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--light-transparent-border) !important;
            border-radius: var(--radius) !important;
            padding: 12px 16px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            backdrop-filter: blur(5px) !important;
            white-space: nowrap !important;
            text-overflow: ellipsis !important;
            overflow: hidden !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        
        button:hover, 
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover,
        [data-baseweb="button"]:hover {{
            background: var(--light-transparent-bg-hover) !important;
            color: var(--primary-color) !important;
            border-color: var(--primary-color) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        }}
        
        /* Primary buttons */
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {{
            background: rgba(99, 102, 241, 0.7) !important;
            color: white !important;
            font-weight: 700 !important;
        }}
        
        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover {{
            background: rgba(99, 102, 241, 0.9) !important;
            color: white !important;
        }}
        
        .stApp [data-testid="stSidebar"] .stButton button[data-testid*="stButton-primary"] {{
            background: var(--active-conversation-bg) !important;
            color: white !important;
            border: 2px solid var(--active-conversation-border) !important;
            box-shadow: 0 6px 20px var(--active-conversation-shadow) !important;
            font-weight: 700 !important;
            transform: translateX(8px) scale(1.02) !important;
        }}
        
        /* Sidebar toggle button */
        .stApp [data-testid="stSidebarToggleButton"] button,
        button[data-testid="stSidebarToggleButton"] {{
            background: var(--light-transparent-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--light-transparent-border) !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            font-size: 20px !important;
            font-weight: 900 !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        }}
        
        /* Form input styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{ /* Added textarea for mood journal */
            background: var(--input-bg) !important;
            border: 2px solid var(--border) !important;
            border-radius: var(--radius) !important;
            padding: 12px 16px !important;
            font-size: 1em !important;
            color: #111 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.2s ease !important;
            backdrop-filter: blur(5px) !important;
        }}
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {{
            color: #111 !important;
            opacity: 1 !important;
        }}
        .stTextInput > div > div > input::-webkit-input-placeholder,
        .stTextArea > div > div > textarea::-webkit-input-placeholder {{
            color: #111 !important;
            opacity: 1 !important;
        }}
        .stTextInput > div > div > input::-moz-placeholder,
        .stTextArea > div > div > textarea::-moz-placeholder {{
            color: #111 !important;
            opacity: 1 !important;
        }}
        .stTextInput > div > div > input:-ms-input-placeholder,
        .stTextArea > div > div > textarea:-ms-input-placeholder {{
            color: #111 !important;
            opacity: 1 !important;
        }}
        .stTextInput > div > div > input::-ms-input-placeholder,
        .stTextArea > div > div > textarea::-ms-input-placeholder {{
            color: #111 !important;
            opacity: 1 !important;
        }}
        
        /* Sidebar styling */
        .stApp [data-testid="stSidebar"] {{
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border-light) !important;
            box-shadow: 4px 0 24px var(--shadow-lg) !important;
            backdrop-filter: blur(10px) !important;
        }}
        
        /* Text in sidebar*/
        .stApp [data-testid="stSidebar"] h1,
        .stApp [data-testid="stSidebar"] h2,
        .stApp [data-testid="stSidebar"] h3,
        .stApp [data-testid="stSidebar"] h4,
        .stApp [data-testid="stSidebar"] p,
        .stApp [data-testid="stSidebar"] label,
        .stApp [data-testid="stSidebar"] .stMarkdown {{
            color: var(--sidebar-text) !important;
            text-shadow: none !important;
        }}
        
        /* Main content text*/
        .stApp .main h1,
        .stApp .main h2,
        .stApp .main h3,
        .stApp .main h4,
        .stApp .main p,
        .stApp .main .stMarkdown {{
            color: var(--main-text-color) !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        }}
        
        /* Info messages */
        .stInfo {{
            background: rgba(99, 102, 241, 0.2) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius) !important;
        }}
        
        .stSuccess {{
            background: rgba(16, 185, 129, 0.2) !important;
            color: #047857 !important;
            border-radius: var(--radius) !important;
        }}
        
        .stWarning {{
            background: rgba(245, 158, 11, 0.2) !important;
            color: #92400e !important;
            border-radius: var(--radius) !important;
        }}
        
        /* Hide default Streamlit elements */
        .stApp > header {{
            display: none !important;
        }}
        
        div[data-testid="stToolbar"] {{
            display: none !important;
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem;
            }}
            
            .user-message, .bot-message {{
                max-width: 90%;
                padding: 12px 16px;
            }}
            
            .main-header h1 {{
                font-size: 2em;
            }}
        }}

        /* Custom mood selector radio buttons - white circles */
        .stRadio > div[role='radiogroup'] > label > div:first-child {{
            background: white !important;
            border: 2px solid var(--primary-color) !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        }}
        .stRadio > div[role='radiogroup'] > label > div:first-child svg {{
            color: var(--primary-color) !important;
        }}
    </style>
    """, unsafe_allow_html=True)