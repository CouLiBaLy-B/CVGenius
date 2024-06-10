import json
import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash


USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
            else:
                return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def add_user(username, password):
    users = load_users()
    if username in users:
        return False
    hashed_password = generate_password_hash(password)
    users[username] = hashed_password
    save_users(users)
    return True


def check_credentials(username, password):
    users = load_users()
    if username not in users:
        return False
    return check_password_hash(users[username], password)


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()  # Recharger l'application pour refléter les changements