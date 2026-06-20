"""Tests des scoreurs déterministes par critère."""

from scr.scoring import deterministic
from scr.scoring.schemas import CriterionKey


def test_skills_score_high_for_aligned_resume(strong_resume, job_advert):
    result = deterministic.score_skills(strong_resume, job_advert, weight=0.3)
    assert result.key is CriterionKey.SKILLS
    assert result.score > 50.0
    assert result.evidence


def test_skills_score_low_for_unaligned_resume(weak_resume, job_advert):
    result = deterministic.score_skills(weak_resume, job_advert)
    assert result.score < 30.0


def test_skills_score_zero_when_offer_empty(strong_resume):
    result = deterministic.score_skills(strong_resume, "")
    assert result.score == 0.0


def test_semantic_score_higher_for_aligned_resume(
    strong_resume, weak_resume, job_advert
):
    strong = deterministic.score_semantic(strong_resume, job_advert)
    weak = deterministic.score_semantic(weak_resume, job_advert)
    assert strong.score > weak.score


def test_experience_score_reflects_requirement(strong_resume, job_advert):
    result = deterministic.score_experience(strong_resume, job_advert)
    # 8 ans pour 5 requis -> ratio plafonné à 100.
    assert result.score == 100.0


def test_experience_score_low_when_insufficient(weak_resume, job_advert):
    result = deterministic.score_experience(weak_resume, job_advert)
    assert result.score < 50.0


def test_seniority_alignment(strong_resume, job_advert):
    result = deterministic.score_seniority(strong_resume, job_advert)
    assert result.key is CriterionKey.SENIORITY
    assert 0.0 <= result.score <= 100.0


def test_education_detects_requirement(strong_resume, job_advert):
    result = deterministic.score_education(strong_resume, job_advert)
    assert result.score > 0.0
    assert result.evidence
