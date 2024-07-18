import hydralit_components as hc
from configuration.config import get_over_theme, get_menu_data


def render_navigation():
    menu_data = get_menu_data()
    over_theme = get_over_theme()

    return hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        home_name="Home",
        hide_streamlit_markers=True,
        sticky_nav=True,
        sticky_mode="pinned",
    )
