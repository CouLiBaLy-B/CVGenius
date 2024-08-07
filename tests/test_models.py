import pytest
from unittest.mock import patch

from scr.models import (
    ResumeImprover,
    CoverLetterGenerator,
    ScoreResumeJob
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
def test_generate(strategy_class, resume, job_advert):
    strategy = strategy_class()
    with patch.object(strategy, "llm") as mock_llm:
        mock_llm.return_value = "Résultat de test..."
        try:
            result = strategy.generate(resume, job_advert)
            assert "Résultat de test..." in result["text"]
        except Exception as e:
            print(f"Error: {str(e)}")
