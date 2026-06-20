"""Tests des utilitaires de traitement de texte déterministes."""

from scr.scoring import text


def test_normalize_removes_accents_and_case():
    assert text.normalize("  Élève   Développeur  ") == "eleve developpeur"


def test_normalize_handles_empty():
    assert text.normalize("") == ""
    assert text.normalize(None) == ""  # type: ignore[arg-type]


def test_tokenize_filters_stopwords_and_keeps_tech_tokens():
    tokens = text.tokenize("Le développeur maîtrise C++ et CI/CD pour AWS")
    assert "developpeur" in tokens
    assert "c++" in tokens
    assert "ci/cd" in tokens
    assert "le" not in tokens  # mot vide retiré


def test_tokenize_can_keep_stopwords():
    tokens = text.tokenize("le code", remove_stopwords=False)
    assert "le" in tokens


def test_extract_keywords_orders_by_frequency():
    keywords = text.extract_keywords("python python django python django docker")
    assert keywords[0] == "python"
    assert keywords[1] == "django"


def test_coverage_detects_present_terms_case_insensitive():
    found = text.coverage(["python", "docker", "rust"], "Python et DOCKER au quotidien")
    assert found == ["docker", "python"]


def test_max_years_of_experience_extracts_maximum():
    assert text.max_years_of_experience("3 ans ici, puis 7 years ailleurs") == 7
    assert text.max_years_of_experience("aucune durée") == 0


def test_count_date_ranges():
    assert text.count_date_ranges("2016 - 2024 puis 2024 - présent") == 2
    assert text.count_date_ranges("rien") == 0


def test_detect_terms_for_seniority_and_education():
    assert "senior" in text.detect_terms("Lead senior", text.SENIORITY_TERMS)
    assert "master" in text.detect_terms("Titulaire d'un Master", text.EDUCATION_TERMS)
