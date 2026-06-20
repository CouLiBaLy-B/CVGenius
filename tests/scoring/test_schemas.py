"""Tests des schémas Pydantic du moteur de scoring."""

import pytest
from pydantic import ValidationError

from scr.scoring.schemas import (
    CriterionKey,
    CriterionScore,
    ScoreBand,
    ScoringWeights,
)


def test_score_band_thresholds():
    assert ScoreBand.from_score(90) is ScoreBand.EXCELLENT
    assert ScoreBand.from_score(75) is ScoreBand.STRONG
    assert ScoreBand.from_score(60) is ScoreBand.MODERATE
    assert ScoreBand.from_score(45) is ScoreBand.WEAK
    assert ScoreBand.from_score(10) is ScoreBand.POOR


def test_criterion_score_computes_contribution_and_label():
    score = CriterionScore(key=CriterionKey.SKILLS, score=80.0, weight=0.5)
    assert score.weighted_contribution == 40.0
    assert score.label == CriterionKey.SKILLS.label


def test_criterion_score_rejects_out_of_range():
    with pytest.raises(ValidationError):
        CriterionScore(key=CriterionKey.SKILLS, score=120.0, weight=0.5)


def test_scoring_weights_are_normalized():
    weights = ScoringWeights(
        weights={CriterionKey.SKILLS: 3, CriterionKey.EXPERIENCE: 1}
    )
    assert weights.of(CriterionKey.SKILLS) == pytest.approx(0.75)
    assert weights.of(CriterionKey.EXPERIENCE) == pytest.approx(0.25)
    assert sum(weights.weights.values()) == pytest.approx(1.0)


def test_scoring_weights_reject_negative():
    with pytest.raises(ValidationError):
        ScoringWeights(weights={CriterionKey.SKILLS: -1})


def test_scoring_weights_reject_empty():
    with pytest.raises(ValidationError):
        ScoringWeights(weights={})


def test_active_keys_excludes_zero_weight():
    weights = ScoringWeights(
        weights={CriterionKey.SKILLS: 1, CriterionKey.EDUCATION: 0}
    )
    assert weights.active_keys() == [CriterionKey.SKILLS]
