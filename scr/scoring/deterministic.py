"""Scoreurs déterministes par critère.

Chaque fonction de ce module évalue un critère précis de l'appariement
CV/offre et renvoie un :class:`CriterionScore`. Les calculs sont entièrement
déterministes (pas d'appel LLM ni réseau) : ils constituent le socle
reproductible et auditable du moteur de scoring.

Le poids transmis à chaque scoreur sert uniquement à enrichir le résultat
(``weight`` / ``weighted_contribution``) ; l'agrégation finale est réalisée
par le moteur.
"""

from __future__ import annotations

from typing import List

from scr.scoring import text
from scr.scoring.schemas import CriterionKey, CriterionScore, ScoreSource
from scr.scoring.similarity import SimilarityProvider, TfidfSimilarity


def _truncate(items: List[str], limit: int = 8) -> List[str]:
    """Limite une liste d'éléments de preuve pour garder un résultat lisible."""
    if len(items) <= limit:
        return items
    return items[:limit] + [f"(+{len(items) - limit} autres)"]


def score_skills(
    resume: str,
    job_advert: str,
    *,
    weight: float = 0.0,
    top_n: int = 40,
) -> CriterionScore:
    """Évalue la couverture des compétences/mots-clés exigés par l'offre.

    Les exigences sont extraites dynamiquement de l'offre (mots-clés les plus
    saillants), puis l'on mesure la proportion effectivement présente dans le
    CV. Cette approche « ATS » ne dépend d'aucun lexique figé.
    """
    required = text.extract_keywords(job_advert, top_n=top_n)
    if not required:
        return CriterionScore(
            key=CriterionKey.SKILLS,
            score=0.0,
            weight=weight,
            rationale="Aucune compétence exploitable n'a pu être extraite de l'offre.",
        )

    matched = text.coverage(required, resume)
    missing = sorted(set(required) - set(matched))
    score = 100.0 * len(matched) / len(required)
    rationale = (
        f"{len(matched)}/{len(required)} compétences clés de l'offre "
        f"sont présentes dans le CV."
    )
    evidence = [f"présentes : {', '.join(_truncate(matched))}"] if matched else []
    if missing:
        evidence.append(f"manquantes : {', '.join(_truncate(missing))}")
    return CriterionScore(
        key=CriterionKey.SKILLS,
        score=round(score, 2),
        weight=weight,
        source=ScoreSource.DETERMINISTIC,
        rationale=rationale,
        evidence=evidence,
    )


def score_semantic(
    resume: str,
    job_advert: str,
    *,
    weight: float = 0.0,
    provider: SimilarityProvider | None = None,
) -> CriterionScore:
    """Évalue la similarité sémantique globale entre le CV et l'offre."""
    provider = provider or TfidfSimilarity()
    similarity = provider.similarity(resume, job_advert)
    score = max(0.0, min(1.0, similarity)) * 100.0
    return CriterionScore(
        key=CriterionKey.SEMANTIC,
        score=round(score, 2),
        weight=weight,
        source=ScoreSource.DETERMINISTIC,
        rationale=(
            f"Similarité textuelle globale de {similarity:.2f} "
            f"(0 = aucun recouvrement, 1 = recouvrement total)."
        ),
    )


def score_experience(
    resume: str,
    job_advert: str,
    *,
    weight: float = 0.0,
) -> CriterionScore:
    """Évalue l'adéquation de l'expérience à l'exigence éventuelle de l'offre.

    - Si l'offre exprime une exigence d'années, le score reflète le ratio
      ancienneté du CV / exigence (plafonné à 100).
    - Sinon, on s'appuie sur des signaux de parcours (durées et intervalles
      de dates détectés dans le CV).
    """
    required_years = text.max_years_of_experience(job_advert)
    candidate_years = text.max_years_of_experience(resume)
    date_ranges = text.count_date_ranges(resume)

    if required_years > 0:
        ratio = candidate_years / required_years if candidate_years else 0.0
        score = max(0.0, min(1.0, ratio)) * 100.0
        rationale = (
            f"Le CV indique ~{candidate_years} an(s) d'expérience pour "
            f"{required_years} requis par l'offre."
        )
    else:
        signal = candidate_years + date_ranges
        score = min(1.0, signal / 5.0) * 100.0
        rationale = (
            "L'offre n'exprime pas d'exigence chiffrée ; le score s'appuie sur "
            f"~{candidate_years} an(s) et {date_ranges} période(s) détectées."
        )

    evidence = []
    if candidate_years:
        evidence.append(f"ancienneté détectée : {candidate_years} an(s)")
    if date_ranges:
        evidence.append(f"{date_ranges} période(s) professionnelle(s)")
    return CriterionScore(
        key=CriterionKey.EXPERIENCE,
        score=round(score, 2),
        weight=weight,
        source=ScoreSource.DETERMINISTIC,
        rationale=rationale,
        evidence=evidence,
    )


def score_seniority(
    resume: str,
    job_advert: str,
    *,
    weight: float = 0.0,
) -> CriterionScore:
    """Évalue l'alignement du niveau de séniorité entre le CV et l'offre."""
    required = set(text.detect_terms(job_advert, text.SENIORITY_TERMS))
    candidate = set(text.detect_terms(resume, text.SENIORITY_TERMS))

    if not required:
        score = 100.0 if candidate else 60.0
        rationale = (
            "L'offre ne précise pas de niveau ; séniorité du CV prise en compte "
            "de façon neutre."
        )
    else:
        overlap = required & candidate
        score = 100.0 * len(overlap) / len(required)
        rationale = (
            f"{len(overlap)}/{len(required)} marqueur(s) de séniorité de l'offre "
            f"retrouvé(s) dans le CV."
        )

    evidence = []
    if required:
        evidence.append(f"offre : {', '.join(sorted(required))}")
    if candidate:
        evidence.append(f"CV : {', '.join(sorted(candidate))}")
    return CriterionScore(
        key=CriterionKey.SENIORITY,
        score=round(score, 2),
        weight=weight,
        source=ScoreSource.DETERMINISTIC,
        rationale=rationale,
        evidence=evidence,
    )


def score_education(
    resume: str,
    job_advert: str,
    *,
    weight: float = 0.0,
) -> CriterionScore:
    """Évalue la présence de formations/certifications, alignée sur l'offre."""
    required = set(text.detect_terms(job_advert, text.EDUCATION_TERMS))
    candidate = set(text.detect_terms(resume, text.EDUCATION_TERMS))

    if not required:
        score = 100.0 if candidate else 50.0
        rationale = (
            "L'offre n'impose pas de formation ; présence de diplômes dans le CV "
            "valorisée de façon neutre."
        )
    else:
        overlap = required & candidate
        base = len(overlap) / len(required)
        # Une formation présente mais non explicitement requise reste un atout.
        bonus = 0.1 if (candidate - required) else 0.0
        score = min(1.0, base + bonus) * 100.0
        rationale = (
            f"{len(overlap)}/{len(required)} exigence(s) de formation de l'offre "
            f"couverte(s) par le CV."
        )

    evidence = []
    if candidate:
        evidence.append(f"CV : {', '.join(sorted(candidate))}")
    if required:
        evidence.append(f"offre : {', '.join(sorted(required))}")
    return CriterionScore(
        key=CriterionKey.EDUCATION,
        score=round(score, 2),
        weight=weight,
        source=ScoreSource.DETERMINISTIC,
        rationale=rationale,
        evidence=evidence,
    )
