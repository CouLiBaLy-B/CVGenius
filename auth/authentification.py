import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def load_config():
    with open('auth/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config


def authenticate_user():
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
