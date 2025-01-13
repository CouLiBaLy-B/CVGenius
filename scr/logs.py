import json
import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash


USERS_FILE = "users.json"


def load_users():
    """
    Loads user data from a JSON file.

    Reads the contents of USERS_FILE and returns a dictionary of users
    if the file contains valid JSON data. If the file is empty or not
    found, or if there's a JSON decode error, it returns an empty dictionary.

    Returns:
        dict: A dictionary containing usernames as keys and hashed passwords as values.
    """

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
    """
    Saves user data to a JSON file.

    Writes the provided dictionary of users to USERS_FILE in JSON format.
    Each key-value pair in the dictionary represents a username and its
    corresponding hashed password.

    Args:
        users (dict): A dictionary containing usernames as keys and hashed
                    passwords as values.

    Raises:
        TypeError: If the input is not serializable to JSON.
    """

    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def add_user(username, password):
    """
    Adds a new user to the system.

    Creates a new user with the given username and password, and stores
    the hashed password in the users file.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.

    Returns:
        bool: True if the user was successfully added, False if the username already exists.
    """
    users = load_users()
    if username in users:
        return False
    hashed_password = generate_password_hash(password)
    users[username] = hashed_password
    save_users(users)
    return True


def check_credentials(username, password):
    """
    Checks the provided username and password against the stored users.

    Args:
        username (str): The username to check.
        password (str): The password to check.

    Returns:
        bool: True if the username and password match a stored user, False otherwise.
    """
    users = load_users()
    if username not in users:
        return False
    return check_password_hash(users[username], password)


def logout():
    """
    Logs the user out of the application.

    Sets the "logged_in" key in the session state to False and sets the "username" key to None.
    This function is usually called when the user clicks the "Logout" button in the navigation menu.
    """

    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()  # Recharger l'application pour refléter les changements
