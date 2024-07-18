import streamlit as st
import hydralit_components as hc
from configuration.config import get_over_theme
from scr.utils import extract_text_from_pdf, generate_pdf
from scr.models import (
    ScoreResumeJob,
    CoverLetterGenerator,
    ResumeImprover,
    ResumeGenerator,
    MailCompletion
)


def render_home():
    option_data = [
        {"icon": "📝", "label": "CV et offre d'emploi"},
        {"icon": "📧", "label": "Completion de mail"},
    ]
    cv_mail_option = hc.option_bar(
        option_definition=option_data,
        title="Que voulez-vous faire ?",
        key="PrimaryOption_",
        override_theme=get_over_theme(),
        font_styling={"font-class": "h1",
                      "font-size": "100%",
                      "color": "black"},
        horizontal_orientation=True,
    )

    if cv_mail_option == "CV et offre d'emploi":
        render_cv_job_offer_options()
    elif cv_mail_option == "Completion de mail":
        render_mail_completion()


def render_cv_job_offer_options():
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
    job_advert = st.text_area("L'offre de poste",
                              value="", height=400, key="offre")

    if resume_pdf is None:
        st.error("Veuillez importer votre CV avant de continuer.")
    elif job_advert == "":
        st.error("""Veuillez saisir une description de poste
                 avant de continuer.""")
    else:
        if st.button("Lancer"):
            process_cv_job_offer(task, resume_pdf, job_advert)


def process_cv_job_offer(task, resume_pdf, job_advert):
    with st.spinner("Traitement en cours..."):
        resume = extract_text_from_pdf(resume_pdf)
        if task == "Score de correspondance":
            strategy = ScoreResumeJob()
        elif task == "Rédaction de lettre de motivation":
            strategy = CoverLetterGenerator()
        elif task == "Amélioration de CV":
            strategy = ResumeImprover()

        generator = ResumeGenerator(resume=resume,
                                    job_advert=job_advert,
                                    resumeStrategy=strategy)
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
