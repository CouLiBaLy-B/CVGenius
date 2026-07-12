import streamlit as st
import streamlit_authenticator as stauth

from scr.logs import log_action


def render_admin():
    """
    Renders the admin-only account management page.

    Because the app's user directory lives in Streamlit secrets (there is no
    writable persistent database on Streamlit Community Cloud / Hugging Face
    Spaces), accounts cannot be created or removed live from within the app.
    Instead, this page helps an admin hash a new recruiter's password and
    produces the exact TOML snippet to paste into the deployment's Secrets
    settings.

    :return: None
    """
    st.markdown("<div class='title'>Gestion des comptes</div>", unsafe_allow_html=True)
    st.markdown(
        """<div class='description'>Les comptes sont stockés dans les
        "Secrets" de la plateforme d'hébergement (pas dans le dépôt de code).
        Générez ci-dessous le bloc à coller dans les Secrets pour ajouter ou
        mettre à jour un compte.</div>""",
        unsafe_allow_html=True,
    )

    with st.form("new_account_form"):
        username = st.text_input("Identifiant (ex: jdupont)")
        name = st.text_input("Nom complet")
        email = st.text_input("Email")
        role = st.selectbox("Rôle", ["recruiter", "admin"])
        password = st.text_input("Mot de passe temporaire", type="password")
        submitted = st.form_submit_button("Générer le bloc Secrets")

    if submitted:
        if not (username and name and email and password):
            st.error("Tous les champs sont obligatoires.")
            return

        log_action(f"admin_generate_account_snippet:{username}")
        hashed_password = stauth.Hasher([password]).generate()[0]
        snippet = (
            f"[auth.credentials.usernames.{username}]\n"
            f'name = "{name}"\n'
            f'email = "{email}"\n'
            f'role = "{role}"\n'
            f'password = "{hashed_password}"\n'
        )
        st.success("Compte généré. Copiez ce bloc dans les Secrets de l'application, puis redéployez.")
        st.code(snippet, language="toml")
        st.warning(
            "Communiquez le mot de passe temporaire au recruteur par un canal "
            "sécurisé distinct (pas par le même message que ce bloc)."
        )
