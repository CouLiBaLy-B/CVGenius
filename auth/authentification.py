import streamlit as st
import streamlit_authenticator as stauth


def _to_plain_dict(value):
    """Recursively convert Streamlit's Secrets/AttrDict mapping into plain dict/list.

    streamlit_authenticator mutates the config it receives (e.g. it hashes
    plaintext passwords in place); st.secrets objects are read-only mappings
    and would raise on that mutation, so a real dict copy is required.
    """
    if hasattr(value, "items"):
        return {key: _to_plain_dict(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain_dict(item) for item in value]
    return value


def load_config():
    """Builds the streamlit-authenticator configuration from Streamlit secrets.

    Credentials, the cookie signing key and the pre-authorized email list all
    live in st.secrets (configured via the platform's "Secrets" UI in
    production, or a local, git-ignored .streamlit/secrets.toml for
    development) rather than in a file committed to the repository.

    Returns
    -------
    dict
        A dictionary with the following keys:
            - credentials: a dictionary mapping usernames to their profile
              (name, email, hashed password, role)
            - cookie: name, signing key and expiry_days for the session cookie
            - pre-authorized: emails allowed to self-register without a
              password (empty by default)
    """
    auth_secrets = _to_plain_dict(st.secrets["auth"])
    return {
        "credentials": auth_secrets["credentials"],
        "cookie": auth_secrets["cookie"],
        "pre-authorized": auth_secrets.get("pre-authorized", {"emails": []}),
    }


def get_user_role(config, username):
    """Returns the role ("admin" or "recruiter") configured for a username."""
    user = config["credentials"]["usernames"].get(username, {})
    return user.get("role", "recruiter")


def authenticate_user():
    """
    Authenticates a user based on the configuration stored in Streamlit secrets.

    Uses `streamlit_authenticator` to authenticate named, per-recruiter
    accounts. On success, stores the authenticated username and role in
    `st.session_state` so the rest of the app can gate features by role and
    attribute actions to a specific person (audit logging).

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
        clear_sensitive_session_state()
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        clear_sensitive_session_state()
        st.warning('Please enter your username and password')
    elif authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.session_state['username'] = username
        st.session_state['role'] = get_user_role(config, username)
        st.sidebar.markdown(f"Bienvenue, {name} ! 👋 ({st.session_state['role']})")
        return True

    return False


def is_admin():
    """Returns True if the currently authenticated user has the admin role."""
    return st.session_state.get('role') == 'admin'


# Session-state keys populated by the CV/job-offer and mail-completion pages
# that may hold candidate personal data (uploaded CV, job advert text) and
# must not linger past logout.
_SENSITIVE_APP_KEYS = (
    "mail_resume", "offre", "PrimaryOption_", "PrimaryOption1",
    "consent_cv_job_offer", "consent_mail_completion",
)


def clear_sensitive_session_state():
    """Drops any candidate CV/job-advert data left in session state, called on logout."""
    for key in _SENSITIVE_APP_KEYS:
        st.session_state.pop(key, None)
