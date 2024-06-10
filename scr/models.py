from langchain_huggingface.llms import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

from requests.exceptions import HTTPError
import streamlit as st
from scr.utils import ModelError
from abc import ABC, abstractmethod


HUGGINGFACE_HUB_API_TOKEN = st.secrets["huggingface_api_key"]


class ResumeAIStrategy(ABC):

    def __init__(self):
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/MixTraL-8x7B-Instruct-v0.1",
            temperature=0.001,
            repetition_penalty=1.2,
            max_length=10000,
            max_new_tokens=2000,
            huggingfacehub_api_token=HUGGINGFACE_HUB_API_TOKEN,
            add_to_git_credential=True,
        )

    @abstractmethod
    def generate(self, resume: str, job_advert: str) -> str:
        pass


class ScoreResumeJob(ResumeAIStrategy):
    def __init__(self):
        super().__init__()

    def generate(self, resume: str, job_advert: str) -> str:
        prompt = """Évaluez la correspondance entre le CV d'un candidat et
        la description d'un poste en attribuant un score sur 100, en tenant
        compte des éléments suivants par ordre d'importance :

        1. La dernière expérience professionnelle et sa durée
        2. La deuxième expérience professionnelle et sa durée
        3. Vérifiez s'il y a des trous dans son parcours professionnel
        4. Le nom des formations, certifications et la renommée de l'université
        5. Les technologies
        6. Les projets
        7. La participation de manière bénévole à des actions humanitaires

        Doit tenir compte des informations sujaissantes, comme la maitrise
        d'un langage de programmation implique maitrise des librairies et
        des frameworks. Répondez selon le format suivant :

        Score de correspondance : [Score sur 100]
        * Principaux points forts : [Liste des principaux points forts
        du candidat]
        * Principaux points faibles : [Liste des principaux points faibles
        du candidat]

        Explication : [Paragraphe expliquant le score attribué, en
        détaillant les raisons des points forts et des points
        faibles identifiés]

        Exemple de réponse :
        Score de correspondance : 85/100
        * Principaux points forts :
        - Expérience pertinente de 5 ans dans un rôle similaire
        - Maîtrise des technologies clés mentionnées dans la description
        de poste
        - Formation universitaire en rapport avec le domaine

        * Principaux points faibles :
        - Manque d'expérience avec un outil spécifique mentionné dans
        la description de poste
        - Aucune certification professionnelle listée

        Explication : Le candidat semble très bien qualifié pour ce poste
        grâce à son expérience substantielle, ses compétences techniques et sa
        formation appropriée. Cependant, le manque d'expérience avec un outil
        spécifique et l'absence de certifications professionnelles pertinentes
        constituent des points faibles mineurs. Dans l'ensemble, le profil du
        candidat correspond très bien aux exigences de l'offre d'emploi.

        CV : {resume}
        Description du poste : {job_advert}
        Réponse :"""

        prompt_template = PromptTemplate(
            template=prompt, input_variables=["resume", "job_advert"]
        )
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume, "job_advert": job_advert})
        return result


class CoverLetterGenerator(ResumeAIStrategy):
    def __init__(self):
        super().__init__()

    def generate(self, resume: str, job_advert: str) -> str:
        prompt = """Générez une lettre de motivation professionnelle pour
        le poste décrit ci-dessous, en vous basant sur le CV fourni.

        La lettre de motivation doit comprendre les sections suivantes :

        1. Intro accrocheuse
        2. Vos expériences et compétences pertinentes pour le poste, en vous
        appuyant sur les informations du CV
           - Utilisez uniquement des termes techniques spécifiques au domaine
           présents dans la description du poste
           - Donnez des exemples concrets de vos réalisations passées
           mentionnées dans le CV ou non mais pertinent pouvant
           augmenter la concordance.
        3. Votre motivation pour le poste et l'entreprise
        4. Conclusion avec appel à l'action

        CV :
        {resume}

        Description du poste :
        {job_advert}

        Réponse :
        """
        prompt_template = PromptTemplate(
            template=prompt, input_variables=["resume", "job_advert"]
        )
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume, "job_advert": job_advert})
        return result.replace('`', '')


class ResumeImprover(ResumeAIStrategy):
    def __init__(self):
        super().__init__()

    def generate(self, resume: str, job_advert: str) -> str:
        prompt = f"""Améliorez le CV ci-dessous en intégrant les compétences,
        qualifications et expériences pertinentes à partir du CV fourni et
        de l'annonce d'emploi. L'objectif est d'atteindre un score de
        correspondance supérieur à 95%.

        Résumé : Présentez brièvement le candidat en mettant en avant ses
        principales forces et son adéquation avec le poste visé. Incorporez
        des mots-clés et phrases clés de l'offre d'emploi. Utiliser la
        première personne pour les conjugaisons.

        Compétences : Listez les compétences techniques et non techniques
        les plus pertinentes pour le poste en mettant en évidence celles
        mentionnées dans l'offre d'emploi. Classez-les par ordre d'importance.

        Expérience professionnelle : Réorganisez, combinez (max deux points)
        et reformulez les expériences pour mettre en avant les réalisations
        et responsabilités en lien avec le poste visé. Ajoutez des détails
        pertinents tirés de l'expérience élargie du candidat si disponibles.

        Formation et certifications : Mettez en avant les formations,
        diplômes et certifications en adéquation avec les exigences de
        l'offre d'emploi. Ajoutez toute information pertinente manquante.

        Projets : Reformulez et mettez en avant les projets en adéquation
        avec les exigences de l'offre d'emploi. Ajoutez des projets open
        source supplémentaires valorisants pour le poste si nécessaire.

        Informations supplémentaires : Ajoutez toute autre information
        valorisante pour le poste, comme les implications bénévoles,
        les récompenses, les publications, etc.

        Assurez-vous que toutes les modifications sont professionnelles,
        concises et positives. La structure du CV doit être cohérente
        et logique.

        Résumé : {resume}

        Offre d'emploi : {job_advert}

        Contexte supplémentaire : Le candidat a une vaste expérience en
        dehors de son historique d'emploi listé, qui pourrait être
        pertinente selon les exigences du poste. Veuillez en tenir
        compte lors des ajustements du CV.

        Réponse :"""

        prompt_template = PromptTemplate(
            template=prompt, input_variables=["resume", "job_advert"]
        )
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume, "job_advert": job_advert})
        return result


class ResumeGenerator:
    def __init__(self, resume: str,
                 job_advert: str,
                 resumeStrategy: ResumeAIStrategy):
        self.resume = resume
        self.job_advert = job_advert
        self.resumeStrategy = resumeStrategy

    def generator(self) -> str:
        try:
            generated_text = self.resumeStrategy.generate(
                resume=self.resume, job_advert=self.job_advert
            )
            return generated_text
        except TimeoutError:
            return """Le modèle a pris trop de temps pour répondre.
        Veuillez réessayer plus tard."""
        except ModelError as e:
            return f"""Une erreur s'est produite lors de l'appel
        au modèle : {str(e)}"""
        except HTTPError as http_err:
            if http_err.response.status_code == 500:
                request_id = http_err.response.headers.get("x-request-id",
                                                           "N/A")
                return f"""API problem: Internal Server Error
            (Request ID: {request_id})"""
            else:
                return f"HTTP error occurred: {http_err}"
        except Exception as e:
            return f"Une erreur inattendue s'est produite : {str(e)}"


class MailCompletion:
    def __init__(self):
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/MixTraL-8x7B-Instruct-v0.1",
            temperature=0.001,
            max_new_tokens=1000,
            huggingfacehub_api_token=HUGGINGFACE_HUB_API_TOKEN,
        )

    def mailcompletion(self, resume: str) -> str:
        prompt = """Complétez le modèle de courrier électronique ci-dessous en
        utilisant les informations contenues dans le CV fourni. Assurez-vous
        de remplacer les parties entre crochets [] par les informations
        pertinentes tirées du CV.

        Format de sortie :

        Bonjour,

        J'espère que vous allez bien ?

        Je me permets de vous proposer le profil de [Prénom du candidat],
        [Intitulé du poste] de [Nombre] année(s) d'expérience qui pourrait
        vivement intéresser votre équipe.

        Vous trouverez son dossier technique en pièce jointe.

        En quelques mots :
        - Technologies & Langages : [Liste des technologies et langages
        de programmation]
        - Compétences métiers : [Liste des compétences métiers pertinentes]
        - Dernier client : [Nom de l'entreprise de la dernière expérience]
        - Disponibilité : [Date de disponibilité s'il exsit sinon
        Immédiatement]

        Qu'en pensez-vous ? Je reste à votre disposition si le profil de
        [Prénom du candidat] est susceptible d'intéresser votre équipe ou
        celle de vos collègues.

        Excellente journée à vous,

        CV : {resume}

        Réponse :
        """
        prompt_template = PromptTemplate(template=prompt,
                                         input_variables=["resume"])
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume})
        return result
