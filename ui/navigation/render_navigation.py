import hydralit_components as hc
from configuration.config import get_over_theme, get_menu_data
from auth.authentification import is_admin


def render_navigation():
    """
    Renders the navigation bar for the application.

    This function will render the navigation bar based on the menu data and theme
    defined in the configuration file. The "Admin" entry is only shown to
    users with the admin role.

    Returns:
        hydralit_components.nav_bar: The rendered navigation bar.
    """
    menu_data = get_menu_data(is_admin=is_admin())
    over_theme = get_over_theme()

    return hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        home_name="Home",
        hide_streamlit_markers=True,
        sticky_nav=True,
        sticky_mode="pinned",
    )
