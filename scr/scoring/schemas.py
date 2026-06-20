"""Schémas de données du moteur de scoring multi-critères.

Ce module définit, à l'aide de Pydantic v2, les structures de données
immuables et validées qui circulent dans le moteur de scoring :

- :class:`CriterionKey`   : identifiants stables des critères d'évaluation ;
- :class:`ScoreSource`    : provenance d'un sous-score (déterministe / LLM) ;
- :class:`ScoreBand`      : classe qualitative dérivée d'un score sur 100 ;
- :class:`CriterionScore` : résultat détaillé pour un critère ;
- :class:`ScoringWeights` : pondération normalisée des critères ;
- :class:`MatchScore`     : résultat global agrégé et explicable.

L'utilisation de modèles validés garantit que les résultats produits sont
reproductibles, sérialisables (JSON) et auto-documentés, ce qui constitue
le socle d'un outil R&H fiable et auditable.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class CriterionKey(str, Enum):
    """Identifiants stables des critères d'évaluation d'un appariement CV/poste."""

    SKILLS = "skills"
    SEMANTIC = "semantic"
    EXPERIENCE = "experience"
    SENIORITY = "seniority"
    EDUCATION = "education"
    QUALITATIVE = "qualitative"

    @property
    def label(self) -> str:
        """Libellé lisible (français) du critère, destiné à l'affichage."""
        return _CRITERION_LABELS[self]


_CRITERION_LABELS: Dict["CriterionKey", str] = {
    CriterionKey.SKILLS: "Adéquation des compétences",
    CriterionKey.SEMANTIC: "Similarité sémantique globale",
    CriterionKey.EXPERIENCE: "Expérience professionnelle",
    CriterionKey.SENIORITY: "Niveau de séniorité",
    CriterionKey.EDUCATION: "Formation et certifications",
    CriterionKey.QUALITATIVE: "Évaluation qualitative (LLM)",
}


class ScoreSource(str, Enum):
    """Provenance d'un sous-score, pour la traçabilité de l'évaluation."""

    DETERMINISTIC = "deterministic"
    LLM = "llm"
    HYBRID = "hybrid"


class ScoreBand(str, Enum):
    """Classe qualitative d'un score, utile pour le tri et la décision R&H."""

    EXCELLENT = "excellent"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    POOR = "poor"

    @classmethod
    def from_score(cls, score: float) -> "ScoreBand":
        """Convertit un score sur 100 en bande qualitative.

        Args:
            score: Score compris dans l'intervalle ``[0, 100]``.

        Returns:
            La bande qualitative correspondant aux seuils standards.
        """
        if score >= 85:
            return cls.EXCELLENT
        if score >= 70:
            return cls.STRONG
        if score >= 55:
            return cls.MODERATE
        if score >= 40:
            return cls.WEAK
        return cls.POOR

    @property
    def label(self) -> str:
        """Libellé français de la bande qualitative."""
        return {
            ScoreBand.EXCELLENT: "Excellente correspondance",
            ScoreBand.STRONG: "Bonne correspondance",
            ScoreBand.MODERATE: "Correspondance modérée",
            ScoreBand.WEAK: "Correspondance faible",
            ScoreBand.POOR: "Correspondance insuffisante",
        }[self]


class CriterionScore(BaseModel):
    """Résultat détaillé et explicable pour un critère d'évaluation."""

    model_config = {"frozen": True}

    key: CriterionKey
    score: float = Field(ge=0.0, le=100.0, description="Score du critère sur 100.")
    weight: float = Field(ge=0.0, le=1.0, description="Poids normalisé du critère.")
    source: ScoreSource = ScoreSource.DETERMINISTIC
    rationale: str = Field(default="", description="Explication synthétique du score.")
    evidence: List[str] = Field(
        default_factory=list,
        description="Éléments concrets justifiant le score (mots-clés, durées...).",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def label(self) -> str:
        """Libellé lisible du critère."""
        return self.key.label

    @computed_field  # type: ignore[prop-decorator]
    @property
    def weighted_contribution(self) -> float:
        """Contribution pondérée du critère au score global (``score * weight``)."""
        return round(self.score * self.weight, 2)


class ScoringWeights(BaseModel):
    """Pondération des critères, automatiquement normalisée à somme 1.

    Les poids peuvent être fournis de façon arbitraire (par exemple
    ``{"skills": 3, "experience": 2}``) : ils sont renormalisés afin que
    leur somme vaille 1, ce qui permet aux recruteurs d'ajuster l'importance
    relative des critères sans se soucier de l'échelle.
    """

    model_config = {"frozen": True}

    weights: Dict[CriterionKey, float]

    @field_validator("weights")
    @classmethod
    def _check_non_negative(
        cls, value: Dict[CriterionKey, float]
    ) -> Dict[CriterionKey, float]:
        if not value:
            raise ValueError("Au moins un critère pondéré est requis.")
        if any(weight < 0 for weight in value.values()):
            raise ValueError("Les poids ne peuvent pas être négatifs.")
        if sum(value.values()) <= 0:
            raise ValueError("La somme des poids doit être strictement positive.")
        return value

    @model_validator(mode="after")
    def _normalize(self) -> "ScoringWeights":
        total = sum(self.weights.values())
        normalized = {key: weight / total for key, weight in self.weights.items()}
        # ``frozen`` interdit l'affectation directe : on contourne via __dict__.
        object.__setattr__(self, "weights", normalized)
        return self

    def of(self, key: CriterionKey) -> float:
        """Retourne le poids normalisé d'un critère (0 s'il est absent)."""
        return self.weights.get(key, 0.0)

    def active_keys(self) -> List[CriterionKey]:
        """Liste des critères dont le poids est strictement positif."""
        return [key for key, weight in self.weights.items() if weight > 0]


class MatchScore(BaseModel):
    """Résultat global, agrégé et explicable, d'un appariement CV/poste."""

    model_config = {"frozen": True}

    global_score: float = Field(ge=0.0, le=100.0)
    band: ScoreBand
    criteria: List[CriterionScore]
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendation: str = ""
    metadata: Dict[str, str] = Field(default_factory=dict)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def band_label(self) -> str:
        """Libellé français de la bande qualitative globale."""
        return self.band.label

    def criterion(self, key: CriterionKey) -> CriterionScore | None:
        """Retourne le sous-score d'un critère donné, ou ``None`` s'il est absent."""
        return next((c for c in self.criteria if c.key == key), None)
