"""Tests d'intégration du moteur de scoring multi-critères."""

import pytest

from scr.scoring import (
    CriterionKey,
    MatchScore,
    MultiCriteriaScoringEngine,
    ScoreBand,
    ScoringWeights,
)


class _FakeLLM:
    def invoke(self, prompt: str) -> str:
        return '{"score": 88, "rationale": "Profil solide", "strengths": ["autonomie"]}'


def test_engine_returns_match_score(strong_resume, job_advert):
    engine = MultiCriteriaScoringEngine()
    result = engine.score(strong_resume, job_advert)
    assert isinstance(result, MatchScore)
    assert 0.0 <= result.global_score <= 100.0
    assert result.metadata["mode"] == "déterministe"


def test_strong_resume_outscores_weak(strong_resume, weak_resume, job_advert):
    engine = MultiCriteriaScoringEngine()
    strong = engine.score(strong_resume, job_advert)
    weak = engine.score(weak_resume, job_advert)
    assert strong.global_score > weak.global_score
    assert strong.band in (ScoreBand.STRONG, ScoreBand.EXCELLENT, ScoreBand.MODERATE)


def test_deterministic_mode_excludes_qualitative(strong_resume, job_advert):
    engine = MultiCriteriaScoringEngine()
    result = engine.score(strong_resume, job_advert)
    assert result.criterion(CriterionKey.QUALITATIVE) is None
    assert result.criterion(CriterionKey.SKILLS) is not None


def test_hybrid_mode_includes_qualitative(strong_resume, job_advert):
    engine = MultiCriteriaScoringEngine(language_model=_FakeLLM())
    result = engine.score(strong_resume, job_advert)
    assert result.metadata["mode"] == "hybride"
    qualitative = result.criterion(CriterionKey.QUALITATIVE)
    assert qualitative is not None
    assert qualitative.score == 88.0


def test_engine_is_deterministic_across_runs(strong_resume, job_advert):
    engine = MultiCriteriaScoringEngine()
    first = engine.score(strong_resume, job_advert)
    second = engine.score(strong_resume, job_advert)
    assert first.global_score == second.global_score


def test_custom_weights_are_respected(strong_resume, job_advert):
    weights = ScoringWeights(weights={CriterionKey.SKILLS: 1.0})
    engine = MultiCriteriaScoringEngine(weights=weights)
    result = engine.score(strong_resume, job_advert)
    assert len(result.criteria) == 1
    assert result.criteria[0].key is CriterionKey.SKILLS
    assert result.global_score == result.criteria[0].score


def test_empty_inputs_raise(strong_resume):
    engine = MultiCriteriaScoringEngine()
    with pytest.raises(ValueError):
        engine.score("", "offre")
    with pytest.raises(ValueError):
        engine.score(strong_resume, "   ")


def test_highlights_are_populated(strong_resume, job_advert):
    engine = MultiCriteriaScoringEngine()
    result = engine.score(strong_resume, job_advert)
    assert result.strengths
    assert result.recommendation
