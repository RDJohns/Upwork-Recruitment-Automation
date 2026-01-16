# 🚀 Upwork Recruitment Automation

> **Système complet d'automatisation du recrutement sur Upwork**  
> Architecture basée sur Kestra, Skyvern AI, Airtable et Google Cloud

---

## 📋 Vue d'ensemble

Ce projet automatise l'ensemble du processus de recrutement sur Upwork :
- 🎯 **Publication automatique** des offres d'emploi
- 🔍 **Recherche intelligente** de candidats qualifiés
- 📧 **Campagnes d'invitation** automatisées
- 📊 **Collecte et analyse** des réponses

### Stack Technique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Orchestration** | Kestra | Latest | Workflow engine, scheduling, retry logic |
| **Automation** | Skyvern | Latest | AI-driven browser automation (LLM-based) |
| **Data Store** | Airtable | API v2.0 | Base de données centrale + UI admin |
| **Compute** | Google Cloud VM | n1-standard-2 | Environnement d'exécution isolé |
| **Storage** | Google Cloud Storage | Latest | Screenshots, logs visuels |
| **Language** | Python | 3.11+ | Logique métier et intégrations |

---

## 🏗️ Architecture du Projet

```
upwork-automation/
├── 📁 src/
│   ├── 📁 core/                    # Business logic (agnostic plateforme)
│   │   ├── hiring_manager.py      # Orchestration métier
│   │   ├── scoring_engine.py      # Algorithme de scoring candidats
│   │   ├── decision_rules.py      # Règles de qualification
│   │   └── interfaces.py          # Abstract classes
│   │
│   ├── 📁 adapters/                # Platform-specific implementations
│   │   ├── 📁 upwork/
│   │   │   ├── tasks.py            # Skyvern task definitions
│   │   │   ├── parser.py          # Data extraction & parsing
│   │   │   └── auth.py            # Authentication handler
│   │   ├── 📁 fiverr/             # [Future expansion]
│   │   └── 📁 freelancer/         # [Future expansion]
│   │
│   ├── 📁 services/                # External service clients
│   │   ├── airtable_client.py     # Airtable CRUD wrapper
│   │   ├── storage.py             # GCS upload handler
│   │   ├── skyvern_client.py      # Skyvern API wrapper
│   │   └── logger.py              # Structured logging
│   │
│   ├── 📁 utils/
│   │   ├── config.py              # Environment variables loader
│   │   ├── logger.py              # Structured logging
│   │   └── helpers.py             # Common utilities
│   │
│   └── 📁 workflows/               # Kestra flow definitions
│       ├── job_publishing.yaml
│       ├── candidate_search.yaml
│       ├── invitation.yaml
│       └── response_collection.yaml
│
├── 📁 tests/
│   ├── unit/
│   └── integration/
│
├── 📁 docs/
│   └── API.md
│
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔧 Prérequis

### Infrastructure requise

1. **Google Cloud Platform**
   - VM instance (n1-standard-2 recommandé)
   - Google Cloud Storage bucket
   - Service account avec permissions Storage

2. **Airtable**
   - Compte Airtable (Pro ou Enterprise recommandé)
   - Base de données avec 4 tables (voir configuration)

3. **Services externes**
   - Compte Skyvern (API key requise)
   - Compte Upwork (credentials d'authentification)

### Logiciels requis

- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**

### Vérification rapide des prérequis

```bash
# Vérifier Python
python3 --version  # Doit être 3.11+

# Vérifier Docker
docker --version
docker-compose --version

# Vérifier Git
git --version

# Vérifier accès aux services (optionnel)
curl -I https://api.airtable.com
curl -I https://api.skyvern.ai
```

---

## 📦 Installation Complète

### Étape 1: Cloner le projet

```bash
git clone <repository-url>
cd upwork-automation
```

### Étape 2: Configuration de l'environnement Python

```bash
# Créer environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep -E "(airtable|skyvern|kestra)"
```

### Étape 3: Configuration des variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos credentials
nano .env  # ou vim .env, ou code .env
```

**Variables requises dans `.env` :**

```bash
# ======== SERVICES EXTERNES ========
# Airtable (obtenir depuis airtable.com/create/tokens)
AIRTABLE_API_KEY=patxxxxxxxxxxxxxxxxxxxxxx
AIRTABLE_BASE_ID=appxxxxxxxxxxxxxxxxxxxxxx

# Skyvern (obtenir depuis app.skyvern.com/settings)
SKYVERN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
SKYVERN_BASE_URL=https://api.skyvern.com/v1

# Upwork Credentials (obligatoire)
UPWORK_USERNAME=votre-email@domain.com
UPWORK_PASSWORD=votre-mot-de-passe

# 2FA Configuration (optionnel - pour automation complète)
# UPWORK_2FA_METHOD=email                    # email, backup_code, authenticator
# UPWORK_EMAIL_ACCESS=false                  # true pour activer lecture automatique
# UPWORK_2FA_EMAIL=votre-email-2fa@domaine.com
# UPWORK_EMAIL_PASSWORD=votre-mot-de-passe-email-2fa

# ======== INFRASTRUCTURE ========
# Google Cloud Storage
GCS_BUCKET_NAME=upwork-automation-screenshots
GCS_CREDENTIALS_PATH=/path/to/service-account.json

# ======== APPLICATION ========
# Logs et monitoring
LOG_LEVEL=INFO

# Limites Upwork (à adapter selon votre compte)
MAX_INVITATIONS_PER_DAY=50
MAX_PROFILES_PER_JOB=50
BATCH_SIZE=10

# Performance
MAX_PARALLEL_JOBS=3
SESSION_TTL_MINUTES=30
SCRAPING_DELAY_SECONDS=3

# Scoring algorithm
MIN_QUALIFICATION_SCORE=70
REVIEW_SCORE_THRESHOLD=40
```

**Validation de la configuration :**

```bash
# Test rapide des variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['AIRTABLE_API_KEY', 'SKYVERN_API_KEY', 'UPWORK_USERNAME']
missing = [var for var in required if not os.getenv(var)]

if missing:
    print(f'❌ Variables manquantes: {missing}')
else:
    print('✅ Configuration de base OK')
"
```

### Étape 4: Configuration Airtable

#### 4.1 Création de la base

1. **Connectez-vous à [Airtable](https://airtable.com)**
2. **Créez une nouvelle base** : "Upwork Recruitment Automation"
3. **Créez les 4 tables** suivantes :

#### 4.2 Table 1: `Jobs`

| Champ | Type | Formula/Options | Description |
|-------|------|----------------|-------------|
| Job ID | Formula | `JOB-{RECORD_ID()}` | ID unique auto-généré |
| Title | Single line text | - | Titre de l'offre |
| Description | Long text | - | Description complète du poste |
| Skills | Multiple select | Python, React, Node.js, etc. | Compétences requises |
| Budget | Currency | USD | Budget alloué |
| Contract Type | Single select | Hourly, Fixed Price | Type de contrat |
| Duration | Single select | < 1 week, 1-3 months, 3-6 months | Durée estimée |
| Status | Single select | Draft, To Publish, Published, Closed | État du job |
| Platform | Single select | Upwork, Fiverr, Freelancer | Plateforme cible |
| Upwork URL | URL | - | Lien vers l'offre publiée |
| Published Date | Date | - | Date de publication |
| Created Time | Created time | - | Timestamp de création |
| Last Updated | Last modified time | - | Dernière modification |

#### 4.3 Table 2: `Candidates`

| Champ | Type | Description |
|-------|------|-------------|
| Candidate ID | Formula | `CAND-{RECORD_ID()}` |
| Name | Single line text | Nom du freelance |
| Profile URL | URL | Lien profil Upwork (unique) |
| Job ID | Link to Jobs | Relation avec l'offre |
| Platform | Single select | Plateforme d'origine |
| Qualification Status | Single select | To Review, Qualified, Unqualified, Rejected |
| Invitation Status | Single select | Not Invited, Sent, Accepted, Declined, No Response |
| Algorithm Score | Number | Score de matching (0-100) |
| Hourly Rate | Currency | Tarif horaire en USD |
| Job Success Score (JSS) | Percent | Score succès Upwork (0-100%) |
| Total Earned | Currency | Revenus totaux plateforme |
| Total Jobs | Number | Nombre de projets complétés |
| Location | Single line text | Pays/Ville |
| Skills | Multiple select | Compétences du candidat |
| Portfolio Analyzed | Checkbox | Portfolio analysé par IA |
| Review Notes | Long text | Notes humaines ou IA |
| Invited Date | Date | Date d'invitation |
| Response Date | Date | Date de réponse |
| First Scraped | Created time | Première fois vu |

#### 4.4 Table 3: `Interactions`

| Champ | Type | Options | Description |
|-------|------|----------|-------------|
| Interaction ID | Formula | `INT-{RECORD_ID()}` | ID unique |
| Candidate ID | Link to Candidates | - | Lien vers le candidat |
| Job ID | Link to Jobs | - | Lien vers l'offre |
| Type | Single select | Invitation, Message Received, Error Log, System Event, Scraping Event | Type d'interaction |
| Content | Long text | - | Contenu message/erreur |
| Timestamp | Created time | - | Horodatage automatique |
| Severity | Single select | Info, Warning, Error, Critical | Niveau de gravité |
| Screenshot URL | URL | - | Lien vers screenshot GCS |
| Metadata | Long text | - | JSON metadata (stack trace, context) |

#### 4.5 Table 4: `System_Metrics`

| Champ | Type | Options | Description |
|-------|------|----------|-------------|
| Metric ID | Formula | `METRIC-{RECORD_ID()}` | ID unique |
| Date | Date | - | Date de la métrique |
| Metric Name | Single select | Invitations Sent, Jobs Published, Profiles Scraped, Errors Count | Nom de la métrique |
| Value | Number | - | Valeur de la métrique |
| Platform | Single select | Upwork, All | Plateforme concernée |
| Notes | Long text | - | Commentaires |

#### 4.6 Configuration des vues (recommandé)

**Vue "Jobs à Publier"** (table Jobs) :
- Filter: `{Status} = 'To Publish'`
- Sort: `Created Time` (Newest first)

**Vue "Candidats Qualifiés"** (table Candidates) :
- Filter: `AND({Qualification Status} = 'Qualified', {Invitation Status} = 'Not Invited')`
- Sort: `Algorithm Score` (Highest first)

**Vue "Erreurs Critiques"** (table Interactions) :
- Filter: `{Severity} = 'Critical'`
- Sort: `Timestamp` (Newest first)

**Vue "Métriques Journalières"** (table System_Metrics) :
- Filter: `{Date} = TODAY()`
- Group: `Metric Name`

### Étape 5: Configuration Google Cloud Storage

#### 5.1 Création du bucket

```bash
# Installer Google Cloud SDK si non déjà installé
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Créer un bucket unique (remplacer avec votre nom)
BUCKET_NAME="upwork-automation-$(date +%s)-$(whoami)"
gsutil mb gs://$BUCKET_NAME

# Configurer les permissions (public pour les screenshots)
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Noter le nom du bucket pour .env
echo "Bucket créé: $BUCKET_NAME"
```

#### 5.2 Configuration du Service Account

```bash
# Créer un service account
gcloud iam service-accounts create upwork-automation \
    --display-name="Upwork Automation Service Account"

# Donner les permissions nécessaires
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:upwork-automation@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Générer et télécharger la clé
gcloud iam service-accounts keys create ~/upwork-automation-key.json \
    --iam-account=upwork-automation@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Déplacer la clé dans le projet
mv ~/upwork-automation-key.json ./gcs-credentials.json

# Mettre à jour .env avec le chemin
sed -i "s|/path/to/service-account.json|./gcs-credentials.json|" .env
```

#### 5.3 Test de connexion

```bash
# Test d'upload
echo "test" | gsutil cp - gs://$BUCKET_NAME/test.txt

# Vérifier
gsutil ls gs://$BUCKET_NAME/

# Nettoyer
gsutil rm gs://$BUCKET_NAME/test.txt
```

### Étape 6: Installation de Kestra (Docker)

#### 6.1 Préparation de l'environnement

```bash
# Vérifier que Docker est actif
docker --version
docker-compose --version

# Créer les dossiers nécessaires
mkdir -p kestra/config kestra/workflows logs storage

# Donner les permissions
chmod 755 kestra/config logs storage
```

#### 6.2 Configuration Docker Compose

Le fichier `docker-compose.yml` est déjà fourni dans le projet. Vérifions-le :

```bash
# Vérifier que le fichier existe
ls -la docker-compose.yml

# Le visualiser si besoin
cat docker-compose.yml
```

#### 6.3 Démarrage de Kestra

```bash
# Démarrer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Attendre le démarrage complet (30-60 secondes)
echo "Attente du démarrage de Kestra..."
sleep 45

# Vérifier que Kestra est accessible
curl -f http://localhost:8080/health || echo "Kestra pas encore prêt"
```

#### 6.4 Configuration de Kestra

Le fichier `kestra/config/kestra.yml` est déjà configuré. Pour le personnaliser :

```bash
# Vérifier la configuration
cat kestra/config/kestra.yml

# Personnaliser si nécessaire (port, base de données, etc.)
nano kestra/config/kestra.yml

# Redémarrer si modifié
docker-compose restart kestra
```

#### 6.5 Accès à l'interface Kestra

```bash
# Ouvrir dans le navigateur
echo "Kestra UI: http://localhost:8080"

# Ou tester avec curl
curl http://localhost:8080/api/v1/info
```

### Étape 7: Configuration des secrets Kestra

#### 7.1 Accès à l'interface

1. **Ouvrez** http://localhost:8080 dans votre navigateur
2. **Créez un namespace** : `recruitment` (ou le nom de votre choix)
3. **Allez dans** Settings → Secrets

#### 7.2 Ajout des secrets

Ajoutez les secrets suivants un par un :

```bash
# Via l'interface web ou en CLI (si kestra CLI installé)
kestra secrets set AIRTABLE_API_KEY "votre-clé-airtable-complète"
kestra secrets set SKYVERN_API_KEY "votre-clé-skyvern-complète"
kestra secrets set UPWORK_USERNAME "votre-email-upwork"
kestra secrets set UPWORK_PASSWORD "votre-mot-de-passe-upwork"
# kestra secrets set UPWORK_2FA_METHOD "email"                    # optionnel
# kestra secrets set UPWORK_EMAIL_ACCESS "false"                  # optionnel
# kestra secrets set UPWORK_2FA_EMAIL "votre-email-2fa@domaine.com"  # optionnel
# kestra secrets set UPWORK_EMAIL_PASSWORD "votre-mot-de-passe-email" # optionnel
kestra secrets set GCS_CREDENTIALS "$(cat gcs-credentials.json)"
```

#### 7.3 Validation des secrets

```bash
# Lister tous les secrets
kestra secrets list

# Tester un secret spécifique
kestra secrets get AIRTABLE_API_KEY
```

#### 7.4 Import des workflows

```bash
# Copier les workflows dans le dossier Kestra
cp workflows/*.yaml kestra/workflows/

# Importer via l'interface
# 1. Allez dans Flows → Import
# 2. Sélectionnez les fichiers .yaml
# 3. Importez dans le namespace recruitment

# Ou redémarrer Kestra pour chargement automatique
docker-compose restart kestra

# Vérifier l'import
curl http://localhost:8080/api/v1/flows | jq '.[] | .id'
```

---

## 🚀 Lancement du Système

### 1. Validation rapide de l'installation

```bash
# Test complet de la configuration
python tests/test_config.py

# Si tous les tests passent, continuez
# Sinon, corrigez les erreurs avant de continuer
```

### 2. Test des services individuels

```bash
# Test Airtable
python -c "
from src.services.airtable_client import AirtableClient
client = AirtableClient()
print('✅ Airtable OK' if client.test_connection() else '❌ Airtable KO')
"

# Test Skyvern (nécessite vraie API key)
python -c "
from src.services.skyvern_client import SkyvernClient
client = SkyvernClient()
print('✅ Skyvern OK' if client.test_connection() else '❌ Skyvern KO')
"

# Test scoring engine
python -c "
from src.core.scoring_engine import CandidateScoringEngine
engine = CandidateScoringEngine()
print('✅ Scoring engine OK')
"
```

### 3. Lancement de l'environnement Docker

```bash
# Démarrer Kestra et PostgreSQL
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps

# Voir les logs si problème
docker-compose logs kestra
```

### 4. Configuration des secrets Kestra

Accédez à `http://localhost:8080` :

1. **Créer un namespace** : `recruitment`
2. **Ajouter les secrets** via l'interface :
   - `AIRTABLE_API_KEY`
   - `SKYVERN_API_KEY`
   - `UPWORK_USERNAME`
   - `UPWORK_PASSWORD`
   - `UPWORK_2FA_BACKUP`

### 5. Import des workflows

```bash
# Copier les workflows Kestra
cp workflows/*.yaml kestra/workflows/

# Redémarrer Kestra pour charger les workflows
docker-compose restart kestra

# Attendre 30 secondes puis vérifier
curl http://localhost:8080/api/v1/flows
```

### 6. Premier test complet

```bash
# Créer un job test dans Airtable manuellement :
# - Title: "Python Developer Test"
# - Description: "Test job for automation"
# - Skills: ["Python", "Django"]
# - Budget: 1000
# - Status: "To Publish"
# - Platform: "Upwork"

# Lancer le workflow de publication
python src/main.py publish

# Vérifier les résultats dans Airtable
```

---

## 📊 Monitoring & Maintenance

### Dashboard Kestra

Accédez à `http://localhost:8080` pour :
- **Monitoring des flows** en temps réel
- **Visualisation des logs** et erreurs
- **Gestion des secrets** et variables
- **Scheduling** des automatisations

### Logs et Alertes

- **Airtable Interactions** : Source de vérité pour tous les événements
- **Kestra UI** : Monitoring temps réel des exécutions
- **Google Cloud Storage** : Screenshots des erreurs
- **Logs applicatifs** : Dans `logs/` du projet

### Métriques clés à surveiller

- **Jobs Published** : Nombre d'offres publiées/jour
- **Invitations Sent** : Nombre d'invitations envoyées/jour
- **Response Rate** : Taux de réponse aux invitations
- **Error Rate** : Taux d'erreur par workflow

---

## ⚠️ Limites et Considérations

### Rate Limits Upwork

- **Max 50 invitations/jour** (configurable)
- **Max 100 profils scrapés/heure**
- **Délais anti-détection** intégrés

### Bonnes pratiques

1. **Démarrer lentement** : Commencer avec 1-2 jobs/jour
2. **Monitorer les erreurs** : Vérifier régulièrement Airtable
3. **Respecter les quotas** : Ne pas dépasser les limites Upwork
4. **Sauvegarder les données** : Exporter Airtable régulièrement

### Sécurité

- **Ne jamais committer** les credentials dans Git
- **Utiliser les secrets Kestra** pour les données sensibles
- **Rotation des clés API** recommandée trimestriellement
- **Accès restreint** à l'interface Kestra en production

---

## 🛠️ Développement Personnalisé

### Ajouter une nouvelle plateforme

1. Créer un nouvel adapter dans `src/adapters/nouvelle_plateforme/`
2. Implémenter les interfaces de `src/core/interfaces.py`
3. Ajouter les workflows Kestra correspondants
4. Mettre à jour le schéma Airtable si nécessaire

### Modifier l'algorithme de scoring

Éditez `src/core/scoring_engine.py` :

```python
# Personnaliser les poids
WEIGHTS = {
    'skills_match': 0.40,      # Augmenté de 35% à 40%
    'jss': 0.25,               # Augmenté de 20% à 25%
    'experience': 0.15,        # Réduit de 20% à 15%
    'portfolio': 0.10,         # Réduit de 15% à 10%
    'rate_compatibility': 0.10 # Inchangé
}
```

### Ajouter de nouvelles métriques

1. Mettre à jour `src/services/airtable_client.py`
2. Ajouter les nouvelles métriques dans `System_Metrics`
3. Créer les vues correspondantes dans Airtable

---

## 📚 Support & Documentation

### Documentation complémentaire

- [Kestra Documentation](https://kestra.io/docs/)
- [Skyvern API Documentation](https://www.skyvern.com/docs)
- [Skyvern API Reference](https://www.skyvern.com/docs/api-reference/api-reference/agent/run-task)
- [Airtable API Documentation](https://airtable.com/developers/web/api)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)

### Guides spécialisés

- 📄 **[Setup Minimal](docs/MINIMAL_SETUP.md)** : Démarrage avec 2 variables seulement
- 🤖 **[Email 2FA Automation](docs/EMAIL_2FA_AUTOMATION.md)** : Configuration complète automatique

### Dépannage commun

**Problème : Erreur d'authentification Upwork**
- Vérifier les credentials dans les secrets Kestra
- Confirmer que le 2FA backup code est valide
- Vérifier les logs dans Airtable Interactions

**Problème : Skyvern API timeout**
- Augmenter les timeouts dans `src/services/skyvern_client.py`
- Vérifier la connectivité réseau depuis la VM
- Consulter les logs Skyvern pour plus de détails

**Problème : Airtable rate limit**
- Implémenter des backoffs exponentiels
- Utiliser le cache pour les requêtes répétées
- Vérifier le plan Airtable (limits par minute)

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

> **🎯 Pour commencer** : Suivez les étapes d'installation dans l'ordre, testez avec un job unique, puis augmentez progressivement le volume d'automatisation.  
> **📞 Support** : Pour toute question technique, consultez la documentation Kestra ou créez une issue dans le repository GitHub.
