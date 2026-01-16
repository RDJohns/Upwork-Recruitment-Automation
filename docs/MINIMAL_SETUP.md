# 🚀 Setup Minimal Upwork Automation

## 🎯 Objectif

Faire fonctionner le projet avec **seulement 2 variables obligatoires** :

```bash
UPWORK_USERNAME=votre-email@domain.com
UPWORK_PASSWORD=votre-mot-de-passe
```

## 📋 Comportement par Défaut

### Configuration Minimale
```bash
# .env minimal
AIRTABLE_API_KEY=patxxxxxxxxxxxxxxxxxxxxxx
AIRTABLE_BASE_ID=appxxxxxxxxxxxxxxxxxxxxxx
SKYVERN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
SKYVERN_BASE_URL=https://api.skyvern.com
UPWORK_USERNAME=votre-email@domain.com
UPWORK_PASSWORD=votre-mot-de-passe
GCS_BUCKET_NAME=upwork-automation-screenshots
GCS_CREDENTIALS_PATH=/path/to/service-account.json
```

### Flux d'Authentication

```
1. Skyvern essaie de se connecter avec username/password
2. Upwork demande 2FA (normal pour les nouvelles connexions)
3. Système détecte qu'aucune méthode 2FA n'est configurée
4. Affiche des instructions claires dans les logs
5. Retourne False (échec de connexion)
6. Utilisateur doit intervenir manuellement
```

### Messages dans les Logs

```bash
[INFO] 🔐 Tentative de connexion Upwork...
[WARNING] ⚠️ 2FA requis - Vérification méthode configurée
[WARNING] ⚠️ Configuration email 2FA incomplète - fallback vers manuel
[WARNING] ⚠️ 2FA manuel requis - intervention humaine nécessaire
[INFO] 📋 Options:
[INFO]    1. Configurer UPWORK_2FA_EMAIL et UPWORK_EMAIL_PASSWORD pour automation complète
[INFO]    2. Utiliser un backup code numérique dans UPWORK_2FA_EMAIL
[INFO]    3. Saisir manuellement le code dans l'interface Skyvern
[ERROR] ❌ Aucune méthode 2FA configurée - intervention manuelle requise
```

## 🔧 Options pour Activer l'Automation

### Option 1: Backup Code Numérique (Simple)

```bash
# Ajouter dans .env
UPWORK_2FA_EMAIL=12345678  # Code backup à 6-8 chiffres
```

**Avantages:**
- ✅ Simple à configurer
- ✅ Pas de dépendances email
- ✅ Fonctionne immédiatement

**Inconvénients:**
- ❌ Code usage unique
- ❌ Moins sécurisé
- ❌ Nécessite régénération

### Option 2: Email Automatique (Recommandé)

```bash
# Ajouter dans .env
UPWORK_2FA_METHOD=email
UPWORK_EMAIL_ACCESS=true
UPWORK_2FA_EMAIL=votre-email-2fa@domaine.com
UPWORK_EMAIL_PASSWORD=votre-mot-de-passe-email
```

**Avantages:**
- ✅ Automatisation complète
- ✅ Sécurité maximale
- ✅ Codes à usage unique automatiques

**Inconvénients:**
- ❌ Configuration plus complexe
- ❌ Dépendance service email

## 🚀 Lancement avec Setup Minimal

### 1. Installation de Base

```bash
# Cloner le projet
git clone <repository-url>
cd upwork-automation

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation de base (sans email 2FA)
pip install -r requirements.txt

# Installation avec email 2FA automation
pip install -r requirements.txt
# pip install imaplib2  # Décommenter pour email 2FA

# Note: Skyvern est open source
# pip install git+https://github.com/Skyvern-AI/skyvern.git

# Configuration minimale
cp .env.example .env
# Éditer .env avec seulement les variables obligatoires
```

### 2. Test de Configuration

```bash
# Test rapide
python tests/test_config.py

# Doit afficher:
# ✅ Configuration de base OK
# ⚠️ 2FA non configuré - intervention manuelle requise
```

### 3. Lancement

```bash
# Démarrer Kestra
docker-compose up -d

# Importer les workflows
cp workflows/*.yaml kestra/workflows/
docker-compose restart kestra

# Lancer un test
python src/main.py test
```

### 4. Résultat Attendu

Avec setup minimal, le système va :

1. ✅ **Se connecter** à Airtable
2. ✅ **Se connecter** à Skyvern
3. ✅ **Essayer** de se connecter à Upwork
4. ⚠️ **Échouer** sur 2FA (normal)
5. 📋 **Afficher** des instructions claires
6. ❌ **Retourner** False pour les opérations Upwork

## 📊 Monitoring

### Dans Airtable

- **Table Interactions** : Logs des tentatives 2FA
- **Table System_Metrics** : Métriques d'échec
- **Table Jobs** : Statuts "To Publish" non traités

### Logs Détaillés

```bash
# Voir tous les logs
tail -f logs/upwork-automation.log

# Filtrer les erreurs 2FA
grep "2FA" logs/upwork-automation.log
```

## 🔄 Passage à l'Automation Complète

Quand vous êtes prêt pour l'automation complète :

### Étape 1: Backup Code (5 minutes)

```bash
# Générer un backup code dans Upwork
# Settings → Security → Two-Factor Authentication → Generate Backup Codes
# Ajouter dans .env
echo "UPWORK_2FA_EMAIL=12345678" >> .env
```

### Étape 2: Email Automatique (30 minutes)

```bash
# Créer adresse email dédiée
# upwork-2fa@votredomaine.com

# Configurer dans Upwork
# Settings → Security → Two-Factor Authentication → Email Passcode

# Ajouter dans .env
cat >> .env << EOF
UPWORK_2FA_METHOD=email
UPWORK_EMAIL_ACCESS=true
UPWORK_2FA_EMAIL=upwork-2fa@votredomaine.com
UPWORK_EMAIL_PASSWORD=votre-mot-de-passe-email
EOF

# Installer dépendance email
pip install imaplib2
```

## 🎯 Recommandation

### Pour Développement/Test
- ✅ **Setup minimal** : Rapide pour tester le reste du système
- ✅ **Focus sur le core** : Airtable, Skyvern, workflows
- ✅ **Intervention manuelle** : Acceptable pour les tests

### Pour Production
- ✅ **Email automatique** : Robuste et sécurisé
- ✅ **Backup code** : Simple et fiable
- ❌ **Setup minimal** : Non recommandé pour production

## 📞 Support

### Problèmes Communs

**"Aucune méthode 2FA configurée"**
- Normal avec setup minimal
- Suivez les instructions dans les logs
- Configurez backup code ou email automatique

**"Connexion échouée"**
- Vérifiez UPWORK_USERNAME et UPWORK_PASSWORD
- Testez manuellement sur upwork.com
- Vérifiez les logs Skyvern

**"Module email_reader non disponible"**
- Normal avec setup minimal
- Installez : `pip install imaplib2`
- Ou configurez backup code à la place

---

## 🎯 Conclusion

Le setup minimal permet de :
- ✅ **Démarrer rapidement** avec 2 variables seulement
- ✅ **Tester le système** sans configuration complexe
- ✅ **Comprendre le flux** avant d'activer l'automation
- ✅ **Progresser vers** l'automation complète quand prêt

C'est l'approche **idéale pour le développement et les premiers tests** !
