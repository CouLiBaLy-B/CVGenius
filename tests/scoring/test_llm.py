"""Tests de l'évaluation qualitative LLM (avec doublures, sans réseau)."""

from scr.scoring.llm import LLMQualitativeScorer
from scr.scoring.schemas import CriterionKey, ScoreSource


class _FakeLLM:
    """Doublure de LLM renvoyant une réponse prédéfinie."""

    def __init__(self, response: str):
        self._response = response

    def invoke(self, prompt: str) -> str:
        return self._response


class _BrokenLLM:
    def invoke(self, prompt: str) -> str:
        raise RuntimeError("appel impossible")


def test_parses_valid_json_response():
    response = (
        'Voici mon analyse : {"score": 82, "rationale": "Parcours cohérent", '
        '"strengths": ["leadership"], "weaknesses": ["anglais"]}'
    )
    scorer = LLMQualitativeScorer(_FakeLLM(response))
    result = scorer.score("cv", "offre", weight=0.2)
    assert result.key is CriterionKey.QUALITATIVE
    assert result.source is ScoreSource.LLM
    assert result.score == 82.0
    assert "force : leadership" in result.evidence
    assert "limite : anglais" in result.evidence


def test_clamps_out_of_range_score():
    scorer = LLMQualitativeScorer(_FakeLLM('{"score": 150}'))
    assert scorer.score("cv", "offre").score == 100.0


def test_returns_neutral_on_invalid_json():
    scorer = LLMQualitativeScorer(_FakeLLM("réponse sans json"))
    result = scorer.score("cv", "offre")
    assert result.score == 50.0
    assert "non exploitable" in result.rationale


def test_returns_neutral_on_llm_failure():
    scorer = LLMQualitativeScorer(_BrokenLLM())
    result = scorer.score("cv", "offre")
    assert result.score == 50.0
    assert "indisponible" in result.rationale
