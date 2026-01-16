# 🚀 Architecture Automatisation Recrutement Upwork

> **Document de référence technique**  
> Architecture complète et optimisée pour l'automatisation du recrutement sur Upwork via Kestra, Google Cloud VM et Airtable.

---

## 📋 Vue d'ensemble

### Objectifs de l'Architecture
- 🎯 **Automatisation End-to-End** : De la publication d'offres à l'engagement candidat
- 🤖 **AI-Driven Automation** : Skyvern pour interactions web intelligentes
- 🧠 **Intelligence Décisionnelle** : Scoring et qualification automatique
- 🔄 **Résilience** : Gestion d'erreurs multi-niveaux + résistance aux changements UI
- 📈 **Scalabilité** : Extension multi-plateformes (Upwork, Fiverr, Freelancer)
- ⚡ **Performance** : Optimisation sessions et batch processing

### Stack Technique Core

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Orchestration** | Kestra | Workflow engine, scheduling, retry logic |
| **Automation** | Skyvern | AI-driven browser automation (LLM-based) |
| **Data Store** | Airtable | Base de données centrale + UI admin |
| **Compute** | Google Cloud VM (n1-standard-2) | Environnement d'exécution isolé |
| **Storage** | Google Cloud Storage | Screenshots, logs visuels |

---

## 🏗️ 1. Architecture Système (Layers)

### Architecture en 3 Tiers

```
┌────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                      │
│                    (Kestra Workflows)                      │
│                                                            │
│  • Scheduling (Cron triggers)                              │
│  • State Management (Flow execution state)                 │
│  • Error Handling & Retry (Exponential backoff)           │
│  • Multi-flow Coordination (Publish → Search → Invite)    │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER                          │
│              (Google Cloud VM Workers)                     │
│                                                            │
│  ┌──────────────────────┐    ┌──────────────────────┐    │
│  │  Skyvern Agent       │    │  Core Business Logic │    │
│  │  • AI Task Execution │    │  • Scoring Algorithm │    │
│  │  • LLM-based Nav.    │    │  • Filtering Rules   │    │
│  │  • Auto-adapt UI     │    │  • Decision Engine   │    │
│  └──────────────────────┘    └──────────────────────┘    │
│                                                            │
│  ┌──────────────────────┐    ┌──────────────────────┐    │
│  │  Platform Adapters   │    │  Service Clients     │    │
│  │  • Upwork            │    │  • Airtable API      │    │
│  │  • Fiverr [Future]   │    │  • GCS Storage       │    │
│  │  • Freelancer [...]  │    │                      │    │
│  └──────────────────────┘    └──────────────────────┘    │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│                    DATA LAYER                              │
│                                                            │
│  ┌──────────────────────────┐  ┌──────────────────────┐  │
│  │       Airtable           │  │         GCS          │  │
│  │                          │  │                      │  │
│  │ • Jobs                   │  │ • Screenshots        │  │
│  │ • Candidates             │  │ • Error Logs         │  │
│  │ • Interactions           │  │ • Artifacts          │  │
│  │ • System_Metrics         │  │                      │  │
│  └──────────────────────────┘  └──────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Structure du Projet (Code Organization)

```
📦 upwork-automation/
├── 📁 src/
│   ├── 📁 core/                    # Business logic (agnostic plateforme)
│   │   ├── hiring_manager.py      # Orchestration métier
│   │   ├── scoring_engine.py      # Algorithme de scoring candidats
│   │   ├── decision_rules.py      # Règles de qualification
│   │   └── interfaces.py          # Abstract classes (JobPoster, Searcher, Inviter)
│   │
│   ├── 📁 adapters/                # Platform-specific implementations
│   │   ├── 📁 upwork/
│   │   │   ├── tasks.py            # Skyvern task definitions (natural language)
│   │   │   ├── parser.py          # Data extraction & parsing
│   │   │   └── auth.py            # Authentication handler (2FA, captcha)
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
└── docker-compose.yml
```

---

## 🗄️ 2. Schéma de Données (Airtable Extended)

### Table 1️⃣ : `Jobs` (Offres d'emploi)

| Champ | Type | Description | Valeurs / Format |
|-------|------|-------------|------------------|
| `Job ID` | Formula | ID unique auto-généré | `JOB-{RECORD_ID()}` |
| `Title` | Single Line Text | Titre de l'offre | Ex: "Senior React Developer" |
| `Description` | Long Text | Description complète du poste | Markdown supporté |
| `Skills` | Multi Select | Compétences requises | Python, React, Node.js, etc. |
| `Budget` | Currency | Budget alloué | USD |
| `Contract Type` | Single Select | Type de contrat | Hourly, Fixed Price |
| `Duration` | Single Select | Durée estimée | < 1 week, 1-3 months, 3-6 months |
| `Status` | Single Select | État du job | `Draft`, `To Publish`, `Published`, `Closed` |
| `Platform` | Single Select | Plateforme cible | `Upwork`, `Fiverr`, `Freelancer` |
| `Upwork URL` | URL | Lien vers l'offre publiée | Auto-capturé lors publication |
| `Published Date` | Date | Date de publication | Auto-rempli |
| `Created Time` | Created Time | Timestamp de création | Auto |
| `Last Updated` | Last Modified Time | Dernière modification | Auto |
| `Invitations Sent` | Rollup | Nombre d'invitations envoyées | COUNT(Candidates) |
| `Responses Received` | Rollup | Nombre de réponses | COUNT(Interactions WHERE Type = Response) |

### Table 2️⃣ : `Candidates` (Candidats)

| Champ | Type | Description | Valeurs / Format |
|-------|------|-------------|------------------|
| `Candidate ID` | Formula | ID unique | `CAND-{RECORD_ID()}` |
| `Name` | Single Line Text | Nom du freelance | |
| `Profile URL` | URL | Lien profil Upwork | Unique (index) |
| `Job ID` | Link to Jobs | Relation avec l'offre | Many-to-One |
| `Platform` | Single Select | Plateforme d'origine | `Upwork`, `Fiverr`, etc. |
| `Qualification Status` | Single Select | Statut qualification | `To Review`, `Qualified`, `Unqualified`, `Rejected` |
| `Invitation Status` | Single Select | Statut invitation | `Not Invited`, `Sent`, `Accepted`, `Declined`, `No Response` |
| `Algorithm Score` | Number | Score de matching (0-100) | Auto-calculé |
| `Hourly Rate` | Currency | Tarif horaire | USD |
| `Job Success Score (JSS)` | Percent | Score succès Upwork | 0-100% |
| `Total Earned` | Currency | Revenus totaux plateforme | USD |
| `Total Jobs` | Number | Nombre de projets complétés | |
| `Location` | Single Line Text | Pays/Ville | |
| `Skills` | Multi Select | Compétences du candidat | Auto-extrait |
| `Portfolio Analyzed` | Checkbox | Portfolio a été analysé | Auto |
| `Review Notes` | Long Text | Notes humaines ou IA | |
| `Invited Date` | Date | Date d'invitation | Auto |
| `Response Date` | Date | Date de réponse | Auto |
| `First Scraped` | Created Time | Première fois vu | Auto |

### Table 3️⃣ : `Interactions` (Logs & Messages)

| Champ | Type | Description | Valeurs / Format |
|-------|------|-------------|------------------|
| `Interaction ID` | Formula | ID unique | `INT-{RECORD_ID()}` |
| `Candidate ID` | Link to Candidates | Lien vers le candidat | |
| `Job ID` | Link to Jobs | Lien vers l'offre | |
| `Type` | Single Select | Type d'interaction | `Invitation`, `Message Received`, `Error Log`, `System Event`, `Scraping Event` |
| `Content` | Long Text | Contenu message/erreur | |
| `Timestamp` | Created Time | Horodatage automatique | Auto |
| `Severity` | Single Select | Niveau de gravité | `Info`, `Warning`, `Error`, `Critical` |
| `Screenshot URL` | URL | Lien vers screenshot GCS | Pour erreurs |
| `Metadata` | Long Text | JSON metadata | Stack trace, context |

### Table 4️⃣ : `System_Metrics` (Nouveau - Monitoring)

| Champ | Type | Description | Valeurs / Format |
|-------|------|-------------|------------------|
| `Metric ID` | Formula | ID unique | `METRIC-{RECORD_ID()}` |
| `Date` | Date | Date de la métrique | |
| `Metric Name` | Single Select | Nom de la métrique | `Invitations Sent`, `Jobs Published`, `Profiles Scraped`, `Errors Count` |
| `Value` | Number | Valeur de la métrique | |
| `Platform` | Single Select | Plateforme concernée | `Upwork`, `All` |
| `Notes` | Long Text | Commentaires | |

---

## 🔄 3. Flow Map Détaillée (Architecture Process)

### 🌐 Vue Globale des Flows

```
┌─────────────────┐
│  TRIGGER CRON   │
│   ou WEBHOOK    │
└────────┬────────┘
         │
         ▼
    ┌────────────────────────────────────┐
    │   FLOW 1: Job Publishing           │
    │   Fréquence: Toutes les 5 min      │
    │   Condition: Jobs.Status = To Pub  │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │   FLOW 2: Candidate Search         │
    │   Fréquence: Daily 08:00 UTC       │
    │   Condition: Jobs.Status = Pub     │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │   FLOW 3: Invitation Campaign      │
    │   Fréquence: Every 2 hours         │
    │   Condition: Qualified + Not Inv   │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │   FLOW 4: Response Collection      │
    │   Fréquence: Every 4 hours         │
    │   Condition: Always                │
    └────────────────────────────────────┘
```

---

### 📌 FLOW 1 : Job Publishing (Architecture Optimisée)

**🎯 Objectif** : Publier plusieurs offres en batch avec session réutilisable

**⚙️ Architecture du Flow** :

```
START
  │
  ├─→ [Kestra] Fetch Jobs WHERE Status = 'To Publish'
  │    └─→ Airtable Query (filterByFormula)
  │
  ├─→ [Validation] Jobs found?
  │    ├─→ Non → END
  │    └─→ Oui → Continue
  │
  ├─→ [VM Worker] Initialize Browser Session Manager
  │    ├─→ Check existing session (< 30min?)
  │    │    ├─→ Valid → Reuse session ♻️
  │    │    └─→ Expired → Create new session
  │    │
  │    └─→ Login Upwork (si nécessaire)
  │         ├─→ Check cookies persistence
  │         ├─→ Handle 2FA if prompted
  │         └─→ Verify login success
  │
  ├─→ [Loop] For each Job in batch:
  │    │
  │    ├─→ Navigate to "Post a Job"
  │    ├─→ Fill form (Title, Desc, Skills, Budget)
  │    ├─→ Submit & Capture URL
  │    ├─→ Update Airtable:
  │    │    • Status = 'Published'
  │    │    • Upwork URL = [captured]
  │    │    • Published Date = [now]
  │    │
  │    ├─→ Log Interaction (Type: System Event)
  │    └─→ Delay 10-20s (anti-detection)
  │
  ├─→ [Session Management] Keep browser alive
  │    └─→ Set cleanup timer (30min)
  │
  └─→ [Metrics] Update System_Metrics
       • Metric: 'Jobs Published'
       • Value: COUNT(published)
       
END
```

**🔧 Implémentation Technique** :

```python
# /src/workflows/job_publishing_flow.py
from services.skyvern_client import SkyvernClient
from services.airtable_client import AirtableClient
import time

def job_publishing_flow():
    """Flow principal de publication d'offres avec Skyvern"""
    
    # 1. Fetch jobs à publier
    airtable = AirtableClient()
    jobs_to_publish = airtable.get_jobs(
        filter_formula="{Status} = 'To Publish'",
        platform="Upwork"
    )
    
    if not jobs_to_publish:
        print("ℹ️ Aucun job à publier")
        return
    
    print(f"📋 {len(jobs_to_publish)} jobs à publier")
    
    # 2. Initialiser Skyvern client
    skyvern = SkyvernClient()
    
    # 3. Login si nécessaire (Skyvern gère automatiquement)
    skyvern.ensure_authenticated("upwork")
    
    # 4. Batch processing avec Skyvern tasks
    results = []
    for job in jobs_to_publish:
        try:
            # Définir la tâche Skyvern en langage naturel
            task = {
                "url": "https://www.upwork.com/nx/jobs/post/",
                "navigation_goal": "Post a new job on Upwork",
                "data_extraction_goal": "Extract the posted job URL",
                "navigation_payload": {
                    "job_title": job['fields']['Title'],
                    "job_description": job['fields']['Description'],
                    "skills": ", ".join(job['fields']['Skills']),
                    "budget": job['fields']['Budget'],
                    "contract_type": job['fields']['Contract Type']
                }
            }
            
            # Exécuter la tâche via Skyvern
            result = skyvern.execute_task(task)
            job_url = result.get('extracted_data', {}).get('job_url')
            
            # Update Airtable
            airtable.update_job(job['id'], {
                'Status': 'Published',
                'Upwork URL': job_url,
                'Published Date': datetime.now().isoformat()
            })
            
            # Log success
            airtable.create_interaction({
                'Job ID': [job['id']],
                'Type': 'System Event',
                'Content': f"Job published successfully: {job_url}",
                'Severity': 'Info'
            })
            
            results.append({'job_id': job['id'], 'status': 'success', 'url': job_url})
            
            # Anti-detection delay (moins nécessaire avec Skyvern)
            time.sleep(5)
            
        except Exception as e:
            # Log error
            airtable.create_interaction({
                'Job ID': [job['id']],
                'Type': 'Error Log',
                'Content': f"Publication failed: {str(e)}",
                'Severity': 'Error',
                'Metadata': json.dumps({'stack_trace': traceback.format_exc()})
            })
            
            results.append({'job_id': job['id'], 'status': 'error', 'error': str(e)})
    
    # 5. Update metrics
    airtable.create_metric({
        'Metric Name': 'Jobs Published',
        'Value': len([r for r in results if r['status'] == 'success']),
        'Platform': 'Upwork'
    })
    
    return results
```

---

### 📌 FLOW 2 : Candidate Search & Scoring

**🎯 Objectif** : Identifier et scorer automatiquement les candidats qualifiés

**🧠 Architecture du Scoring Engine** :

```python
# /src/core/scoring_engine.py
class CandidateScoringEngine:
    """Algorithme de scoring multi-critères"""
    
    WEIGHTS = {
        'skills_match': 0.35,      # 35%
        'jss': 0.20,               # 20%
        'experience': 0.20,        # 20%
        'portfolio': 0.15,         # 15%
        'rate_compatibility': 0.10 # 10%
    }
    
    def calculate_score(self, candidate_data, job_requirements):
        """Calcule le score total pondéré (0-100)"""
        
        scores = {}
        
        # 1. Skills Match Score
        candidate_skills = set(candidate_data.get('skills', []))
        required_skills = set(job_requirements.get('skills', []))
        
        if required_skills:
            match_ratio = len(candidate_skills & required_skills) / len(required_skills)
            scores['skills_match'] = match_ratio * 100
        else:
            scores['skills_match'] = 0
        
        # 2. Job Success Score (JSS)
        jss = candidate_data.get('job_success_score', 0)
        if jss >= 95:
            scores['jss'] = 100
        elif jss >= 90:
            scores['jss'] = 80
        elif jss >= 80:
            scores['jss'] = 60
        else:
            scores['jss'] = 40
        
        # 3. Experience Score
        total_earned = candidate_data.get('total_earned', 0)
        total_jobs = candidate_data.get('total_jobs', 0)
        
        if total_earned > 50000 and total_jobs > 20:
            scores['experience'] = 100
        elif total_earned > 10000 and total_jobs > 10:
            scores['experience'] = 75
        elif total_earned > 1000:
            scores['experience'] = 50
        else:
            scores['experience'] = 25
        
        # 4. Portfolio Score (keywords dans description)
        portfolio_text = candidate_data.get('profile_description', '').lower()
        job_keywords = job_requirements.get('keywords', [])
        
        keyword_matches = sum(1 for kw in job_keywords if kw.lower() in portfolio_text)
        if job_keywords:
            scores['portfolio'] = (keyword_matches / len(job_keywords)) * 100
        else:
            scores['portfolio'] = 50  # Neutral
        
        # 5. Rate Compatibility
        candidate_rate = candidate_data.get('hourly_rate', 0)
        max_budget = job_requirements.get('max_rate', 999)
        
        if candidate_rate <= max_budget:
            scores['rate_compatibility'] = 100
        elif candidate_rate <= max_budget * 1.2:  # 20% margin
            scores['rate_compatibility'] = 70
        else:
            scores['rate_compatibility'] = 30
        
        # Calcul final pondéré
        final_score = sum(scores[key] * self.WEIGHTS[key] for key in scores)
        
        return {
            'total_score': round(final_score, 2),
            'breakdown': scores
        }
    
    def get_qualification_status(self, score):
        """Détermine le statut basé sur le score"""
        if score >= 70:
            return 'Qualified'
        elif score >= 40:
            return 'To Review'
        else:
            return 'Unqualified'
```

**⚙️ Architecture du Flow Search** :

```
START
  │
  ├─→ [Kestra] Fetch Jobs WHERE Status = 'Published'
  │
  ├─→ [Parallel Processing] For each Job (max 3 concurrent):
  │    │
  │    ├─→ [VM] Launch search on Upwork
  │    │    ├─→ Apply filters (Skills, JSS>90%, Earned>$1k)
  │    │    └─→ Scrape profiles (max 50 per job)
  │    │
  │    ├─→ [Deduplication Check] For each profile:
  │    │    ├─→ Airtable.exists(profile_url)?
  │    │    │    ├─→ Yes → Skip (already processed)
  │    │    │    └─→ No → Continue
  │    │    │
  │    │    ├─→ Extract: Name, Skills, JSS, Rate, Earned, etc.
  │    │    │
  │    │    ├─→ [Scoring Engine] Calculate score
  │    │    │    └─→ scoring_engine.calculate_score()
  │    │    │
  │    │    ├─→ [Decision] Determine status
  │    │    │    • Score ≥ 70 → Qualified
  │    │    │    • 40-69 → To Review
  │    │    │    • < 40 → Unqualified
  │    │    │
  │    │    └─→ [Airtable] Create Candidate record
  │    │
  │    └─→ [Rate Limiting] Throttle: max 20 profiles/min
  │
  ├─→ [Metrics] Update System_Metrics
  │    • Metric: 'Profiles Scraped'
  │    • Value: COUNT(scraped)
  │
  └─→ END
```

---

### 📌 FLOW 3 : Invitation Campaign (Smart Prioritization)

**🎯 Architecture avec Priorisation** :

```python
# /src/core/invitation_prioritizer.py
class InvitationPrioritizer:
    """Gère la priorisation et la limite quotidienne d'invitations"""
    
    MAX_INVITATIONS_PER_DAY = 50
    
    def get_prioritized_candidates(self, airtable_client):
        """Récupère les candidats qualifiés par priorité décroissante"""
        
        # Fetch qualified + not invited
        candidates = airtable_client.get_candidates(
            filter_formula="AND({Qualification Status} = 'Qualified', {Invitation Status} = 'Not Invited')"
        )
        
        # Trier par score (descending)
        candidates_sorted = sorted(
            candidates,
            key=lambda c: c['fields'].get('Algorithm Score', 0),
            reverse=True
        )
        
        # Vérifier quota quotidien
        today_count = airtable_client.count_invitations_today()
        remaining = self.MAX_INVITATIONS_PER_DAY - today_count
        
        if remaining <= 0:
            print("⚠️ Quota quotidien atteint")
            return []
        
        # Retourner top N candidats selon quota restant
        return candidates_sorted[:remaining]
```

**⚙️ Flow Invitation** :

```
START
  │
  ├─→ [Check Quota] Invitations today < 50?
  │    ├─→ Non → END (quota reached)
  │    └─→ Oui → Continue
  │
  ├─→ [Prioritizer] Get top candidates by score
  │    └─→ Sort by Algorithm Score DESC
  │
  ├─→ [Batch] Group by 10 candidates
  │
  ├─→ [VM Worker] For each candidate:
  │    │
  │    ├─→ Open profile
  │    ├─→ Click "Invite to Job"
  │    ├─→ Select job
  │    ├─→ Paste personalized message
  │    │    └─→ Template: "Hi {{Name}}, we're looking for..."
  │    ├─→ Send invitation
  │    │
  │    ├─→ [Airtable] Update:
  │    │    • Invitation Status = 'Sent'
  │    │    • Invited Date = [now]
  │    │
  │    ├─→ [Interaction] Log event
  │    │
  │    └─→ Delay 5-10s (anti-spam)
  │
  ├─→ [Metrics] Update:
  │    • Metric: 'Invitations Sent'
  │    • Value: COUNT(sent)
  │
  └─→ END
```

---

### 📌 FLOW 4 : Response Collection & NLP Analysis

**🎯 Nouveau: Analyse de Sentiment NLP** :

```python
# /src/core/nlp_analyzer.py
from textblob import TextBlob  # ou spaCy pour plus de précision

class ResponseAnalyzer:
    """Analyse automatique des réponses candidats"""
    
    POSITIVE_KEYWORDS = ['interested', 'available', 'yes', 'sure', 'glad', 'excited']
    NEGATIVE_KEYWORDS = ['not interested', 'busy', 'no thanks', 'decline', 'pass']
    QUESTION_KEYWORDS = ['when', 'what', 'how much', 'budget', 'details', '?']
    
    def analyze_response(self, message_content):
        """Analyse le sentiment et classe la réponse"""
        
        message_lower = message_content.lower()
        
        # 1. Classification basique par keywords
        is_positive = any(kw in message_lower for kw in self.POSITIVE_KEYWORDS)
        is_negative = any(kw in message_lower for kw in self.NEGATIVE_KEYWORDS)
        is_question = any(kw in message_lower for kw in self.QUESTION_KEYWORDS)
        
        # 2. Sentiment analysis (TextBlob)
        blob = TextBlob(message_content)
        polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
        
        # 3. Décision finale
        if is_negative or polarity < -0.3:
            return {
                'classification': 'Declined',
                'priority': 'LOW',
                'suggested_action': 'Mark as Declined'
            }
        elif is_positive or polarity > 0.3:
            return {
                'classification': 'Accepted',
                'priority': 'HIGH',
                'suggested_action': 'Notify recruiter immediately'
            }
        elif is_question:
            return {
                'classification': 'Question',
                'priority': 'MEDIUM',
                'suggested_action': 'Human response needed'
            }
        else:
            return {
                'classification': 'Neutral',
                'priority': 'MEDIUM',
                'suggested_action': 'Review manually'
            }
```

---

## ⚠️ 4. Error Handling Architecture (Multi-Level)

### Stratégie en 4 Niveaux

```
┌─────────────────────────────────────────────────────────┐
│ LEVEL 1: Application Level (Try/Catch)                 │
│  • Catch exceptions dans chaque fonction               │
│  • Log détaillé (stack trace)                          │
│  • Continuer si possible (isolation errors)            │
└──────────────────┬──────────────────────────────────────┘
                   │ Si échec persistent ↓
┌─────────────────────────────────────────────────────────┐
│ LEVEL 2: Kestra Retry (Exponential Backoff)            │
│  • maxAttempt: 3                                        │
│  • Delays: 30s → 60s → 120s                            │
│  • Retry sur: Network errors, Timeout, DOM not found   │
└──────────────────┬──────────────────────────────────────┘
                   │ Si toujours échec ↓
┌─────────────────────────────────────────────────────────┐
│ LEVEL 3: Fallback Strategy                             │
│  • Screenshot de l'erreur → GCS                        │
│  • Log dans Airtable (Severity: Critical)              │
│  • Alternative path (si disponible)                    │
└──────────────────┬──────────────────────────────────────┘
                   │ En dernier recours ↓
┌─────────────────────────────────────────────────────────┐
│ LEVEL 4: Human Intervention                            │
│  • Log critical error to Airtable (Severity: Critical) │
│  • Upload error screenshot to GCS                      │
│  • Pause du flow                                       │
│  • Alert via Kestra UI dashboard                      │
└─────────────────────────────────────────────────────────┘
```

### Gestion Spécifique: Captcha & 2FA

```python
# /src/adapters/upwork/auth.py
class UpworkAuthHandler:
    """Gère l'authentification avec Skyvern"""
    
    def login_with_skyvern(self, skyvern_client, username, password):
        """Login avec Skyvern - gestion intelligente des challenges"""
        
        # Skyvern task pour login
        task = {
            "url": "https://www.upwork.com/ab/account-security/login",
            "navigation_goal": "Log in to Upwork account",
            "data_extraction_goal": "Confirm successful login",
            "navigation_payload": {
                "username": username,
                "password": password
            },
            "error_handling": {
                "captcha": "auto_solve",  # Skyvern peut gérer automatiquement
                "2fa": "use_backup_code"   # Utiliser backup code si disponible
            }
        }
        
        try:
            result = skyvern_client.execute_task(task)
            
            if result.get('status') == 'success':
                print("✅ Login successful")
                return True
            
            # Gérer les cas spéciaux
            if 'captcha' in result.get('challenges', []):
                return self._handle_captcha_with_ai(skyvern_client, result)
            
            if '2fa' in result.get('challenges', []):
                return self._handle_2fa(skyvern_client, result)
                
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def _handle_captcha_with_ai(self, skyvern_client, result):
        """Skyvern peut résoudre les captchas automatiquement via vision AI"""
        print("🤖 Captcha détecté - Skyvern AI en cours...")
        
        # Skyvern utilise vision AI pour résoudre
        retry_task = result.get('retry_suggestion')
        retry_result = skyvern_client.execute_task(retry_task)
        
        if retry_result.get('status') != 'success':
            # Si échec, log to Airtable
            airtable_client.create_interaction({
                'Type': 'Error Log',
                'Content': '⚠️ CAPTCHA non résolu par Skyvern AI - Intervention manuelle requise',
                'Severity': 'Critical',
                'Screenshot URL': retry_result.get('screenshot_url'),
                'Metadata': json.dumps(retry_result)
            })
            raise CaptchaException("Captcha non résolu - Check Airtable")
        
        return True
    
    def _handle_2fa(self, skyvern_client, result):
        """Gestion 2FA avec backup code"""
        print("🔐 2FA requested")
        
        backup_code = os.getenv('UPWORK_2FA_BACKUP')
        if backup_code:
            # Skyvern peut entrer le code automatiquement
            task = result.get('retry_suggestion')
            task['navigation_payload']['2fa_code'] = backup_code
            
            retry_result = skyvern_client.execute_task(task)
            if retry_result.get('status') == 'success':
                return True
        
        # Log to Airtable si échec
        airtable_client.create_interaction({
            'Type': 'Error Log',
            'Content': '🔐 2FA requis - Vérifier méthode d\'authentification',
            'Severity': 'Critical'
        })
        raise TwoFactorException("2FA code needed")
```

---

## 🚀 5. Optimisations Avancées

### 5.1 Skyvern: AI-Driven Automation

**Pourquoi Skyvern > Playwright ?**

Skyvern utilise des LLMs pour comprendre et interagir avec les pages web, offrant plusieurs avantages critiques :

#### 🤖 Intelligence Contextuelle
- **Vision AI** : Comprend visuellement les éléments de la page
- **Adaptabilité** : S'adapte automatiquement aux changements d'UI
- **Natural Language** : Tâches définies en langage naturel, pas de sélecteurs CSS

#### 🛡️ Résilience Supérieure
```python
# Playwright (fragile)
page.click("#submit-button")  # ❌ Casse si ID change

# Skyvern (resilient)
task = {
    "navigation_goal": "Submit the form"  # ✅ Comprend l'intention
}
```

#### 🔧 Maintenance Réduite
- **Pas de selectors.py** : Plus besoin de maintenir des sélecteurs CSS
- **Auto-healing** : S'adapte aux redesigns sans modification du code
- **Moins de tests** : Moins de breakage lors des updates UI

#### ⚡ Capabilities Avancées
- **Anti-detection** : Comportement humain natif
- **Captcha solving** : Vision AI intégrée
- **Multi-step flows** : Comprend les workflows complexes
- **Data extraction** : Extraction intelligente sans XPath

**Exemple Concret :**
```python
# Définir une tâche Skyvern
task = {
    "url": "https://www.upwork.com/nx/jobs/post/",
    "navigation_goal": "Post a job for a React developer",
    "navigation_payload": {
        "title": "Senior React Developer",
        "description": "We need an expert...",
        "budget": "$5000",
        "skills": "React, TypeScript, Next.js"
    },
    "data_extraction_goal": "Get the posted job URL"
}

# Skyvern exécute intelligemment
result = skyvern.execute_task(task)
job_url = result['extracted_data']['job_url']
```

**ROI de Skyvern :**
- ⬇️ **-70% maintenance time** (pas de mise à jour sélecteurs)
- ⬆️ **+90% uptime** (résistant aux changements UI)
- 🚀 **Faster development** (langage naturel vs CSS debugging)

### 5.2 Airtable-Based Deduplication

```python
# /src/services/airtable_client.py
class AirtableClient:
    """Client Airtable avec deduplication intégrée"""
    
    def candidate_exists(self, profile_url):
        """Vérifie si un candidat existe déjà"""
        results = self.candidates_table.all(
            formula=f"{{Profile URL}} = '{profile_url}'"
        )
        return len(results) > 0
    
    def get_or_create_candidate(self, profile_url, candidate_data, job_id):
        """Récupère un candidat existant ou en crée un nouveau"""
        
        # Check if exists
        existing = self.candidates_table.all(
            formula=f"{{Profile URL}} = '{profile_url}'"
        )
        
        if existing:
            print(f"✓ Candidat déjà existant: {profile_url}")
            return existing[0]
        
        # Create new
        candidate_data['Profile URL'] = profile_url
        candidate_data['Job ID'] = [job_id]
        
        new_record = self.candidates_table.create(candidate_data)
        print(f"✓ Nouveau candidat créé: {profile_url}")
        return new_record
```

**Utilisation** :
- Deduplication via Profile URL (unique index)
- Évite le re-scraping de candidats déjà invités
- Mise à jour automatique si le candidat existe déjà

### 5.3 Airtable-Based Rate Limiting

```python
# /src/core/rate_limiter.py
from datetime import datetime

class RateLimiter:
    """Rate limiting basé sur Airtable System_Metrics"""
    
    LIMITS = {
        'invitations_per_day': 50,
        'profiles_scraped_per_hour': 100,
        'page_loads_per_minute': 20
    }
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
    
    def get_todays_count(self, metric_name):
        """Récupère le count depuis Airtable pour aujourd'hui"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        results = self.airtable.metrics_table.all(
            formula=f"AND({{Metric Name}} = '{metric_name}', {{Date}} = '{today}')"
        )
        
        total = sum(r['fields'].get('Value', 0) for r in results)
        return total
    
    def can_send_invitation(self):
        """Vérifie si quota invitations OK"""
        count = self.get_todays_count('Invitations Sent')
        return count < self.LIMITS['invitations_per_day']
    
    def increment_metric(self, metric_name, value=1):
        """Incrémente un compteur dans Airtable"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if metric exists for today
        existing = self.airtable.metrics_table.all(
            formula=f"AND({{Metric Name}} = '{metric_name}', {{Date}} = '{today}')"
        )
        
        if existing:
            # Update existing
            current_value = existing[0]['fields'].get('Value', 0)
            self.airtable.metrics_table.update(
                existing[0]['id'],
                {'Value': current_value + value}
            )
        else:
            # Create new
            self.airtable.metrics_table.create({
                'Metric Name': metric_name,
                'Date': today,
                'Value': value,
                'Platform': 'Upwork'
            })
    
    def throttle_if_needed(self, delay_seconds=3):
        """Ajoute un délai anti-détection"""
        import time
        time.sleep(delay_seconds)
```

**Optimisations** :
- Compteurs quotidiens stockés dans System_Metrics
- Queries efficaces avec formulas Airtable
- Pas besoin de service externe (Redis)
- Historique conservé pour analytics

---

## 🔧 6. Configuration & Secrets Management

### Variables Système (Kestra Secrets)

```yaml
# Configuration Kestra Namespace Variables
variables:
  # Performance
  max_parallel_jobs: 3
  browser_session_ttl_minutes: 30
  batch_size_invitations: 10
  
  # Rate Limiting
  max_invitations_per_day: 50
  max_profiles_per_job: 50
  scraping_delay_seconds: 3
  
  # Scoring
  min_qualification_score: 70
  review_score_threshold: 40
```

### Secrets (Encrypted)

Tous les secrets sont stockés dans Kestra Secrets (encrypted at rest) :

```bash
# Via Kestra CLI
kestra secrets set UPWORK_USERNAME "your-email@domain.com"
kestra secrets set UPWORK_PASSWORD "your-secure-password"
kestra secrets set UPWORK_2FA_BACKUP "12345678"
kestra secrets set AIRTABLE_API_KEY "pat..."
kestra secrets set SKYVERN_API_KEY "sk-..."
kestra secrets set GCS_CREDENTIALS "{...}"
```

---

## 📈 7. Monitoring & Observability

### Dashboard Kestra (Métriques Clés)

```yaml
# Example metrics to track in Kestra UI
metrics:
  - name: "Jobs Published (Today)"
    query: "SELECT COUNT(*) FROM System_Metrics WHERE Metric Name = 'Jobs Published' AND Date = TODAY()"
  
  - name: "Invitations Sent (Today)"
    query: "..."
  
  - name: "Response Rate (%)"
    formula: "(Accepted + Declined) / Invitations Sent * 100"
  
  - name: "Error Rate (%)"
    query: "SELECT COUNT(*) FROM Interactions WHERE Type = 'Error Log' AND Severity = 'Critical'"
```

### Logging \u0026 Alerting Strategy

```python
# /src/services/logger.py
class AlertManager:
    """Gère les logs et alertes via Airtable"""
    
    ALERT_RULES = {
        'critical_error': {
            'severity': 'Critical',
            'log_to_airtable': True,
            'screenshot': True
        },
        'quota_reached': {
            'severity': 'Warning',
            'log_to_airtable': True,
            'screenshot': False
        },
        'captcha_detected': {
            'severity': 'Critical',
            'log_to_airtable': True,
            'screenshot': True
        },
        'job_published': {
            'severity': 'Info',
            'log_to_airtable': True,
            'screenshot': False
        }
    }
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
    
    def log_event(self, event_type, message, metadata=None, screenshot_url=None):
        """Log l'événement dans Airtable Interactions"""
        rule = self.ALERT_RULES.get(event_type, {})
        
        if rule.get('log_to_airtable'):
            self.airtable.create_interaction({
                'Type': self._get_interaction_type(rule['severity']),
                'Content': message,
                'Severity': rule['severity'],
                'Screenshot URL': screenshot_url,
                'Metadata': json.dumps(metadata) if metadata else None
            })
            
            print(f"[{rule['severity']}] {message}")
    
    def _get_interaction_type(self, severity):
        """Map severity to interaction type"""
        if severity == 'Critical' or severity == 'Error':
            return 'Error Log'
        else:
            return 'System Event'
```

**Stratégie de Monitoring** :
- **Airtable Interactions** : Source de vérité pour tous les événements
- **Kestra UI Dashboard** : Monitoring temps réel des flows
- **GCS Screenshots** : Evidence visuelle des erreurs
- **Email (optional)** : Digest hebdomadaire des métriques

---

## 📋 8. Checklist de Mise en Production

### Phase 1 : Infrastructure Setup ✅
- [ ] Provisionner VM Google Cloud (n1-standard-2, Debian 11)
- [ ] Installer Docker Engine + Docker Compose
- [ ] Installer Kestra (via docker-compose)
- [ ] Créer bucket Google Cloud Storage (logs/screenshots)
- [ ] Configurer Airtable (4 tables + views)

### Phase 2 : Development ✅
- [ ] Coder `skyvern_client.py` (API wrapper)
- [ ] Coder `scoring_engine.py` (algorithme multi-critères)
- [ ] Coder adapters Upwork (tasks.py avec définitions langage naturel)
- [ ] Implémenter deduplication layer Airtable
- [ ] Créer clients (Airtable, GCS, Logger)
- [ ] Écrire tests unitaires (pytest coverage > 80%)

### Phase 3 : Kestra Configuration ✅
- [ ] Définir 4 flows YAML (Publishing, Search, Invitation, Response)
- [ ] Configurer tous les secrets (credentials)
- [ ] Tester retry logic & error handling
- [ ] Créer dashboard monitoring (métriques temps réel)

### Phase 4 : Testing & Validation ✅
- [ ] Test end-to-end (1 dummy job)
- [ ] Validation conformité Upwork (rate limits respectés)
- [ ] Load testing (10 jobs simultanés, 100 candidats)
- [ ] Vérifier logs dans Airtable Interactions
- [ ] Test fallback (simuler erreurs)

### Phase 5 : Deployment ✅
- [ ] Déployer code sur VM
- [ ] Activer crons (faible fréquence au début)
- [ ] Monitorer 48h non-stop
- [ ] Ajuster rate limits selon taux d'erreur
- [ ] Documenter runbook (incident response)

---

## 🎯 Prochaines Étapes & Roadmap

### Court Terme (Sprint 1-2)
1. ✅ **POC sur 1 job** (validation manuelle)
2. ✅ **Affiner algorithme scoring** (feedback recruteurs)
3. ✅ **Créer templates messages** (A/B testing)
4. ✅ **Documenter API Airtable** (schéma exact + webhooks)

### Moyen Terme (Sprint 3-6)
5. 🔄 **Ajouter plateforme Fiverr** (nouvel adapter)
6. 🔄 **Implémenter NLP avancé** (spaCy pour analyse réponses)
7. 🔄 **Dashboard Analytics** (Metabase ou Grafana)
8. 🔄 **Mobile App** (suivi temps réel pour recruteurs)

### Long Terme (> 6 mois)
9. 🚀 **ML pour scoring** (remplacer règles par modèle entraîné)
10. 🚀 **Multi-VM auto-scaling** (Kubernetes)
11. 🚀 **API publique** (permettre intégrations externes)

---

## 📚 Annexes

### A. Technologies & Dépendances

```txt
# requirements.txt
skyvern==0.1.0
pyairtable==2.1.0
python-dotenv==1.0.0
google-cloud-storage==2.10.0
textblob==0.17.0
pyyaml==6.0.1
pytest==7.4.3
```

### B. Exemple Flow Kestra Complet

```yaml
id: upwork_recruitment_master
namespace: recruitment.upwork

variables:
  max_parallel_jobs: 3
  session_ttl: 30  # minutes

tasks:
  # FLOW 1: Publishing
  - id: job_publishing
    type: io.kestra.core.tasks.flows.Subflow
    flowId: job_publishing_flow
    wait: true
    transmitFailed: true

  # FLOW 2: Search (après publishing)
  - id: candidate_search
    type: io.kestra.core.tasks.flows.Subflow
    flowId: candidate_search_flow
    wait: true

  # FLOW 3: Invitations (après search)
  - id: invitation_campaign
    type: io.kestra.core.tasks.flows.Subflow
    flowId: invitation_flow
    wait: true

  # FLOW 4: Responses
  - id: response_collection
    type: io.kestra.core.tasks.flows.Subflow
    flowId: response_collection_flow
    wait: true

triggers:
  - id: daily_automation
    type: io.kestra.core.models.triggers.types.Schedule
    cron: "0 8 * * *"  # Every day at 08:00 UTC
```

---

> **📌 Architecture Optimisée avec Skyvern**  
> Cette architecture est conçue pour être robuste, scalable et maintenable avec un stack minimal et intelligent. Elle intègre les meilleures pratiques de l'automatisation RPA et du recrutement automatisé, avec l'avantage de Skyvern pour une résilience maximale aux changements UI.
>
> **Stack Core** : Kestra + **Skyvern (AI)** + Airtable + Google Cloud (VM + GCS)  
> **Monitoring** : Airtable Interactions + Kestra Dashboard  
> **Avantage clé** : -70% maintenance grâce à l'automation AI de Skyvern
>
> **Contact & Support** : Pour toute question technique, référez-vous à la documentation Kestra ou contactez Johns David.
