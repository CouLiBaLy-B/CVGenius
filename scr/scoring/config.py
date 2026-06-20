"""Pondérations par défaut du moteur de scoring multi-critères.

Les poids reflètent les priorités classiques d'une présélection R&H
(compétences et expérience en tête). Ils sont volontairement exposés ici
pour être ajustés sans toucher à la logique du moteur : un recruteur peut
fournir ses propres pondérations via :class:`~scr.scoring.schemas.ScoringWeights`.
"""

from __future__ import annotations

from typing import Dict

from scr.scoring.schemas import CriterionKey

# Poids relatifs (renormalisés à somme 1 par ``ScoringWeights``) lorsque le
# critère qualitatif LLM N'EST PAS utilisé.
DETERMINISTIC_WEIGHTS: Dict[CriterionKey, float] = {
    CriterionKey.SKILLS: 0.35,
    CriterionKey.EXPERIENCE: 0.25,
    CriterionKey.SEMANTIC: 0.18,
    CriterionKey.SENIORITY: 0.12,
    CriterionKey.EDUCATION: 0.10,
}

# Poids relatifs lorsque l'évaluation qualitative LLM EST disponible :
# une part est réallouée au jugement qualitatif.
HYBRID_WEIGHTS: Dict[CriterionKey, float] = {
    CriterionKey.SKILLS: 0.30,
    CriterionKey.EXPERIENCE: 0.22,
    CriterionKey.SEMANTIC: 0.13,
    CriterionKey.SENIORITY: 0.10,
    CriterionKey.EDUCATION: 0.08,
    CriterionKey.QUALITATIVE: 0.17,
}
