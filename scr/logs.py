import json
import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()
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


def add_user(username, email, password):
    users = load_users()
    if username in users or any(user["email"] == email for user in users.values()):
        return False
    hashed_password = generate_password_hash(password)
    verification_token = str(uuid.uuid4())
    users[username] = {
        "email": email,
        "password": hashed_password,
        "verified": False,
        "verification_token": verification_token
    }
    save_users(users)
    return verification_token


def send_verification_email(email, verification_token):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))

    verification_link = f"http://localhost:8501/?verification_token={verification_token}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Vérifiez votre adresse email pour CV Genius"

    body = f"""
    Merci de vous être inscrit sur CV Genius !

    Veuillez cliquer sur le lien suivant pour vérifier votre adresse email :
    {verification_link}

    Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.

    Cordialement,
    L'équipe CV Genius
    """
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)


def verify_email(verification_token):
    users = load_users()
    for username, user_data in users.items():
        if user_data["verification_token"] == verification_token:
            users[username]["verified"] = True
            save_users(users)
            return True
    return False


def check_credentials(username, password):
    users = load_users()
    if username not in users:
        return False, "Nom d'utilisateur incorrect."
    if not users[username]["verified"]:
        return False, "Veuillez vérifier votre email avant de vous connecter."
    if check_password_hash(users[username]["password"], password):
        return True, "Connexion réussie !"
    return False, "Mot de passe incorrect."


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()  # Recharger l'application pour refléter les changements