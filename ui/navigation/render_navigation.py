import streamlit as st
from configuration.config import get_menu_data
from auth.authentification import is_admin


def render_navigation():
    """
    Renders the top navigation for the application as a horizontal radio.

    The available pages come from the menu data defined in the configuration
    module, with "Home" always shown first. The "Admin" entry is only
    included for users with the admin role.

    Returns:
        str: The id of the selected page ("Home", "Infos", "To Do's" or "Admin").
    """
    menu_data = [{"id": "Home", "icon": "🏠", "label": "Home"}] + get_menu_data(is_admin=is_admin())
    page_ids = [item.get("id", item["label"]) for item in menu_data]
    page_captions = {item.get("id", item["label"]): f"{item['icon']} {item['label']}" for item in menu_data}

    return st.radio(
        "Navigation",
        page_ids,
        format_func=lambda page_id: page_captions[page_id],
        horizontal=True,
        label_visibility="collapsed",
        key="main_navigation",
    )
