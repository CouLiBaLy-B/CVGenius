"""Moteur de scoring multi-critères hybride (déterministe + LLM).

Le moteur orchestre les scoreurs par critère, agrège leurs sous-scores selon
une pondération normalisée et produit un :class:`MatchScore` global, explicable
et sérialisable.

Conception :
- **Hybride** : combine des critères déterministes (compétences, similarité,
  expérience, séniorité, formation) et un critère qualitatif LLM optionnel.
- **Dégradation maîtrisée** : sans LLM, le moteur fonctionne en mode purement
  déterministe avec une pondération adaptée.
- **Injection de dépendances** : le calculateur de similarité et le LLM sont
  injectables, ce qui rend le moteur testable et extensible (embeddings, etc.).
"""

from __future__ import annotations

from typing import List, Optional

from scr.scoring import deterministic
from scr.scoring.config import DETERMINISTIC_WEIGHTS, HYBRID_WEIGHTS
from scr.scoring.llm import LLMQualitativeScorer, LanguageModel
from scr.scoring.schemas import (
    CriterionKey,
    CriterionScore,
    MatchScore,
    ScoreBand,
    ScoringWeights,
)
from scr.scoring.similarity import SimilarityProvider, TfidfSimilarity

_STRONG_THRESHOLD = 70.0
_WEAK_THRESHOLD = 50.0


class MultiCriteriaScoringEngine:
    """Évalue l'adéquation d'un CV à une offre selon plusieurs critères pondérés."""

    def __init__(
        self,
        *,
        weights: Optional[ScoringWeights] = None,
        similarity_provider: Optional[SimilarityProvider] = None,
        language_model: Optional[LanguageModel] = None,
        skills_top_n: int = 40,
    ) -> None:
        """Initialise le moteur.

        Args:
            weights: Pondération des critères. Par défaut, une pondération
                adaptée à la présence (ou non) d'un LLM est appliquée.
            similarity_provider: Calculateur de similarité sémantique
                (TF-IDF par défaut ; un provider à embeddings peut être injecté).
            language_model: LLM optionnel activant l'évaluation qualitative.
            skills_top_n: Nombre de mots-clés extraits de l'offre pour le
                critère « compétences ».
        """
        self._similarity = similarity_provider or TfidfSimilarity()
        self._llm_scorer = (
            LLMQualitativeScorer(language_model) if language_model is not None else None
        )
        self._skills_top_n = skills_top_n
        self._weights = weights or self._default_weights()

    @property
    def weights(self) -> ScoringWeights:
        """Pondération effective (normalisée) utilisée par le moteur."""
        return self._weights

    def _default_weights(self) -> ScoringWeights:
        base = HYBRID_WEIGHTS if self._llm_scorer is not None else DETERMINISTIC_WEIGHTS
        return ScoringWeights(weights=dict(base))

    def score(self, resume: str, job_advert: str) -> MatchScore:
        """Calcule le score global multi-critères d'un appariement CV/offre.

        Args:
            resume: Texte du CV du candidat.
            job_advert: Texte de l'offre d'emploi.

        Returns:
            Un :class:`MatchScore` contenant le score global, sa bande
            qualitative, le détail par critère et une recommandation.

        Raises:
            ValueError: Si le CV ou l'offre est vide.
        """
        if not (resume and resume.strip()):
            raise ValueError("Le CV fourni est vide.")
        if not (job_advert and job_advert.strip()):
            raise ValueError("L'offre d'emploi fournie est vide.")

        criteria = self._evaluate_criteria(resume, job_advert)
        global_score = self._aggregate(criteria)
        band = ScoreBand.from_score(global_score)
        strengths, weaknesses = self._extract_highlights(criteria)
        return MatchScore(
            global_score=round(global_score, 2),
            band=band,
            criteria=criteria,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=self._recommendation(band),
            metadata={
                "mode": "hybride" if self._llm_scorer is not None else "déterministe",
                "criteria_count": str(len(criteria)),
            },
        )

    def _evaluate_criteria(
        self, resume: str, job_advert: str
    ) -> List[CriterionScore]:
        """Exécute chaque scoreur dont le critère a un poids strictement positif."""
        active = set(self._weights.active_keys())
        scores: List[CriterionScore] = []

        if CriterionKey.SKILLS in active:
            scores.append(
                deterministic.score_skills(
                    resume,
                    job_advert,
                    weight=self._weights.of(CriterionKey.SKILLS),
                    top_n=self._skills_top_n,
                )
            )
        if CriterionKey.SEMANTIC in active:
            scores.append(
                deterministic.score_semantic(
                    resume,
                    job_advert,
                    weight=self._weights.of(CriterionKey.SEMANTIC),
                    provider=self._similarity,
                )
            )
        if CriterionKey.EXPERIENCE in active:
            scores.append(
                deterministic.score_experience(
                    resume, job_advert, weight=self._weights.of(CriterionKey.EXPERIENCE)
                )
            )
        if CriterionKey.SENIORITY in active:
            scores.append(
                deterministic.score_seniority(
                    resume, job_advert, weight=self._weights.of(CriterionKey.SENIORITY)
                )
            )
        if CriterionKey.EDUCATION in active:
            scores.append(
                deterministic.score_education(
                    resume, job_advert, weight=self._weights.of(CriterionKey.EDUCATION)
                )
            )
        if CriterionKey.QUALITATIVE in active and self._llm_scorer is not None:
            scores.append(
                self._llm_scorer.score(
                    resume,
                    job_advert,
                    weight=self._weights.of(CriterionKey.QUALITATIVE),
                )
            )
        return scores

    @staticmethod
    def _aggregate(criteria: List[CriterionScore]) -> float:
        """Agrège les sous-scores en moyenne pondérée sur les poids effectifs.

        Les poids sont renormalisés sur les seuls critères réellement évalués,
        afin que l'absence d'un critère (ex. LLM désactivé) ne biaise pas le
        score global vers le bas.
        """
        total_weight = sum(c.weight for c in criteria)
        if total_weight <= 0:
            return 0.0
        return sum(c.score * c.weight for c in criteria) / total_weight

    @staticmethod
    def _extract_highlights(criteria: List[CriterionScore]):
        """Dérive les points forts/faibles à partir des sous-scores."""
        strengths = [
            f"{c.label} ({c.score:.0f}/100)"
            for c in sorted(criteria, key=lambda c: c.score, reverse=True)
            if c.score >= _STRONG_THRESHOLD
        ]
        weaknesses = [
            f"{c.label} ({c.score:.0f}/100)"
            for c in sorted(criteria, key=lambda c: c.score)
            if c.score < _WEAK_THRESHOLD
        ]
        return strengths, weaknesses

    @staticmethod
    def _recommendation(band: ScoreBand) -> str:
        """Recommandation R&H actionnable associée à la bande qualitative."""
        return {
            ScoreBand.EXCELLENT: "Profil hautement pertinent : à présenter en priorité.",
            ScoreBand.STRONG: "Bon profil : entretien recommandé.",
            ScoreBand.MODERATE: "Profil à approfondir : vérifier les écarts identifiés.",
            ScoreBand.WEAK: "Adéquation limitée : à considérer faute d'alternative.",
            ScoreBand.POOR: "Profil non aligné sur les exigences clés de l'offre.",
        }[band]
