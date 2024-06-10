---
title: CvGeniusAI
emoji: 📉
colorFrom: red
colorTo: red
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
license: apache-2.0
---


# CV Genius

CV Genius est une application web développée avec Streamlit qui utilise des modèles d'intelligence artificielle pour aider les utilisateurs dans leur processus de candidature. Elle fournit des fonctionnalités telles que le scoring de CV par rapport à une offre d'emploi, la génération de lettres de motivation personnalisées et l'amélioration des CV.

![alt text](image.png)
## Fonctionnalités

- **Score de correspondance CV/Offre d'emploi** : Évalue la correspondance entre le CV d'un candidat et une offre d'emploi spécifique en attribuant un score sur 100 et en identifiant les points forts et les points faibles.
- **Rédaction de lettre de motivation** : Génère une lettre de motivation personnalisée en fonction du CV et de l'offre d'emploi.
- **Amélioration de CV** : Améliore le CV en intégrant les compétences, qualifications et expériences pertinentes pour l'offre d'emploi visée.
- **Completion de mail** : Complète un modèle de courrier électronique avec les informations du candidat tirées de son CV.

## Prérequis

- Python 3.8 ou version supérieure
- Les dépendances listées dans le fichier `requirements.txt`
- Un jeton d'API Hugging Face (à définir dans un fichier `.env`)

## Installation

1. Clonez ce dépôt :

```
git clone https://huggingface.co/spaces/bourahima/CvGeniusAI
```

2. Installez les dépendances :

```
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet et ajoutez votre jeton d'API Hugging Face :

```
huggingface_api_key=YOUR_API_TOKEN
```

## Utilisation

1. Démarrez l'application Streamlit :

```
streamlit run app.py
```

2. Suivez les instructions dans l'interface utilisateur pour utiliser les différentes fonctionnalités de l'application.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer à ce projet, veuillez suivre les étapes suivantes :

1. Fork ce dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commitez vos modifications (`git commit -am 'Ajoute une nouvelle fonctionnalité'`)
4. Poussez la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request
