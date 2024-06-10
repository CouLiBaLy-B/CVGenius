import streamlit as st
import hydralit_components as hc

import os
from scr.utils import extract_text_from_pdf, generate_pdf
from scr.models import (
    ResumeImprover,
    CoverLetterGenerator,
    ScoreResumeJob,
    ResumeGenerator,
    MailCompletion,
)
from scr.documentation import documentations
from scr.logs import add_user, check_credentials, logout

from PIL import Image

logo_path = os.path.join(os.getcwd(), "images", "logo.png")
logo = Image.open(logo_path)


st.set_page_config(
    page_title="CV Genius",
    page_icon=logo,
    initial_sidebar_state="collapsed",
    layout='wide'
)

# Définir les styles CSS avec les couleurs d'Extia
css = """
<style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #2D3E50;
    }
    .subtitle {
        font-size: 24px;
        font-weight: bold;
        color: #4A6F8A;
    }
    .description {
        font-size: 18px;
        color: #6C8798;
    }
</style>
"""

# Appliquer les styles CSS
st.markdown(css, unsafe_allow_html=True)


st.markdown("""<h1 style='text-align: center;
            background-color: #1587EA;
            color: #ece5f6'>CV Genius</h1>""",
            unsafe_allow_html=True)
st.markdown("""<h4 style='text-align: center;
            background-color: #1587EA;
            color: #ece5f6'>Améliorez votre processus de candidature</h4>""",
            unsafe_allow_html=True)


# Définir les couleurs pour le menu de navigation
over_theme = {
    "txc_inactive": "#FFFFFF",
    "color": "#FF6300",
    "txc_active": "#2D3E50",
    "MENU_BACKGROUND": "#FF6300",
    "txc_hover": "#4A6F8A",
    "MENU_BACKGROUND_HOVER": "#4A6F8A",
    # "border-radius": "10px"
}


def get_menu_data():
    if st.session_state.get("logged_in", False):
        return [
            {"id": "Infos", "icon": "💡", "label": "Infos"},
            {"icon": "🚀", "label": "To Do's"},
            {"icon": "🚪", "label": "Logout"},
        ]
    else:
        return [
            {"id": "Infos", "icon": "💡", "label": "Infos"},
            {"icon": "🚀", "label": "To Do's"},
            {"icon": "📝", "label": "Sign Up"},
            {"icon": "🔒", "label": "Login"},
        ]


# Utiliser cette fonction pour générer le menu
menu_data = get_menu_data()
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name="Home",
    hide_streamlit_markers=True,
    sticky_nav=True,
    sticky_mode="pinned",
)

# Onglet "Login"
if menu_id == "Login":
    st.markdown("<div class='title'>Login</div>", unsafe_allow_html=True)
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if check_credentials(username, password):
            st.success("Connexion réussie !")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Recharger l'application pour refléter les changements
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")

# Onglet "Sign Up"
if menu_id == "Sign Up":
    st.markdown("<div class='title'>Sign Up</div>", unsafe_allow_html=True)
    new_username = st.text_input("Nouveau nom d'utilisateur")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe",
                                     type="password")

    if st.button("S'inscrire"):
        if new_password != confirm_password:
            st.error("Les mots de passe ne correspondent pas.")
        elif add_user(new_username, new_password):
            st.success(
                "Inscription réussie ! Vous pouvez maintenant vous connecter."
                )
            st.rerun()
        else:
            st.error("Ce nom d'utilisateur existe déjà.")

if menu_id == "Logout":
    logout()
    st.success("Vous avez été déconnecté avec succès !")
    st.rerun()

if not st.session_state.get("logged_in", False):
    if menu_id not in ["Login", "Sign Up"]:
        st.warning("Veuillez vous connecter pour accéder à l'application.")
        st.stop()
else:
    # Afficher un message de bienvenue si l'utilisateur est connecté
    st.sidebar.markdown(f"Bienvenue, {st.session_state.username} ! 👋")
# Vérifier si l'utilisateur est connecté avant d'afficher le contenu principal
if not st.session_state.get("logged_in", False):
    st.warning("Veuillez vous connecter pour accéder à l'application.")
    st.stop()

st.sidebar.image(Image.open(os.path.join(os.getcwd(),
                                         "images",
                                         "background.jpg"
                                         )
                            )
                 )

st.sidebar.markdown(
    "<div class='title'>CV Genius</div>", unsafe_allow_html=True
)
st.sidebar.markdown(
    "<div class='subtitle'>Améliorez votre processus de candidature</div>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """<div class='description'>Cette application utilise des modèles d'IA pour
    vous aider à scorer votre CV, rédiger des lettres de motivation et
    améliorer votre CV.</div>""",
    unsafe_allow_html=True,
)

with st.sidebar.expander("HuggingFace Accees Key"):
    documentations()

# override the theme, else it will use the Streamlit applied theme
over_theme_ = {
    "txc_inactive": "white",
    "menu_background": "#b9b2b2",
    "txc_active": "Black",
    "option_active": "#FF6300",
}

font_fmt_ = {"font-class": "h1", "font-size": "100%", "color": "black"}

# Onglet "Main"
if menu_id == "Home":
    option_data = [
            {"icon": "📝", "label": "CV et offre d'emploi"},
            {"icon": "📧", "label": "Completion de mail"},
    ]
    # display a horizontal version of the option bar
    cv_mail_option = hc.option_bar(
            option_definition=option_data,
            title="Que vous voulez faire ?",
            key="PrimaryOption_",
            override_theme=over_theme,
            font_styling=font_fmt_,
            horizontal_orientation=True,
        )

    if cv_mail_option == "CV et offre d'emploi":
        option_data = [
            {"label": "Score de correspondance"},
            {"label": "Rédaction de lettre de motivation"},
            {"label": "Amélioration de CV"},
        ]

        font_fmt = {"font-class": "h2", "font-size": "100%"}

        # display a horizontal version of the option bar
        task = hc.option_bar(
            option_definition=option_data,
            title="Que vous voulez faire ?",
            key="PrimaryOption1",
            override_theme=over_theme,
            font_styling=font_fmt,
            horizontal_orientation=True,
        )

        resume_pdf = st.file_uploader("Import ton CV en pdf",
                                      type="pdf")
        job_advert = st.text_area("L'offre de poste",
                                  value="",
                                  height=400,
                                  key="offre")

        if resume_pdf is None:
            st.error("Veuillez importer votre CV avant de continuer.")
        elif job_advert == "":
            st.error("""Veuillez saisir une description de
                     poste avant de continuer.""")
        else:
            try:
                if st.button("Lancer"):
                    with st.spinner("Wait for it..."):
                        resume = extract_text_from_pdf(resume_pdf)
                        if task == "Score de correspondance":
                            generator = ResumeGenerator(
                                resume=resume,
                                job_advert=job_advert,
                                resumeStrategy=ScoreResumeJob(),
                            )
                            generated = generator.generator()
                            st.markdown(generated,
                                        unsafe_allow_html=True)
                            pdf_output = generate_pdf(generated)
                            st.download_button(
                                label="Télécharger l'analyse",
                                data=pdf_output.getvalue(),
                                file_name="matching_score.pdf",
                                mime="application/pdf",
                            )
                        if task == "Rédaction de lettre de motivation":
                            generator = ResumeGenerator(
                                resume=resume,
                                job_advert=job_advert,
                                resumeStrategy=CoverLetterGenerator(),
                            )
                            generated = generator.generator()
                            st.write(generated)
                            pdf_output = generate_pdf(generated)
                            st.download_button(
                                label="Télécharger la lettre de motivation",
                                data=pdf_output.getvalue(),
                                file_name="cover_letter.pdf",
                                mime="application/pdf",
                            )
                        if task == "Amélioration de CV":
                            generator = ResumeGenerator(
                                resume=resume,
                                job_advert=job_advert,
                                resumeStrategy=ResumeImprover(),
                            )
                            generated = generator.generator()
                            try:
                                st.markdown(generated,
                                            unsafe_allow_html=True)
                                pdf_output = generate_pdf(generated)
                                st.download_button(
                                    label="Télécharger le CV",
                                    data=pdf_output.getvalue(),
                                    file_name="resume.pdf",
                                    mime="application/pdf",
                                )
                            except Exception as e:
                                st.exception(f"Erreur {e}")
                    st.success("Done!")
            except Exception as e:
                st.exception(f"Erreur {e}")
    if cv_mail_option == "Completion de mail":
        resume_pdf = st.file_uploader(
            "Import ton CV en pdf", type="pdf", key="mail_resume"
        )
        if resume_pdf is not None:
            try:
                if st.button("Lancer", key="mail"):
                    with st.spinner("Wait for it..."):
                        resume = extract_text_from_pdf(resume_pdf)
                        generator = MailCompletion()
                        mail_complet = generator.mailcompletion(resume=resume)
                        st.write(mail_complet)
                        pdf_output = generate_pdf(mail_complet)
                        st.download_button(
                            label="Télécharger le mail",
                            data=pdf_output.getvalue(),
                            file_name="mail.pdf",
                            mime="application/pdf",
                        )
                    st.success("Done!")
            except Exception as e:
                st.exception(f"Erreur {e}")

# Onglet "Info"
if menu_id == "Infos":
    st.markdown(
        "<div class='title'>À propos de cette application</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        """<div class='description'>Cette application utilise le modèle
        d'IA MixTraL-8x7B-Instruct-v0.1, développé par MistralAI. Ce modèle
        a été entraîné sur une grande variété de tâches de traitement
        du langage naturel, y compris la rédaction, l'analyse et la
        génération de texte.</div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='subtitle'>Tâches effectuées</div>",
                unsafe_allow_html=True)
    st.markdown(
        """- **Score de correspondance** : Évaluer la correspondance entre
        votre CV et une offre d'emploi spécifique en attribuant un score
        sur 100 et en identifiant les points forts et les points faibles.""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """- **Rédaction de lettre de motivation** : Générer une lettre de
        motivation personnalisée en fonction de votre CV et de
        l'offre d'emploi.""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """- **Amélioration de CV** : Améliorer votre CV en intégrant les
        compétences, qualifications et expériences pertinentes pour
        l'offre d'emploi visée.""",
        unsafe_allow_html=True,
    )

# Onglet "To-do's"
if menu_id == "To Do's":
    st.markdown(
        "<div class='title'>Améliorations futures</div>",
        unsafe_allow_html=True
    )

    st.markdown("### Fonctionnalités supplémentaires")
    st.markdown(
        """- **Analyse des compétences** : Ajouter une fonctionnalité pour
        analyser les compétences du candidat à partir de son CV et fournir
        des recommandations pour combler les lacunes par rapport à
        l'offre d'emploi."""
    )
    st.markdown(
        """- **Optimisation du CV pour les systèmes ATS** : Intégrer une
        fonctionnalité pour optimiser le CV afin qu'il soit mieux reconnu
        par les systèmes de suivi des candidats (ATS) utilisés par
        les entreprises."""
    )
    st.markdown(
        """- **Suggestions de postes pertinents** : Développer une
        fonctionnalité pour recommander des offres d'emploi pertinentes
        en fonction du profil du candidat."""
    )
    st.markdown(
        """- **Suivi des candidatures** : Ajouter une fonctionnalité
        permettant aux utilisateurs de suivre leurs candidatures et
        de recevoir des rappels pour les étapes suivantes."""
    )
    st.markdown("### Améliorations de l'interface utilisateur")
    st.markdown(
        """- **Thème personnalisable** : Permettre aux utilisateurs de
        choisir un thème de couleurs personnalisé pour l'application."""
    )
    st.markdown(
        """- **Mode sombre** : Ajouter un mode sombre pour une meilleure
        expérience dans des environnements faiblement éclairés."""
    )
    st.markdown(
        """- **Aide contextuelle** : Fournir des info-bulles et des guides
        pour aider les utilisateurs à comprendre les différentes
        fonctionnalités de l'application."""
    )

    st.markdown("### Intégrations supplémentaires")
    st.markdown(
        """- **Intégration avec des services d'emploi** : Permettre aux
        utilisateurs de se connecter à des services d'emploi populaires,
        comme LinkedIn ou Indeed, pour importer leurs informations de
        profil et postuler directement depuis l'application."""
    )
    st.markdown(
        """- **Partage de CV** : Ajouter une fonctionnalité pour partager
        facilement le CV amélioré avec des employeurs potentiels ou
        des réseaux professionnels."""
    )

    st.markdown("### Améliorations de performance")
    st.markdown(
        """- **Mise en cache des résultats** : Mettre en cache les résultats
        générés par le modèle d'IA pour accélérer les temps de
        réponse lors de requêtes ultérieures similaires."""
    )
    st.markdown(
        """- **Traitement parallèle** : Explorer les possibilités de traitement
        parallèle pour accélérer les temps de réponse, en particulier
        pour les tâches gourmandes en ressources."""
    )

    st.markdown(
        """N'hésitez pas à soumettre vos propres idées d'améliorations dans
        la section des commentaires ci-dessous."""
    )

_, _, _, text, logo = st.columns([4, 1, 1, 1, 0.5])
with text:
    st.markdown("<h7 style='text-align: right'>brought to you by</h7>",
                unsafe_allow_html=True)

with logo:
    st.markdown('''<a href=https://www.linkedin.com/in/bourahima-coulibaly-6bb335218/> Extia Lille </a>''',
                unsafe_allow_html=True)
