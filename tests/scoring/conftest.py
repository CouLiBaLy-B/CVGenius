"""Fixtures partagées pour les tests du moteur de scoring."""

import pytest


@pytest.fixture
def strong_resume() -> str:
    """CV d'un profil senior aligné sur l'offre de référence."""
    return (
        "Développeur Python senior avec 8 ans d'expérience. "
        "Maîtrise de Django, FastAPI, PostgreSQL, Docker et Kubernetes. "
        "Mise en place de pipelines CI/CD et de microservices sur AWS. "
        "Expérience 2016 - 2024 en tant que lead developer. "
        "Diplôme d'ingénieur, certification AWS."
    )


@pytest.fixture
def weak_resume() -> str:
    """CV d'un profil junior éloigné de l'offre de référence."""
    return (
        "Graphiste junior passionné de design. "
        "Maîtrise de Photoshop et Illustrator. "
        "Stage de 6 mois en agence de communication. Licence en arts appliqués."
    )


@pytest.fixture
def job_advert() -> str:
    """Offre d'emploi de référence pour un poste backend senior."""
    return (
        "Nous recherchons un développeur Python senior avec 5 ans d'expérience. "
        "Compétences requises : Django, FastAPI, PostgreSQL, Docker, Kubernetes, "
        "AWS et CI/CD. Diplôme d'ingénieur apprécié."
    )
