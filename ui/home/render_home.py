import streamlit as st
import hydralit_components as hc
from configuration.config import get_over_theme
from scr.utils import extract_text_from_pdf, generate_pdf
from scr.scoring import MatchScore, to_markdown
from scr.models import (
    create_scoring_engine,
    CoverLetterGenerator,
    ResumeImprover,
    ResumeGenerator,
    MailCompletion,
)

SCORE_TASK = "Score de correspondance"


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
        {"label": SCORE_TASK},
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

    use_llm = False
    if task == SCORE_TASK:
        use_llm = st.checkbox(
            "Ajouter une analyse qualitative par IA (plus lente, nécessite un jeton)",
            value=False,
            help=(
                "Le scoring multi-critères fonctionne sans IA. Cette option ajoute "
                "une évaluation qualitative du parcours et des soft skills."
            ),
        )

    if resume_pdf is None:
        st.error("Veuillez importer votre CV avant de continuer.")
    elif job_advert == "":
        st.error(
            """Veuillez saisir une description de poste
            avant de continuer."""
        )
    else:
        if st.button("Lancer"):
            process_cv_job_offer(task, resume_pdf, job_advert, use_llm=use_llm)


def process_cv_job_offer(task, resume_pdf, job_advert, use_llm=False):
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
    use_llm : bool, optional
        Whether to enrich the matching score with an LLM qualitative analysis,
        by default ``False``. Only relevant for the scoring task.

    Returns
    -------
    None
    """
    with st.spinner("Traitement en cours..."):
        resume = extract_text_from_pdf(resume_pdf)

        if task == SCORE_TASK:
            process_match_score(resume, job_advert, use_llm=use_llm)
            return

        strategy = (
            CoverLetterGenerator()
            if task == "Rédaction de lettre de motivation"
            else ResumeImprover()
        )
        generator = ResumeGenerator(
            resume=resume, job_advert=job_advert, resumeStrategy=strategy
        )
        generated = generator.generator()

        st.markdown(generated, unsafe_allow_html=True)
        pdf_output = generate_pdf(generated)
        st.download_button(
            label="Télécharger le document",
            data=pdf_output.getvalue(),
            file_name="document.pdf",
            mime="application/pdf",
        )
    st.success("Terminé !")


def process_match_score(resume, job_advert, use_llm=False):
    """
    Run the multi-criteria scoring engine and render its detailed result.

    Parameters
    ----------
    resume : str
        The extracted text of the candidate's resume.
    job_advert : str
        The job advert of the position.
    use_llm : bool, optional
        Whether to add the LLM qualitative criterion, by default ``False``.

    Returns
    -------
    None
    """
    try:
        engine = create_scoring_engine(use_llm=use_llm)
        match = engine.score(resume, job_advert)
    except ValueError as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001 - surfacing toute erreur à l'UI
        st.error(f"Une erreur est survenue pendant le scoring : {exc}")
        return

    render_match_score(match)
    pdf_output = generate_pdf(to_markdown(match))
    st.download_button(
        label="Télécharger le rapport de scoring",
        data=pdf_output.getvalue(),
        file_name="rapport_scoring.pdf",
        mime="application/pdf",
    )
    st.success("Terminé !")


def render_match_score(match: MatchScore):
    """
    Render a :class:`MatchScore` with global score, per-criterion gauges and
    highlights.

    Parameters
    ----------
    match : MatchScore
        The aggregated multi-criteria scoring result.

    Returns
    -------
    None
    """
    st.metric(
        label=f"Score global — {match.band_label}",
        value=f"{match.global_score:.0f}/100",
    )
    st.progress(min(1.0, match.global_score / 100.0))
    st.info(match.recommendation)

    st.subheader("Détail par critère")
    for criterion in match.criteria:
        st.markdown(
            f"**{criterion.label}** — {criterion.score:.0f}/100 "
            f"*(poids {criterion.weight * 100:.0f}%)*"
        )
        st.progress(min(1.0, criterion.score / 100.0))
        with st.expander("Justification"):
            if criterion.rationale:
                st.write(criterion.rationale)
            for item in criterion.evidence:
                st.markdown(f"- {item}")

    col_strengths, col_weaknesses = st.columns(2)
    with col_strengths:
        st.subheader("Points forts")
        for item in match.strengths or ["Aucun point fort marquant."]:
            st.markdown(f"- {item}")
    with col_weaknesses:
        st.subheader("Points de vigilance")
        for item in match.weaknesses or ["Aucun point de vigilance majeur."]:
            st.markdown(f"- {item}")


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
