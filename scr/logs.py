import logging

import streamlit as st

logger = logging.getLogger("cvgenius.audit")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)


def log_action(action: str):
    """Records an audit-trail entry: which authenticated user did what, when.

    Only the username and action name are logged, never the CV content or
    job-advert text, so this satisfies data-minimization for the candidate
    personal data the app processes.

    Parameters
    ----------
    action : str
        A short, human-readable description of the action performed
        (e.g. "score_resume", "generate_cover_letter").
    """
    username = st.session_state.get('username', 'anonymous')
    logger.info("user=%s action=%s", username, action)


def log_error(context: str, exc: Exception):
    """Logs an exception server-side with context, without exposing details to the UI."""
    username = st.session_state.get('username', 'anonymous')
    logger.error("user=%s context=%s error=%s", username, context, repr(exc))
