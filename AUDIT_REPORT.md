# Audit de production-readiness — CVGenius

Date : 2026-07-12
Portée convenue : refonte complète, comptes nominatifs + rôles, conformité RGPD, hébergement Streamlit Cloud / Hugging Face Spaces.

## 0. Action à faire immédiatement, par vous, hors de ce dépôt

Un jeton d'API Hugging Face réel et des identifiants `admin`/`admin` étaient committés en clair dans `.streamlit/secrets.toml` depuis le tout premier commit (juillet 2024), dans un dépôt public. Ce jeton doit être considéré comme compromis.

1. **Révoquez immédiatement ce token sur huggingface.co** (Settings → Access Tokens) et générez-en un nouveau.
2. Le nouveau token, ainsi que les comptes recruteurs, doivent être saisis **uniquement** dans les "Secrets" de la plateforme d'hébergement (Streamlit Cloud ou HF Spaces), jamais dans un fichier commité. Voir `.streamlit/secrets.toml.example` pour le format attendu.
3. **Recommandé** : purger le token de l'historique git (`git filter-repo` ou BFG Repo-Cleaner) puis force-push, car `git rm` seul ne supprime pas le secret des commits passés. Je ne l'ai pas fait automatiquement car c'est une opération destructive sur l'historique partagé — dites-moi si vous voulez que je la prépare.

## 1. Corrections appliquées dans ce PR

### Sécurité
- **Secrets retirés du dépôt** : `.streamlit/secrets.toml` et `auth/config.yaml` ne sont plus versionnés (untracked + `.gitignore` corrigé — l'ancienne règle pointait vers `.secrets/secrets.toml`, un chemin qui n'existe pas, d'où la fuite).
- **Authentification unifiée** : il existait deux systèmes d'auth en parallèle et incohérents (`auth/authentification.py` branché dans `app.py`, et un système mort à base de `werkzeug`/`users.json` dans `scr/logs.py`, jamais appelé). Le second a été supprimé.
- **Comptes nominatifs + rôles** (`admin` / `recruiter`) : les identifiants, la clé de signature du cookie et les rôles vivent désormais dans `st.secrets` (plateforme), plus dans un fichier YAML commité avec une clé de cookie par défaut (`some_signature_key`) et des mots de passe d'exemple non hashés.
- **Page d'administration** (`ui/admin/render_admin.py`, visible seulement si `role == admin`) : génère le hash bcrypt et le bloc TOML à coller dans les Secrets pour ajouter un recruteur. Il n'y a pas de création de compte "live" en base : Streamlit Cloud/HF Spaces n'offrent pas de disque persistant fiable, donc un magasin d'utilisateurs local (JSON/SQLite) serait effacé au moindre redéploiement — j'ai documenté ce compromis plutôt que de construire une fausse persistance.
- **Journal d'audit minimal** (`scr/logs.py`, entièrement réécrit) : logge qui a fait quelle action et quand, **jamais** le contenu du CV ou de l'offre d'emploi (minimisation RGPD). Sort sur stdout, visible dans les logs de la plateforme.
- **`__pycache__/` et `CVGenius.egg-info/` (artefacts de build)** étaient aussi commités par erreur ; retirés du suivi git et ajoutés au `.gitignore`.

### Bugs
- `MailCompletion` utilisait `repo_id="mistralai/MixTraL-8x7B-Instruct-v0.1"` (casse incorrecte vs. `Mixtral` utilisé ailleurs) → échouait probablement à l'appel API. Un seul `RESUME_MODEL_REPO_ID` partagé évite la divergence.
- `add_to_git_credential=True` sur `HuggingFaceEndpoint` écrivait le token dans le credential store git du serveur — effet de bord inutile et risqué, supprimé.
- `process_cv_job_offer` : si la tâche sélectionnée ne correspondait à aucun des 3 cas, `strategy` n'était jamais assignée → `UnboundLocalError`. Remplacé par un dictionnaire `TASK_STRATEGIES` avec validation en amont.
- Chemins d'assets (`images/logo.png`, etc.) construits avec `os.getcwd()` — fragile selon le répertoire de lancement. Remplacé par un chemin relatif au fichier source (`__file__`).

### Gestion d'erreurs
- Les exceptions (y compris les erreurs HTTP/modèle) étaient renvoyées telles quelles à l'utilisateur (`str(e)`), risque de fuite d'information. Elles sont maintenant journalisées côté serveur (`log_error`) et un message générique est affiché à l'utilisateur.
- Une extraction PDF échouée (fichier corrompu/protégé) plantait auparavant l'app ; elle est maintenant interceptée avec un message clair.

### RGPD / confidentialité des données
- Case à cocher de consentement avant tout envoi de CV au prestataire IA tiers (score, lettre de motivation, amélioration de CV, complétion de mail).
- Section "Confidentialité des données" ajoutée à la page Infos : ce qui est envoyé, à qui, et ce qui n'est pas stocké.
- Aucune donnée de CV n'était déjà écrite sur disque (bon point existant) — confirmé et documenté.
- Les données sensibles laissées dans `st.session_state` (CV importé, texte d'offre) sont explicitement effacées à la déconnexion.

### Tests
- Le test `test_generate` et `test_process_cv_job_offer` échouaient déjà avant cet audit (la construction de `HuggingFaceEndpoint` valide le token via un **vrai appel réseau**, qui échoue sans jeton valide) — donc la CI n'était probablement jamais verte en pratique. Corrigé en mockant `HuggingFaceEndpoint`.
- Ajout de tests pour : rôles/permissions, page admin, garde anti-`UnboundLocalError`, non-fuite des détails d'erreur, casse du `repo_id`, consentement RGPD.
- Suite complète : **32/32 tests passent**, flake8 propre.

### CI
- Ajout d'un job de scan de secrets (gitleaks) sur chaque push/PR — c'est ce qui aurait dû empêcher la fuite initiale.
- Ajout de `pip-audit` (non bloquant pour l'instant, voir section suivante).
- Ajout de Dependabot (pip + GitHub Actions) pour les mises à jour de sécurité.

## 2. `hydralit` / `hydralit_components` retirés (suite à validation)

`pip install -r requirements.txt` dans un environnement neuf (setuptools moderne, comme sur un conteneur de build fraîchement provisionné) **échouait** :

```
AttributeError: install_layout. Did you mean: 'install_platlib'?
ERROR: Failed building wheel for hydralit_components
```

`hydralit`/`hydralit_components` n'étaient plus maintenus et utilisaient un mécanisme de build (`distutils`) incompatible avec les versions récentes de `setuptools` — un redéploiement futur sur Streamlit Cloud/HF Spaces pouvait échouer du jour au lendemain selon l'image de build de la plateforme, hors de votre contrôle.

**Action effectuée** : remplacement de la barre de navigation (`hc.nav_bar`) et des sélecteurs de tâche (`hc.option_bar`) par des `st.radio(horizontal=True)` natifs Streamlit, avec `format_func` pour conserver les icônes. Comportement fonctionnel identique (mêmes valeurs de retour, mêmes clés de session), rendu visuel légèrement différent (radio plutôt que barre à onglets stylée). `get_over_theme()` (thème hydralit) a été supprimé, devenu inutile. Les dépendances `hydralit`, ainsi que `streamlit-pills` et `streamlit-aggrid` (présentes dans `requirements.txt` mais jamais importées nulle part dans le code), et `werkzeug` (ne servait qu'à l'ancien système d'auth mort déjà supprimé), ont été retirées de `requirements.txt`.

Vérifié : `pip install -r requirements.txt` réussit maintenant dans un environnement neuf, sans contournement de version de `setuptools`.

## 3. Autres recommandations non implémentées (à arbitrer)

- **Dépendances anciennes** : `langchain==0.2.9`, `streamlit-authenticator==0.3.2` datent d'avant juillet 2024 ; `pip-audit` est en place mais volontairement non bloquant tant que personne n'a trié les CVE potentiels sur cette stack — le rendre bloquant est une prochaine étape logique une fois triée.
- **SSO d'entreprise** : vous avez retenu "comptes nominatifs + rôles" plutôt que SSO pour l'instant — si le nombre de recruteurs grandit, une intégration Azure AD/Google Workspace évitera la gestion manuelle des secrets par blocs TOML.
- **Rétention des logs d'audit** : les logs partent sur stdout (capturés par la plateforme). Si vous avez une obligation de conservation de la piste d'audit à moyen terme, il faudra les envoyer vers un puits de logs externe (les logs de plateforme ne sont pas garantis persistants).
