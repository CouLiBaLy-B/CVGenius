"""Calcul de similarité textuelle, conçu pour être extensible.

La similarité sémantique entre un CV et une offre est exposée derrière une
interface (:class:`SimilarityProvider`). L'implémentation par défaut,
:class:`TfidfSimilarity`, repose uniquement sur la bibliothèque standard
(TF-IDF + similarité cosinus) : elle est déterministe, sans dépendance et
sans appel réseau.

Pour passer à une similarité par *embeddings* (sentence-transformers, API
d'embeddings...), il suffit d'implémenter :class:`SimilarityProvider` et de
l'injecter dans le moteur — aucun autre code n'a besoin d'être modifié.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import Counter
from typing import Dict, List

from scr.scoring.text import tokenize


class SimilarityProvider(ABC):
    """Interface d'un calculateur de similarité entre deux textes."""

    @abstractmethod
    def similarity(self, text_a: str, text_b: str) -> float:
        """Retourne une similarité dans l'intervalle ``[0.0, 1.0]``."""
        raise NotImplementedError


class TfidfSimilarity(SimilarityProvider):
    """Similarité cosinus sur vecteurs TF-IDF, implémentée en Python standard.

    Le corpus de référence se limite aux deux documents comparés, ce qui
    suffit à pondérer les termes communs par rapport aux termes spécifiques
    et fournit une mesure stable, explicable et reproductible.
    """

    def similarity(self, text_a: str, text_b: str) -> float:
        tokens_a = tokenize(text_a)
        tokens_b = tokenize(text_b)
        if not tokens_a or not tokens_b:
            return 0.0

        tf_a = self._term_frequencies(tokens_a)
        tf_b = self._term_frequencies(tokens_b)
        idf = self._inverse_document_frequencies([set(tf_a), set(tf_b)])

        vec_a = {term: freq * idf[term] for term, freq in tf_a.items()}
        vec_b = {term: freq * idf[term] for term, freq in tf_b.items()}
        return self._cosine(vec_a, vec_b)

    @staticmethod
    def _term_frequencies(tokens: List[str]) -> Dict[str, float]:
        """Fréquences relatives des termes d'un document."""
        counts = Counter(tokens)
        total = float(len(tokens))
        return {term: count / total for term, count in counts.items()}

    @staticmethod
    def _inverse_document_frequencies(
        documents: List[set],
    ) -> Dict[str, float]:
        """IDF lissé pour un petit corpus (les deux documents comparés)."""
        n_docs = len(documents)
        vocabulary = set().union(*documents) if documents else set()
        idf: Dict[str, float] = {}
        for term in vocabulary:
            containing = sum(1 for doc in documents if term in doc)
            idf[term] = math.log((1 + n_docs) / (1 + containing)) + 1.0
        return idf

    @staticmethod
    def _cosine(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        """Similarité cosinus entre deux vecteurs creux."""
        shared = set(vec_a) & set(vec_b)
        dot = sum(vec_a[term] * vec_b[term] for term in shared)
        norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
        norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)
