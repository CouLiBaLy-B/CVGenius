import pytest
from unittest.mock import patch, MagicMock

import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
    )
)
from ui.home.render_home import render_home, process_cv_job_offer


@pytest.fixture
def mock_st():
    with patch('ui.home.st') as mock:
        yield mock


@pytest.fixture
def mock_hc():
    with patch('ui.home.hc') as mock:
        yield mock


@pytest.fixture
def mock_extract_text_from_pdf():
    with patch('ui.home.extract_text_from_pdf') as mock:
        mock.return_value = "Mocked CV content"
        yield mock


@pytest.fixture
def mock_generate_pdf():
    with patch('ui.home.generate_pdf') as mock:
        yield mock


@pytest.fixture
def mock_resume_generator():
    with patch('ui.home.ResumeGenerator') as mock:
        mock_instance = MagicMock()
        mock_instance.generator.return_value = "Generated content"
        mock.return_value = mock_instance
        yield mock


def test_render_home(mock_st, mock_hc):
    mock_hc.option_bar.return_value = "CV et offre d'emploi"

    render_home()

    mock_hc.option_bar.assert_called()
    mock_st.file_uploader.assert_called_with("Importez votre CV en pdf",
                                             type="pdf")
    mock_st.text_area.assert_called_with("L'offre de poste",
                                         value="", height=400,
                                         key="offre")


def test_process_cv_job_offer(
        mock_st,
        mock_extract_text_from_pdf,
        mock_generate_pdf,
        mock_resume_generator
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
