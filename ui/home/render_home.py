import streamlit as st
import hydralit_components as hc
from configuration.config import get_over_theme
from scr.utils import extract_text_from_pdf, generate_pdf
from scr.logs import log_action, log_error
from scr.models import (
    ScoreResumeJob,
    CoverLetterGenerator,
    ResumeImprover,
    ResumeGenerator,
    MailCompletion,
)

TASK_STRATEGIES = {
    "Score de correspondance": ScoreResumeJob,
    "Rédaction de lettre de motivation": CoverLetterGenerator,
    "Amélioration de CV": ResumeImprover,
}

CONSENT_NOTICE = (
    "Le CV importé (données personnelles du candidat) est transmis à un "
    "prestataire d'IA tiers (Hugging Face / Mistral) pour traitement. Il "
    "n'est conservé ni sur le serveur ni après la fin de votre session. "
    "Assurez-vous d'être autorisé à traiter ce document."
)


def render_home():
    """
    Renders the options for CV and job offer related tasks or for mail completion.

    This function renders a navigation bar with the following options:

    - CV et offre d'emploi
    - Completion de mail

    The selected option is stored in the `cv_mail_option` variable.

    If the user selects "CV et offre d'emploi", the `render_cv_job_offer_options` function will be called.

    If the user selects "Completion de mail", the `render_mail_completion` function will be called.

    :return: None
    """
    option_data = [
        {"icon": "📝", "label": "CV et offre d'emploi"},
        {"icon": "📧", "label": "Completion de mail"},
    ]
    cv_mail_option = hc.option_bar(
        option_definition=option_data,
        title="Que voulez-vous faire ?",
        key="PrimaryOption_",
        override_theme=get_over_theme(),
        font_styling={"font-class": "h1", "font-size": "100%", "color": "black"},
        horizontal_orientation=True,
    )

    if cv_mail_option == "CV et offre d'emploi":
        render_cv_job_offer_options()
    elif cv_mail_option == "Completion de mail":
        render_mail_completion()


def render_cv_job_offer_options():
    """
    Renders the options for CV and job offer related tasks.

    This function renders a navigation bar with the following options:

    - Score de correspondance
    - Rédaction de lettre de motivation
    - Amélioration de CV

    The selected option is stored in the `task` variable.

    Additionally, this function renders a file uploader for the user's CV and
    a text area for the job description. The user must upload a PDF file and
    fill in the job description before the task can be launched.

    If the user has not uploaded a PDF file or has not filled in the job
    description, an error message will be displayed.

    If the user clicks the "Lancer" button, the `process_cv_job_offer` function
    will be called with the selected task, the uploaded PDF file and the job
    description as arguments.
    """
    option_data = [
        {"label": "Score de correspondance"},
        {"label": "Rédaction de lettre de motivation"},
        {"label": "Amélioration de CV"},
    ]

    task = hc.option_bar(
        option_definition=option_data,
        title="Que voulez-vous faire ?",
        key="PrimaryOption1",
        override_theme=get_over_theme(),
        font_styling={"font-class": "h2", "font-size": "100%"},
        horizontal_orientation=True,
    )

    resume_pdf = st.file_uploader("Importez votre CV en pdf", type="pdf")
    job_advert = st.text_area("L'offre de poste", value="", height=400, key="offre")
    consent = st.checkbox(CONSENT_NOTICE, key="consent_cv_job_offer")

    if resume_pdf is None:
        st.error("Veuillez importer votre CV avant de continuer.")
    elif job_advert == "":
        st.error(
            """Veuillez saisir une description de poste
            avant de continuer."""
        )
    elif task not in TASK_STRATEGIES:
        st.error("Veuillez sélectionner une tâche avant de continuer.")
    elif not consent:
        st.warning("Veuillez confirmer avoir pris connaissance de la mention ci-dessus avant de continuer.")
    else:
        if st.button("Lancer"):
            process_cv_job_offer(task, resume_pdf, job_advert)


def process_cv_job_offer(task, resume_pdf, job_advert):
    """
    Process the selected task with the given resume and job advert.

    Parameters
    ----------
    task : str
        The selected task to perform, either "Score de correspondance", "Rédaction de lettre de motivation" or
        "Amélioration de CV".
    resume_pdf : bytes
        The resume of the candidate, as a PDF file.
    job_advert : str
        The job advert of the position.

    Returns
    -------
    None
    """
    with st.spinner("Traitement en cours..."):
        try:
            resume = extract_text_from_pdf(resume_pdf)
        except Exception as e:
            log_error("pdf_extraction_failed", e)
            st.error("Impossible de lire ce fichier PDF. Vérifiez qu'il n'est pas corrompu ou protégé.")
            return

        strategy = TASK_STRATEGIES[task]()
        log_action(f"process_cv:{task}")

        generator = ResumeGenerator(
            resume=resume, job_advert=job_advert, resumeStrategy=strategy
        )
        generated = generator.generator()

        st.markdown(generated, unsafe_allow_html=True)
        pdf_output = generate_pdf(generated)
        st.download_button(
            label=f"""Télécharger le
            {'résultat' if task == 'Score de correspondance'
            else 'document'}""",
            data=pdf_output.getvalue(),
            file_name=f"""{'matching_score'
                        if task == 'Score de correspondance'
                        else 'document'}.pdf""",
            mime="application/pdf",
        )
    st.success("Terminé !")


def render_mail_completion():
    """
    Displays a file uploader to import a resume in PDF format and
    a button to generate a mail completion.

    If the button is clicked, it will use the MailCompletion class to generate
    a mail completion and display it in a text area. It will also generate a PDF
    file from the text and allow the user to download it.

    If an error occurs during the generation of the mail completion, it will
    display an error message with the exception message.
    """
    resume_pdf = st.file_uploader("Import ton CV en pdf", type="pdf", key="mail_resume")
    consent = st.checkbox(CONSENT_NOTICE, key="consent_mail_completion")
    if resume_pdf is not None:
        if not consent:
            st.warning("Veuillez confirmer avoir pris connaissance de la mention ci-dessus avant de continuer.")
            return
        try:
            if st.button("Lancer", key="mail"):
                with st.spinner("Wait for it..."):
                    resume = extract_text_from_pdf(resume_pdf)
                    log_action("mail_completion")
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
            log_error("mail_completion_failed", e)
            st.error("Une erreur s'est produite lors de la génération du mail. Veuillez réessayer plus tard.")
