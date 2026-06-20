"""Mise en forme lisible d'un :class:`MatchScore`.

Centralise le rendu Markdown du résultat de scoring afin que l'interface
(affichage et export PDF) partage une présentation cohérente et testable.
"""

from __future__ import annotations

from scr.scoring.schemas import MatchScore


def to_markdown(match: MatchScore) -> str:
    """Restitue un rapport de scoring complet au format Markdown.

    Args:
        match: Résultat global d'un appariement CV/offre.

    Returns:
        Une chaîne Markdown prête à être affichée ou convertie en PDF.
    """
    lines = [
        "# Rapport de correspondance CV / Offre",
        "",
        f"## Score global : {match.global_score:.0f}/100 — {match.band_label}",
        "",
        f"*{match.recommendation}*",
        "",
        "## Détail par critère",
        "",
        "| Critère | Score | Poids | Contribution |",
        "| --- | ---: | ---: | ---: |",
    ]
    for criterion in match.criteria:
        lines.append(
            f"| {criterion.label} | {criterion.score:.0f}/100 "
            f"| {criterion.weight * 100:.0f}% "
            f"| {criterion.weighted_contribution:.1f} |"
        )

    for criterion in match.criteria:
        lines += ["", f"### {criterion.label} — {criterion.score:.0f}/100"]
        if criterion.rationale:
            lines.append(criterion.rationale)
        for item in criterion.evidence:
            lines.append(f"- {item}")

    if match.strengths:
        lines += ["", "## Points forts"]
        lines += [f"- {item}" for item in match.strengths]
    if match.weaknesses:
        lines += ["", "## Points de vigilance"]
        lines += [f"- {item}" for item in match.weaknesses]

    return "\n".join(lines)
