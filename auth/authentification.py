import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def load_config():
    """Loads configuration from auth/config.yaml.

    Returns a dictionary with the following keys:
        - credentials: a dictionary mapping usernames to passwords
        - cookie: a dictionary with the following keys:
            - name: the name of the cookie set by the authenticator
            - key: the key used to encrypt the cookie
            - expiry_days: the number of days the cookie should last
        - pre-authorized: a list of usernames that are allowed to log in
            without a password
    """
    with open('auth/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config


def authenticate_user():
    """
    Authenticates a user based on the configuration settings.

    This function uses the `streamlit_authenticator` library to authenticate
    users with credentials specified in a configuration file. It handles various
    authentication statuses, providing appropriate user feedback via Streamlit UI
    components.

    Returns:
        bool: True if the user is authenticated successfully, False otherwise.
    """

    config = load_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

    name, authentication_status, username = authenticator.login()

    if authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')
    elif authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.markdown(f"Bienvenue, {name} ! 👋")
        return True

    return False
