"""Évaluation qualitative optionnelle par un grand modèle de langage (LLM).

Le moteur hybride fonctionne sans LLM (mode purement déterministe). Lorsqu'un
LLM est disponible, ce module ajoute une dimension qualitative — soft skills,
cohérence du parcours, éléments non capturés par les heuristiques — sous
forme de **sortie structurée** parsée de façon robuste.

L'interface :class:`LanguageModel` découple le moteur de toute bibliothèque
particulière. :class:`LangChainLLM` fournit un adaptateur prêt à l'emploi
pour les ``Runnable``/LLM LangChain déjà utilisés dans le projet.
"""

from __future__ import annotations

import json
import re
from typing import List, Protocol, runtime_checkable

from scr.scoring.schemas import CriterionKey, CriterionScore, ScoreSource


@runtime_checkable
class LanguageModel(Protocol):
    """Contrat minimal d'un LLM : transformer une invite en texte."""

    def invoke(self, prompt: str) -> str:  # pragma: no cover - protocole
        ...


class LangChainLLM:
    """Adaptateur exposant un ``Runnable``/LLM LangChain via :class:`LanguageModel`."""

    def __init__(self, runnable: object) -> None:
        self._runnable = runnable

    def invoke(self, prompt: str) -> str:
        result = self._runnable.invoke(prompt)  # type: ignore[attr-defined]
        # Les LLM de chat renvoient un message ; les LLM bruts une chaîne.
        return getattr(result, "content", result) if result is not None else ""


_PROMPT_TEMPLATE = """Tu es un expert en recrutement. Évalue qualitativement \
l'adéquation entre le CV et l'offre d'emploi ci-dessous.
Concentre-toi sur ce qu'une analyse par mots-clés ne capture pas : cohérence \
du parcours, soft skills, qualité des réalisations, signaux de progression.

Réponds STRICTEMENT par un objet JSON valide, sans texte autour, au format :
{{
  "score": <entier 0-100>,
  "rationale": "<explication concise en une à deux phrases>",
  "strengths": ["<point fort>", "..."],
  "weaknesses": ["<point faible>", "..."]
}}

CV :
{resume}

Offre d'emploi :
{job_advert}

JSON :"""


class LLMQualitativeScorer:
    """Produit un :class:`CriterionScore` qualitatif à partir d'un LLM."""

    def __init__(self, model: LanguageModel) -> None:
        self._model = model

    def score(
        self,
        resume: str,
        job_advert: str,
        *,
        weight: float = 0.0,
    ) -> CriterionScore:
        """Évalue qualitativement l'appariement ; tolère les sorties LLM imparfaites.

        En cas d'échec d'appel ou de réponse non exploitable, un score neutre
        explicite est renvoyé afin de ne jamais interrompre l'évaluation.
        """
        prompt = _PROMPT_TEMPLATE.format(resume=resume, job_advert=job_advert)
        try:
            raw = self._model.invoke(prompt)
        except Exception as exc:  # noqa: BLE001 - dégradation maîtrisée
            return self._neutral(
                weight, f"Évaluation LLM indisponible ({type(exc).__name__})."
            )

        parsed = self._parse(raw)
        if parsed is None:
            return self._neutral(
                weight, "Réponse du LLM non exploitable ; score neutre appliqué."
            )

        score, rationale, strengths, weaknesses = parsed
        evidence = [f"force : {item}" for item in strengths]
        evidence += [f"limite : {item}" for item in weaknesses]
        return CriterionScore(
            key=CriterionKey.QUALITATIVE,
            score=score,
            weight=weight,
            source=ScoreSource.LLM,
            rationale=rationale or "Évaluation qualitative produite par le LLM.",
            evidence=evidence,
        )

    @staticmethod
    def _neutral(weight: float, rationale: str) -> CriterionScore:
        return CriterionScore(
            key=CriterionKey.QUALITATIVE,
            score=50.0,
            weight=weight,
            source=ScoreSource.LLM,
            rationale=rationale,
        )

    @staticmethod
    def _parse(raw: str):
        """Extrait et valide l'objet JSON renvoyé par le LLM.

        Returns:
            Un quadruplet ``(score, rationale, strengths, weaknesses)`` ou
            ``None`` si la réponse n'est pas exploitable.
        """
        if not raw:
            return None
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(data, dict) or "score" not in data:
            return None
        try:
            score = float(data["score"])
        except (TypeError, ValueError):
            return None
        score = max(0.0, min(100.0, score))
        rationale = str(data.get("rationale", "")).strip()
        strengths = LLMQualitativeScorer._as_str_list(data.get("strengths"))
        weaknesses = LLMQualitativeScorer._as_str_list(data.get("weaknesses"))
        return score, rationale, strengths, weaknesses

    @staticmethod
    def _as_str_list(value: object) -> List[str]:
        """Normalise une valeur JSON en liste de chaînes non vides."""
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []
