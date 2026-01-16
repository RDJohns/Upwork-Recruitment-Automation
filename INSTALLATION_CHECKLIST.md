# 📋 Checklist d'Installation Complète

## ✅ Pré-installation

- [ ] Python 3.11+ installé (`python3 --version`)
- [ ] Docker & Docker Compose installés (`docker --version`)
- [ ] Git installé (`git --version`)
- [ ] Accès internet stable
- [ ] Comptes créés :
  - [ ] Airtable (Pro/Enterprise)
  - [ ] Skyvern (app.skyvern.com)
  - [ ] Upwork
  - [ ] Google Cloud Platform

## ✅ Configuration du Projet

- [ ] Projet cloné (`git clone`)
- [ ] Environnement virtuel créé (`python3 -m venv venv`)
- [ ] Environnement activé (`source venv/bin/activate`)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` créé et configuré
- [ ] Variables **obligatoires** configurées :
  - [ ] UPWORK_USERNAME=votre-email@domain.com
  - [ ] UPWORK_PASSWORD=votre-mot-de-passe
- [ ] Variables **optionnelles** 2FA (si automation complète souhaitée) :
  - [ ] UPWORK_2FA_METHOD=email
  - [ ] UPWORK_EMAIL_ACCESS=false
  - [ ] UPWORK_2FA_EMAIL=votre-email-2fa@domaine.com
  - [ ] UPWORK_EMAIL_PASSWORD=votre-mot-de-passe-email
- [ ] Variables d'environnement validées

## ✅ Infrastructure Airtable

- [ ] Base "Upwork Recruitment Automation" créée
- [ ] Table `Jobs` créée avec tous les champs
- [ ] Table `Candidates` créée avec tous les champs
- [ ] Table `Interactions` créée avec tous les champs
- [ ] Table `System_Metrics` créée avec tous les champs
- [ ] Vues configurées (Jobs à Publier, Candidats Qualifiés, etc.)
- [ ] API key générée et notée
- [ ] Base ID noté

## ✅ Infrastructure Google Cloud

- [ ] Google Cloud SDK installé (`gcloud --version`)
- [ ] Projet GCP créé/sélectionné
- [ ] Bucket GCS créé (`gsutil mb`)
- [ ] Service Account créé
- [ ] Permissions Storage configurées
- [ ] Clé JSON téléchargée et placée dans le projet
- [ ] Test d'upload réussi
- [ ] Nom du bucket noté dans `.env`

## ✅ Infrastructure Kestra

- [ ] Docker Compose démarré (`docker-compose up -d`)
- [ ] Services actifs (`docker-compose ps`)
- [ ] Kestra accessible (http://localhost:8080)
- [ ] Namespace `recruitment` créé
- [ ] Secrets configurés :
  - [ ] AIRTABLE_API_KEY
  - [ ] SKYVERN_API_KEY
  - [ ] UPWORK_USERNAME (obligatoire)
  - [ ] UPWORK_PASSWORD (obligatoire)
  - [ ] UPWORK_2FA_METHOD (optionnel)
  - [ ] UPWORK_EMAIL_ACCESS (optionnel)
  - [ ] UPWORK_2FA_EMAIL (optionnel)
  - [ ] UPWORK_EMAIL_PASSWORD (optionnel)
  - [ ] GCS_CREDENTIALS
- [ ] Configuration 2FA Upwork :
  - [ ] Email passcode configuré (recommandé)
  - [ ] Backup codes générés
  - [ ] Test de réception des codes
- [ ] Workflows importés
- [ ] Flows visibles dans l'interface

## ✅ Tests Finaux

- [ ] Test de configuration global (`python tests/test_config.py`)
- [ ] Test connexion Airtable
- [ ] Test connexion Skyvern
- [ ] Test scoring engine
- [ ] Job test créé dans Airtable
- [ ] Workflow de publication testé
- [ ] Logs vérifiés dans Airtable

## 🚀 Lancement en Production

Quand tous les points ci-dessus sont cochés :

1. **Démarrer les workflows automatiques**
2. **Monitorer les premières exécutions**
3. **Vérifier les métriques dans Airtable**
4. **Ajuster les rate limits si nécessaire**

---

## 🔧 Dépannage Rapide

### Problèmes Communs

**Python/Dependencies**
```bash
# Erreur de module
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Problème d'environnement
deactivate
source venv/bin/activate
```

**Docker/Kestra**
```bash
# Services ne démarrent pas
docker-compose logs kestra
docker-compose down
docker-compose up -d

# Kestra inaccessible
docker-compose restart kestra
curl http://localhost:8080/health
```

**Airtable**
```bash
# Erreur de connexion
python -c "
from src.services.airtable_client import AirtableClient
client = AirtableClient()
print(client.test_connection())
"
```

**Skyvern**
```bash
# Erreur API
python -c "
from src.services.skyvern_client import SkyvernClient
client = SkyvernClient()
print(client.test_connection())
"
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifiez cette checklist** point par point
2. **Consultez les logs** : `docker-compose logs kestra`
3. **Vérifiez Airtable** : table Interactions pour les erreurs
4. **Testez manuellement** : `python src/main.py test`

Tous les tests devraient passer avant de continuer en production.
