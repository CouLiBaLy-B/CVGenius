import streamlit as st
from auth.authentification import authenticate_user
from ui.navigation.render_navigation import render_navigation
from ui.home.render_home import render_home
from ui.infos.render_infos import render_infos
from ui.todos.render_todos import render_todos
from configuration.config import setup_page_config
from scr.documentation import documentations


def main(run_setup=True, test_mode=False):
    """
    Main entry point of the application.

    This function will run the Streamlit setup configuration, authenticate the user
    and then run the application based on the user's choice from the navigation menu.

    Parameters
    ----------
    run_setup : bool, optional
        Whether to run the Streamlit setup configuration, by default True
    test_mode : bool, optional
        Whether to run the application in test mode, by default False

    Returns
    -------
    bool
        Whether the user was authenticated if in test mode
    """

    if run_setup:
        setup_page_config()

    is_authenticated = authenticate_user()

    if test_mode:
        return is_authenticated

    if is_authenticated:
        documentations()
        selected_page = render_navigation()

        if selected_page == "Home":
            render_home()
        elif selected_page == "Infos":
            render_infos()
        elif selected_page == "To Do's":
            render_todos()
    else:
        st.error("Authentication failed")


if __name__ == "__main__":
    main()
