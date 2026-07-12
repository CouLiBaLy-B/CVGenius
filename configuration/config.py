import streamlit as st
from PIL import Image
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_page_config():
    """
    Setup Streamlit page configuration.

    This function sets the page title, icon, sidebar state and layout. It also
    adds custom CSS styles to the page.

    :return: None
    """
    logo_path = os.path.join(PROJECT_ROOT, "images", "logo.png")
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


def get_menu_data(is_admin=False):
    """
    Retrieve the menu data for the application.

    This function provides a list of dictionaries, each representing a menu item
    with its associated icon and label. The menu items are used to render the
    top navigation (st.radio) in the application.

    Parameters
    ----------
    is_admin : bool, optional
        Whether the current user has the admin role, by default False. When
        True, an additional "Admin" entry is included for user management.

    Returns:
        list: A list of dictionaries, each containing an 'id', 'icon', and 'label' key.
    """

    menu_data = [
        {"id": "Infos", "icon": "💡", "label": "Infos"},
        {"icon": "🚀", "label": "To Do's"},
    ]
    if is_admin:
        menu_data.append({"id": "Admin", "icon": "🔑", "label": "Admin"})
    return menu_data
