from langchain_huggingface.llms import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

from requests.exceptions import HTTPError
from scr.utils import ModelError
from abc import ABC, abstractmethod

from dotenv import load_dotenv
import os
load_dotenv()


HUGGINGFACE_HUB_API_TOKEN = os.getenv("HUGGINGFACE_HUB_API_TOKEN")


class ResumeAIStrategy(ABC):

    def __init__(self):
        """
        Initializes the ResumeAIStrategy class with a HuggingFaceEndpoint.

        This constructor sets up a connection to the Hugging Face API using the specified model
        repository. It configures the endpoint with parameters such as temperature, repetition penalty,
        max length, max new tokens, and adds the Hugging Face Hub API token for authentication.
        """

        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0.001,
            repetition_penalty=1.2,
            max_length=10000,
            max_new_tokens=2000,
            huggingfacehub_api_token=HUGGINGFACE_HUB_API_TOKEN,
            add_to_git_credential=True,
        )

    @abstractmethod
    def generate(self, resume: str, job_advert: str) -> str:
        """
        Abstract method to be implemented by all concrete strategies.

        This method should generate a document based on the given resume and job advert.
        The generated document should be a string that represents the output of the strategy.

        Parameters
        ----------
        resume : str
            The resume of the candidate.
        job_advert : str
            The job advert of the position.

        Returns
        -------
        str
            The generated document.
        """
        pass


class ScoreResumeJob(ResumeAIStrategy):
    def __init__(self):
        """
        Initializes the ScoreResumeJob class by calling the superclass initializer.

        This constructor sets up the ScoreResumeJob strategy, which evaluates
        the match between a candidate's resume and a job description.
        """

        super().__init__()

    def generate(self, resume: str, job_advert: str) -> str:
        """
        Evaluates the match between a candidate's resume and a job description by attributing a score on 100.

        Parameters
        ----------
        resume : str
            The resume of the candidate.
        job_advert : str
            The job advert of the position.

        Returns
        -------
        str
            The generated document.
        """
        prompt = """
        Évaluez la correspondance entre le CV d'un candidat et la description du poste en attribuant un score sur 100.
        Tenez compte des éléments suivants par ordre d'importance :
        1. Dernière expérience professionnelle et sa durée
        2. Deuxième expérience professionnelle et sa durée
        3. Présence de lacunes dans le parcours professionnel
        4. Formations, certifications et renommée des institutions
        5. Technologies maîtrisées
        6. Projets réalisés
        7. Engagement dans des actions humanitaires (optionel)

        Notez que la maîtrise d'un langage de programmation implique la connaissance des librairies et frameworks
        associés.
        Répondez au format suivant :

        - Score de correspondance : [Score sur 100]
        - Points forts : [Liste des principaux points forts du candidat]
        - Points faibles : [Liste des principaux points faibles du candidat]
        - Explication : [Paragraphe expliquant le score, les points forts et faibles]

        Exemple :
        Score de correspondance : 85/100
        Points forts :
        - Expérience de 5 ans dans un rôle similaire
        - Maîtrise des technologies requises
        - Formation pertinente

        Points faibles :
        - Manque d'expérience avec un outil spécifique
        - Absence de certifications professionnelles

        Explication : Le candidat est bien qualifié avec une solide expérience et des compétences pertinentes, bien que
        quelques domaines nécessitent des améliorations.

        CV : {resume}
        Description du poste : {job_advert}
        Réponse :
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=["resume", "job_advert"])
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume, "job_advert": job_advert})
        return result


class CoverLetterGenerator(ResumeAIStrategy):
    def __init__(self):
        """
        Initializes the CoverLetterGenerator class by calling the superclass initializer.
        This constructor sets up the CoverLetterGenerator strategy, which generates
        a professional cover letter based on the given resume and job advert.
        """

        super().__init__()

    def generate(self, resume: str, job_advert: str) -> str:
        prompt = """
        Générez une lettre de motivation professionnelle pour le poste décrit ci-dessous, en vous basant sur le CV
        fourni.
        La lettre doit inclure les éléments suivants :

        1. Introduction accrocheuse :
           - Présentation du candidat et de son intérêt pour le poste.
           - Mention de l'entreprise et de ses valeurs.

        2. Expériences et compétences pertinentes :
           - Description des expériences passées avec des exemples concrets de réalisations.
           - Compétences spécifiques et comment elles s'appliquent au poste.

        3. Motivation pour le poste et l'entreprise :
           - Pourquoi le candidat est-il intéressé par ce poste particulier.
           - Comment les valeurs et la mission de l'entreprise résonnent avec le candidat.

        4. Conclusion et appel à l'action :
           - Résumé des points clés de la lettre.
           - Invitation à un entretien et remerciements.

        CV : {resume}
        Description du poste : {job_advert}

        Réponse :
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=["resume", "job_advert"])
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume, "job_advert": job_advert})
        return result.replace('`', '')


class ResumeImprover(ResumeAIStrategy):
    def __init__(self):
        """Initializes the ResumeImprover class by calling the superclass initializer.

        This constructor sets up the ResumeImprover strategy, which improves
        a resume by highlighting the skills, qualifications and experiences
        relevant to a given job advert. It attempts to obtain a score of
        95% or higher. The generated resume includes a summary, skills
        and professional experience sections."""
        super().__init__()

    def generate(self, resume: str, job_advert: str) -> str:
        prompt = """
        Améliorez le CV ci-dessous en mettant en avant les compétences, qualifications et expériences pertinentes
        pour le poste.
        L'objectif est d'obtenir un score de correspondance supérieur à 95%.
        - Résumé : Présentez brièvement le candidat en mettant en avant ses forces principales et sa pertinence pour
        le poste, en utilisant des mots-clés de l'offre.
        - Compétences : Listez les compétences les plus pertinentes pour le poste, en mettant en avant celles
        mentionnées dans l'offre d'emploi.
        - Expérience professionnelle : Réorganisez et reformulez les expériences pour souligner les réalisations
        pertinentes pour le poste. Combinez les points si nécessaire.
        - Formation et certifications : Mettez en avant les formations et certifications pertinentes, ajoutant des
        informations manquantes si nécessaire.
        - Projets : Reformulez et mettez en avant les projets pertinents, incluant des projets open source valorisants
        si nécessaire.
        - Informations supplémentaires : Ajoutez toute information valorisante comme les implications bénévoles,
        récompenses, publications, etc.

        CV : {resume}
        Offre d'emploi : {job_advert}
        Réponse :
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=["resume", "job_advert"])
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume, "job_advert": job_advert})
        return result


class ResumeGenerator:
    def __init__(self, resume: str, job_advert: str, resumeStrategy: ResumeAIStrategy):
        self.resume = resume
        self.job_advert = job_advert
        self.resumeStrategy = resumeStrategy

    def generator(self) -> str:
        """
        Génère un document en fonction de la stratégie de modèle AI fournie.

        Renvoie le document généré en tant que chaîne de caractères. Si une erreur se produit, renvoie un
        message d'erreur détaillé.

        Returns
        -------
        str
            Le document généré ou un message d'erreur si une exception s'est produite.
        """
        try:
            generated_text = self.resumeStrategy.generate(resume=self.resume, job_advert=self.job_advert)
            return generated_text
        except TimeoutError:
            return "Le modèle a pris trop de temps pour répondre. Veuillez réessayer plus tard."
        except ModelError as e:
            return f"Une erreur s'est produite lors de l'appel au modèle : {str(e)}"
        except HTTPError as http_err:
            if http_err.response.status_code == 500:
                request_id = http_err.response.headers.get("x-request-id", "N/A")
                return f"API problem: Internal Server Error (Request ID: {request_id})"
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
        """
        Complétez le modèle de courrier électronique ci-dessous en utilisant les informations du CV fourni.
        Remplacez les parties entre crochets [] par les informations pertinentes du CV.
        """
        prompt = """
        Complétez le modèle de courrier électronique ci-dessous en utilisant les informations du CV fourni. Remplacez
        les parties entre crochets [] par les informations pertinentes du CV.

        Format :
        Bonjour,
        J'espère que vous allez bien.
        Je vous propose le profil de [Prénom du candidat], [Intitulé du poste] avec [Nombre] année(s) d'expérience qui
        pourrait intéresser votre équipe.
        Vous trouverez son dossier technique en pièce jointe.

        En quelques mots :
        - Technologies & Langages : [Liste des technologies et langages de programmation]
        - Compétences métiers : [Liste des compétences métiers pertinentes]
        - Dernier client : [Nom de l'entreprise de la dernière expérience]
        - Disponibilité : [Date de disponibilité ou Immédiatement]

        Qu'en pensez-vous ? Je reste à votre disposition pour toute information complémentaire.
        Excellente journée,
        CV : {resume}
        Réponse :
        """
        prompt_template = PromptTemplate(template=prompt, input_variables=["resume"])
        chain = prompt_template | self.llm
        result = chain.invoke({"resume": resume})
        return result
