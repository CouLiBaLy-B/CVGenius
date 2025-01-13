import streamlit as st


def render_infos():
    """
    Renders information about the application.

    This function displays various sections on a Streamlit page, including
    details about the AI model used by the application, the MixTraL-8x7B-Instruct-v0.1
    by MistralAI, and the tasks performed by the application, such as scoring 
    resume-job offer compatibility, generating cover letters, and improving resumes.
    """

    st.markdown("<div class='title'>À propos de cette application</div>",
                unsafe_allow_html=True)
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
