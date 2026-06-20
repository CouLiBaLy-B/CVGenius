"""Tests du calcul de similarité TF-IDF."""

from scr.scoring.similarity import TfidfSimilarity


def test_identical_texts_have_high_similarity():
    provider = TfidfSimilarity()
    text = "Développeur Python Django Docker Kubernetes"
    assert provider.similarity(text, text) > 0.99


def test_disjoint_texts_have_zero_similarity():
    provider = TfidfSimilarity()
    assert provider.similarity("python django docker", "cuisine peinture jardin") == 0.0


def test_partial_overlap_is_between_bounds():
    provider = TfidfSimilarity()
    score = provider.similarity(
        "python django docker kubernetes",
        "python flask docker",
    )
    assert 0.0 < score < 1.0


def test_empty_text_returns_zero():
    provider = TfidfSimilarity()
    assert provider.similarity("", "python") == 0.0
    assert provider.similarity("python", "") == 0.0


def test_similarity_is_symmetric():
    provider = TfidfSimilarity()
    a, b = "python docker aws", "docker python azure"
    assert provider.similarity(a, b) == provider.similarity(b, a)
