from ui.navigation.render_navigation import render_navigation
from ui.home.render_home import render_home
from ui.infos.render_infos import render_infos
from ui.todos.render_todos import render_todos
from auth.authentification import authenticate_user
from configuration.config import setup_page_config
from scr.documentation import documentations


def main():
    setup_page_config()

    if authenticate_user():
        menu_id = render_navigation()
        documentations()
        if menu_id == "Home":
            render_home()
        elif menu_id == "Infos":
            render_infos()
        elif menu_id == "To Do's":
            render_todos()


if __name__ == "__main__":
    main()
