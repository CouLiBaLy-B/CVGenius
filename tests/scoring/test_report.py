"""Tests de la mise en forme Markdown du résultat de scoring."""

from scr.scoring import MultiCriteriaScoringEngine, to_markdown


def test_to_markdown_contains_key_sections(strong_resume, job_advert):
    match = MultiCriteriaScoringEngine().score(strong_resume, job_advert)
    markdown = to_markdown(match)

    assert "# Rapport de correspondance CV / Offre" in markdown
    assert f"{match.global_score:.0f}/100" in markdown
    assert "## Détail par critère" in markdown
    # Chaque critère évalué apparaît dans le tableau de synthèse.
    for criterion in match.criteria:
        assert criterion.label in markdown


def test_to_markdown_lists_strengths_when_present(strong_resume, job_advert):
    match = MultiCriteriaScoringEngine().score(strong_resume, job_advert)
    markdown = to_markdown(match)
    if match.strengths:
        assert "## Points forts" in markdown
