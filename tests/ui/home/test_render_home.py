import pytest
from unittest.mock import patch, MagicMock

from ui.home.render_home import render_home, process_cv_job_offer, render_cv_job_offer_options


@pytest.fixture
def mock_st():
    with patch('ui.home.render_home.st') as mock:
        yield mock


@pytest.fixture
def mock_hc():
    with patch('ui.home.render_home.hc') as mock:
        yield mock


@pytest.fixture
def mock_extract_text_from_pdf():
    with patch('ui.home.render_home.extract_text_from_pdf') as mock:
        mock.return_value = "Mocked CV content"
        yield mock


@pytest.fixture
def mock_generate_pdf():
    with patch('ui.home.render_home.generate_pdf') as mock:
        yield mock


@pytest.fixture
def mock_resume_generator():
    with patch('ui.home.render_home.ResumeGenerator') as mock:
        mock_instance = MagicMock()
        mock_instance.generator.return_value = "Generated content"
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_huggingface_endpoint():
    # ScoreResumeJob/etc. construction performs a real network call to
    # validate the HF token unless HuggingFaceEndpoint itself is mocked out.
    with patch('scr.models.HuggingFaceEndpoint') as mock:
        yield mock


def test_render_home(mock_st, mock_hc):
    mock_hc.option_bar.return_value = "CV et offre d'emploi"
    mock_st.file_uploader.return_value = None  # Simulate no file uploaded
    mock_st.text_area.return_value = ""  # Simulate empty text area

    render_home()

    mock_hc.option_bar.assert_called()
    mock_st.file_uploader.assert_called_with("Importez votre CV en pdf",
                                             type="pdf")
    mock_st.text_area.assert_called_with("L'offre de poste", value="",
                                         height=400, key="offre")


def test_process_cv_job_offer(
        mock_st,
        mock_extract_text_from_pdf,
        mock_generate_pdf,
        mock_resume_generator,
        mock_huggingface_endpoint,
):
    mock_pdf = MagicMock()
    job_advert = "Job description"

    process_cv_job_offer("Score de correspondance", mock_pdf, job_advert)

    mock_extract_text_from_pdf.assert_called_with(mock_pdf)
    mock_resume_generator.assert_called()
    mock_st.markdown.assert_called_with("Generated content",
                                        unsafe_allow_html=True)
    mock_st.download_button.assert_called()
    mock_st.success.assert_called_with("Terminé !")


def test_process_cv_job_offer_handles_corrupt_pdf_without_crashing(
        mock_st,
        mock_generate_pdf,
        mock_resume_generator,
):
    with patch('ui.home.render_home.extract_text_from_pdf', side_effect=Exception("corrupt file")):
        with patch('ui.home.render_home.log_error') as mock_log_error:
            process_cv_job_offer("Score de correspondance", MagicMock(), "Job description")

            mock_log_error.assert_called_once()
            mock_st.error.assert_called_with(
                "Impossible de lire ce fichier PDF. Vérifiez qu'il n'est pas corrompu ou protégé."
            )
            mock_resume_generator.assert_not_called()


def test_render_cv_job_offer_options_rejects_unknown_task(mock_st, mock_hc):
    mock_hc.option_bar.return_value = None
    mock_st.file_uploader.return_value = MagicMock()
    mock_st.text_area.return_value = "Job description"
    mock_st.checkbox.return_value = True

    render_cv_job_offer_options()

    mock_st.error.assert_called_with("Veuillez sélectionner une tâche avant de continuer.")


def test_render_cv_job_offer_options_requires_consent(mock_st, mock_hc):
    mock_hc.option_bar.return_value = "Score de correspondance"
    mock_st.file_uploader.return_value = MagicMock()
    mock_st.text_area.return_value = "Job description"
    mock_st.checkbox.return_value = False

    render_cv_job_offer_options()

    mock_st.warning.assert_called_with(
        "Veuillez confirmer avoir pris connaissance de la mention ci-dessus avant de continuer."
    )
