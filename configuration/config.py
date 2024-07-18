import streamlit as st
from PIL import Image
import os


def setup_page_config():
    logo_path = os.path.join(os.getcwd(), "images", "logo.png")
    logo = Image.open(logo_path)

    st.set_page_config(
        page_title="CV Genius",
        page_icon=logo,
        initial_sidebar_state="collapsed",
        layout='wide'
    )

    # Add CSS styles
    st.markdown("""
    <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #2D3E50;
        }
        .subtitle {
            font-size: 24px;
            font-weight: bold;
            color: #4A6F8A;
        }
        .description {
            font-size: 18px;
            color: #6C8798;
        }
    </style>
    """, unsafe_allow_html=True)


def get_over_theme():
    return {
        "txc_inactive": "#FFFFFF",
        "color": "#FF6300",
        "txc_active": "#2D3E50",
        "MENU_BACKGROUND": "#FF6300",
        "txc_hover": "#4A6F8A",
        "MENU_BACKGROUND_HOVER": "#4A6F8A",
    }


def get_menu_data():
    return [
        {"id": "Infos", "icon": "💡", "label": "Infos"},
        {"icon": "🚀", "label": "To Do's"},
    ]
