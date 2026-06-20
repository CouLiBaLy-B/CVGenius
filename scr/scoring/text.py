"""Outils de traitement de texte déterministes pour le scoring.

Ce module ne dépend d'aucune bibliothèque externe : toutes les opérations
(normalisation, tokenisation, extraction de mots-clés, détection de durées
et de signaux de séniorité/formation) sont implémentées en Python standard.
Ce choix garantit des résultats parfaitement reproductibles et des tests
rapides, sans appel réseau ni modèle lourd.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Iterable, List, Set

# Mots vides français et anglais : un appariement CV/offre est fréquemment
# bilingue, on filtre donc les deux langues pour ne conserver que le signal.
STOPWORDS: Set[str] = {
    # Français
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "a", "au",
    "aux", "en", "dans", "pour", "par", "sur", "avec", "sans", "sous", "ce",
    "cet", "cette", "ces", "se", "sa", "son", "ses", "nos", "vos", "leur",
    "leurs", "qui", "que", "quoi", "dont", "ne", "pas", "plus", "est", "sont",
    "etre", "avoir", "fait", "faire", "vous", "nous", "ils", "elles", "il",
    "elle", "on", "nos", "notre", "votre", "tres", "tout", "tous", "toute",
    "comme", "afin", "ainsi", "donc", "mais", "car", "chez", "entre", "vers",
    "ans", "an", "annee", "annees", "experience", "poste", "candidat", "cv",
    # Anglais
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "without", "by", "as", "at", "is", "are", "be", "this", "that", "these",
    "those", "it", "we", "you", "they", "our", "your", "their", "from",
    "will", "shall", "can", "should", "must", "have", "has", "had", "not",
    "year", "years", "experience", "job", "role", "candidate", "resume",
}

_TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9+.#/-]*")
_SENTENCE_RE = re.compile(r"[.!?\n]+")

# Détection des durées d'expérience exprimées en années.
_YEARS_RE = re.compile(
    r"(\d{1,2})(?:\s*[-à]\s*\d{1,2})?\s*(?:\+?\s*)?(?:ans?|years?|yrs?)",
    re.IGNORECASE,
)
# Intervalles de dates type « 2019 - 2023 » ou « 2019 - présent ».
_DATE_RANGE_RE = re.compile(
    r"(19|20)\d{2}\s*[-–/]\s*((19|20)\d{2}|present|présent|aujourd|now|today)",
    re.IGNORECASE,
)

SENIORITY_TERMS: Set[str] = {
    "junior", "stage", "stagiaire", "intern", "internship", "alternance",
    "debutant", "confirme", "senior", "lead", "principal", "staff", "expert",
    "manager", "directeur", "director", "head", "chief", "architecte",
    "architect",
}

EDUCATION_TERMS: Set[str] = {
    "licence", "master", "doctorat", "phd", "bachelor", "msc", "bsc", "mba",
    "ingenieur", "ingénieur", "engineer", "diplome", "diplôme", "degree",
    "universite", "université", "university", "ecole", "école", "school",
    "certification", "certifie", "certified", "bac", "dut", "bts", "formation",
}


def strip_accents(text: str) -> str:
    """Supprime les accents d'une chaîne (``é`` -> ``e``) pour comparer sans diacritiques."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize(text: str) -> str:
    """Met un texte en minuscules, sans accents ni espaces superflus.

    Args:
        text: Texte brut éventuellement vide ou ``None``-équivalent.

    Returns:
        Texte normalisé, prêt pour la tokenisation et la comparaison.
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", strip_accents(text).lower()).strip()


def tokenize(text: str, *, remove_stopwords: bool = True) -> List[str]:
    """Découpe un texte en tokens alphanumériques (conserve ``c++``, ``ci/cd``...).

    Args:
        text: Texte à tokeniser.
        remove_stopwords: Si ``True``, retire les mots vides FR/EN.

    Returns:
        Liste ordonnée de tokens normalisés.
    """
    tokens = _TOKEN_RE.findall(normalize(text))
    if remove_stopwords:
        tokens = [tok for tok in tokens if tok not in STOPWORDS and len(tok) > 1]
    return tokens


def sentences(text: str) -> List[str]:
    """Découpe un texte en phrases non vides."""
    return [s.strip() for s in _SENTENCE_RE.split(text or "") if s.strip()]


def keyword_frequencies(text: str) -> Counter:
    """Retourne le compteur de fréquences des tokens signifiants d'un texte."""
    return Counter(tokenize(text))


def extract_keywords(text: str, *, top_n: int = 40) -> List[str]:
    """Extrait les mots-clés les plus saillants d'un texte (ex. une offre d'emploi).

    Les mots-clés sont les tokens signifiants les plus fréquents. Cette
    extraction dynamique évite tout lexique figé : ce sont les exigences
    réelles de l'offre qui définissent les attentes.

    Args:
        text: Texte source (typiquement la description de poste).
        top_n: Nombre maximum de mots-clés retournés.

    Returns:
        Mots-clés triés par fréquence décroissante puis ordre alphabétique.
    """
    counts = keyword_frequencies(text)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ordered[:top_n]]


def coverage(required: Iterable[str], present_in: str) -> List[str]:
    """Retourne les éléments ``required`` effectivement présents dans un texte.

    La comparaison se fait sur l'ensemble des tokens du texte cible, ce qui
    rend la détection insensible à l'ordre et à la casse.

    Args:
        required: Termes attendus (mots-clés de l'offre).
        present_in: Texte dans lequel chercher les termes (le CV).

    Returns:
        Sous-ensemble trié de ``required`` présent dans ``present_in``.
    """
    haystack = set(tokenize(present_in, remove_stopwords=False))
    found = {term for term in required if normalize(term) in haystack}
    return sorted(found)


def max_years_of_experience(text: str) -> int:
    """Estime le nombre maximal d'années d'expérience mentionné dans un texte.

    On retient le maximum des durées exprimées explicitement (« 5 ans »,
    « 7 years ») afin d'approcher l'exigence d'une offre ou l'ancienneté
    revendiquée dans un CV.

    Args:
        text: Texte à analyser.

    Returns:
        Nombre d'années détecté, ou ``0`` si aucune mention n'est trouvée.
    """
    values = [int(match) for match in _YEARS_RE.findall(text or "")]
    return max(values) if values else 0


def count_date_ranges(text: str) -> int:
    """Compte les intervalles de dates (ex. « 2019 - 2023 »), proxy d'un parcours."""
    return len(_DATE_RANGE_RE.findall(text or ""))


def detect_terms(text: str, vocabulary: Set[str]) -> List[str]:
    """Retourne les termes d'un vocabulaire présents dans un texte (sans accents)."""
    tokens = set(tokenize(text, remove_stopwords=False))
    normalized_vocab = {normalize(term) for term in vocabulary}
    return sorted(tokens & normalized_vocab)
