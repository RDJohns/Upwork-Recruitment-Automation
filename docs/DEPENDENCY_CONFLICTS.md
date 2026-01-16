# 🔧 Gestion des Conflits de Dépendances

## 🎯 Problème Commun

L'installation peut générer des conflits de dépendances, notamment avec `python-dotenv` qui est requis par plusieurs packages avec des versions différentes.

## 📋 Conflits Fréquents

### 1. python-dotenv Version Conflict
```bash
# Erreur typique
ERROR: fastmcp 2.12.5 requires python-dotenv>=1.1.0, but you have python-dotenv 1.0.0 which is incompatible.
```

**Solution :**
```bash
# Mettre à jour python-dotenv
pip install --upgrade python-dotenv

# Ou réinstaller avec la bonne version
pip install "python-dotenv>=1.1.0"
```

### 2. requests Version Conflict
```bash
# Erreur typique
ERROR: Some packages require requests<3.0.0, but you have requests 2.32.5
```

**Solution :**
```bash
# Forcer une version compatible
pip install "requests>=2.31.0,<3.0.0"

# Ou mettre à jour tous les packages
pip install --upgrade -r requirements.txt
```

### 3. google-cloud-storage Version Conflict
```bash
# Erreur typique
ERROR: google-cloud-storage 3.8.0 requires google-auth>=2.0.0
```

**Solution :**
```bash
# Mettre à jour google-auth
pip install --upgrade google-auth

# Ou utiliser la version spécifiée
pip install google-cloud-storage==2.10.0
```

## 🛠️ Stratégies de Résolution

### Stratégie 1: Mise à Jour Automatique (Recommandée)
```bash
# Laisser pip résoudre les conflits
pip install --upgrade -r requirements.txt

# Forcer la résolution des dépendances
pip install --upgrade --force-reinstall -r requirements.txt
```

### Stratégie 2: Installation Manuelle Contrôlée
```bash
# Désinstaller les packages conflictuels
pip uninstall python-dotenv requests google-cloud-storage

# Réinstaller avec les bonnes versions
pip install "python-dotenv>=1.1.0"
pip install "requests>=2.31.0,<3.0.0"
pip install "google-cloud-storage==2.10.0"

# Installer le reste
pip install -r requirements.txt --no-deps
pip install pyairtable textblob pyyaml kestra
```

### Stratégie 3: Environnement Virtuel Propre
```bash
# Créer un environnement complètement neuf
python3 -m venv venv-clean
source venv-clean/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer avec résolution automatique
pip install --upgrade -r requirements.txt
```

## 📊 requirements.txt Optimisé

```bash
# Core dependencies avec versions flexibles
pyairtable>=2.1.0
python-dotenv>=1.1.0
google-cloud-storage>=2.10.0
textblob>=0.17.0
pyyaml>=6.0.1
requests>=2.31.0,<3.0.0

# Kestra client
kestra>=0.18.0

# Testing et développement
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.7.0
```

## 🔍 Diagnostic des Conflits

### Vérifier les Dépendances
```bash
# Voir l'arbre des dépendances
pip show python-dotenv

# Vérifier les packages qui dépendent de python-dotenv
pipdeptree -p python-dotenv

# Lister tous les conflits potentiels
pip check
```

### Analyser les Erreurs
```bash
# Détail complet de l'erreur
pip install -v python-dotenv

# Voir les dépendances requises
pip show fastmcp | grep Requires
```

## 🚀 Solutions Rapides

### Solution 1: Upgrade Forcé
```bash
# Forcer la mise à jour de tous les packages
pip install --upgrade --force-reinstall -r requirements.txt
```

### Solution 2: Ignorer les Dépendances (Dernier recours)
```bash
# Installer sans vérifier les dépendances (risqué)
pip install --no-deps -r requirements.txt

# Puis installer manuellement les dépendances critiques
pip install python-dotenv requests pyyaml
```

### Solution 3: Versions Spécifiques
```bash
# Créer un fichier requirements-lock.txt avec versions exactes
pip freeze > requirements-lock.txt

# Utiliser ce fichier pour des installations reproductibles
pip install -r requirements-lock.txt
```

## 📋 Bonnes Pratiques

### 1. Utiliser des Plages de Versions
```bash
# Au lieu de versions exactes
python-dotenv==1.0.0

# Utiliser des plages compatibles
python-dotenv>=1.1.0,<2.0.0
```

### 2. Documenter les Conflits Connus
```bash
# Dans requirements.txt
# python-dotenv>=1.1.0  # fastmcp requires >=1.1.0
# requests>=2.31.0,<3.0.0  # Compatible avec google-cloud-storage
```

### 3. Tester dans un Environnement Isolé
```bash
# Toujours tester dans un venv propre
python3 -m venv test-env
source test-env/bin/activate
pip install -r requirements.txt
```

## 🎯 Workflow Recommandé

```bash
# 1. Environnement propre
python3 -m venv venv
source venv/bin/activate

# 2. pip à jour
pip install --upgrade pip

# 3. Installation avec résolution automatique
pip install --upgrade -r requirements.txt

# 4. Vérification
pip check

# 5. Si conflit, résoudre manuellement
pip install --upgrade python-dotenv

# 6. Test final
python -c "import python_dotenv, kestra, requests; print('✅ OK')"
```

---

## 🎯 Conclusion

Les conflits de dépendances sont **normaux** avec les projets Python modernes. La clé est de :

1. ✅ **Utiliser des plages de versions** plutôt que des versions exactes
2. ✅ **Mettre à jour pip** régulièrement
3. ✅ **Utiliser des environnements virtuels** propres
4. ✅ **Documenter les conflits connus** dans requirements.txt
5. ✅ **Tester l'installation** dans un environnement isolé

Avec ces stratégies, votre installation sera **robuste et reproductible** !
