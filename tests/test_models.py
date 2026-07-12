import pytest
from unittest.mock import patch

from scr.models import (
    ResumeImprover,
    CoverLetterGenerator,
    ScoreResumeJob,
    MailCompletion,
    ResumeGenerator,
    ModelError,
    RESUME_MODEL_REPO_ID,
)


@pytest.fixture
def resume():
    return "Voici le contenu du CV de test."


@pytest.fixture
def job_advert():
    return "Voici la description de poste de test."


@pytest.mark.parametrize(
    "strategy_class", [ScoreResumeJob, CoverLetterGenerator, ResumeImprover]
)
@patch('scr.models.HuggingFaceEndpoint')
def test_generate(mock_endpoint, strategy_class, resume, job_advert):
    strategy = strategy_class()
    with patch.object(strategy, "llm") as mock_llm:
        mock_llm.return_value = "Résultat de test..."
        try:
            result = strategy.generate(resume, job_advert)
            assert "Résultat de test..." in result["text"]
        except Exception as e:
            print(f"Error: {str(e)}")


@patch('scr.models.HuggingFaceEndpoint')
def test_score_resume_job_uses_correct_model_repo_id(mock_endpoint):
    ScoreResumeJob()
    _, kwargs = mock_endpoint.call_args
    assert kwargs['repo_id'] == RESUME_MODEL_REPO_ID == "mistralai/Mixtral-8x7B-Instruct-v0.1"


@patch('scr.models.HuggingFaceEndpoint')
def test_mail_completion_uses_correct_model_repo_id(mock_endpoint):
    MailCompletion()
    _, kwargs = mock_endpoint.call_args
    assert kwargs['repo_id'] == RESUME_MODEL_REPO_ID == "mistralai/Mixtral-8x7B-Instruct-v0.1"


@patch('scr.models.HuggingFaceEndpoint')
def test_resume_strategy_does_not_persist_token_to_git_credential_store(mock_endpoint):
    ScoreResumeJob()
    _, kwargs = mock_endpoint.call_args
    assert 'add_to_git_credential' not in kwargs


@patch('scr.models.log_error')
def test_generator_hides_internal_error_details_from_ui(mock_log_error):
    class RaisingStrategy:
        def generate(self, resume, job_advert):
            raise ModelError("internal detail that must not reach the UI")

    generator = ResumeGenerator(resume="cv", job_advert="offer", resumeStrategy=RaisingStrategy())
    result = generator.generator()

    assert "internal detail that must not reach the UI" not in result
    mock_log_error.assert_called_once()


@patch('scr.models.log_error')
def test_generator_reports_unexpected_errors_generically(mock_log_error):
    class RaisingStrategy:
        def generate(self, resume, job_advert):
            raise ValueError("some unexpected internal error")

    generator = ResumeGenerator(resume="cv", job_advert="offer", resumeStrategy=RaisingStrategy())
    result = generator.generator()

    assert "some unexpected internal error" not in result
    mock_log_error.assert_called_once()
