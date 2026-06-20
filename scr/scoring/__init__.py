"""Moteur de scoring multi-critères hybride de CVGenius.

Point d'entrée public du sous-paquet : il regroupe le moteur, les schémas de
résultats et les briques extensibles (similarité, LLM) afin d'offrir une API
stable et lisible aux couches applicatives (UI, services, tests).

Exemple :
    >>> from scr.scoring import MultiCriteriaScoringEngine
    >>> engine = MultiCriteriaScoringEngine()
    >>> result = engine.score(resume_text, job_advert_text)
    >>> result.global_score, result.band_label
"""

from scr.scoring.engine import MultiCriteriaScoringEngine
from scr.scoring.llm import LangChainLLM, LanguageModel, LLMQualitativeScorer
from scr.scoring.report import to_markdown
from scr.scoring.schemas import (
    CriterionKey,
    CriterionScore,
    MatchScore,
    ScoreBand,
    ScoreSource,
    ScoringWeights,
)
from scr.scoring.similarity import SimilarityProvider, TfidfSimilarity

__all__ = [
    "MultiCriteriaScoringEngine",
    "CriterionKey",
    "CriterionScore",
    "MatchScore",
    "ScoreBand",
    "ScoreSource",
    "ScoringWeights",
    "SimilarityProvider",
    "TfidfSimilarity",
    "LanguageModel",
    "LangChainLLM",
    "LLMQualitativeScorer",
    "to_markdown",
]
