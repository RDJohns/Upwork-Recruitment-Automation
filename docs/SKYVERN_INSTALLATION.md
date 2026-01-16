# 📦 Installation Skyvern (Open Source)

## 🎯 Problème

Le package `skyvern==0.1.0` n'existe **pas** sur PyPI. Skyvern est un projet **open source** qui doit être installé différemment.

## 🔧 Solutions d'Installation

### Option 1: Installation depuis GitHub (Recommandée)

```bash
# Installation directe depuis le repository officiel
pip install git+https://github.com/Skyvern-AI/skyvern.git

# Ou avec une version spécifique
pip install git+https://github.com/Skyvern-AI/skyvern.git@v1.0.0
```

### Option 2: Cloner et Installer (Développement)

```bash
# Cloner le repository
git clone https://github.com/Skyvern-AI/skyvern.git
cd skyvern

# Installer en mode développement
pip install -e .

# Ou créer un package local
pip install build
pip install dist/skyvern-*.tar.gz
```

### Option 3: Utiliser l'API Directement (Alternative)

Si l'installation du client Skyvern est compliquée, vous pouvez utiliser l'API REST directement :

```python
# client_skyvern_simple.py
import requests
import os

class SimpleSkyvernClient:
    def __init__(self):
        self.api_key = os.getenv("SKYVERN_API_KEY")
        self.base_url = os.getenv("SKYVERN_BASE_URL", "https://api.skyvern.com/v1")
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def run_task(self, prompt: str, url: str = None):
        """Exécute une tâche Skyvern simple"""
        data = {"prompt": prompt}
        if url:
            data["url"] = url
        
        response = self.session.post(
            f"{self.base_url}/run/tasks",
            json=data
        )
        
        return response.json()
```

## 📋 Configuration du Projet

### Mettre à Jour requirements.txt

```bash
# Remplacer la ligne skyvern==0.1.0 par :
# skyvern @ git+https://github.com/Skyvern-AI/skyvern.git

# Ou commenteer et utiliser l'API directement
# skyvern==0.1.0  # Package pip n'existe pas encore
```

### Mettre à Jour le Code

```python
# Dans src/services/skyvern_client.py
try:
    from skyvern import SkyvernClient as OfficialSkyvernClient
    SKYVERN_AVAILABLE = True
except ImportError:
    SKYVERN_AVAILABLE = False
    # Utiliser notre client simple
    OfficialSkyvernClient = None

class SkyvernClient:
    def __init__(self):
        if SKYVERN_AVAILABLE and OfficialSkyvernClient:
            self.client = OfficialSkyvernClient()
        else:
            self.client = SimpleSkyvernClient()
    
    def run_task(self, task_data):
        return self.client.run_task(
            task_data.get("prompt"),
            task_data.get("url")
        )
```

## 🚀 Test d'Installation

### Vérifier l'Installation

```bash
# Tester l'import Skyvern
python -c "
try:
    import skyvern
    print('✅ Skyvern installé avec succès')
    print(f'Version: {skyvern.__version__}')
except ImportError as e:
    print(f'❌ Erreur import Skyvern: {e}')
    print('💡 Installez: pip install git+https://github.com/Skyvern-AI/skyvern.git')
"

# Tester Kestra
python -c "
try:
    import kestra
    print('✅ Kestra installé avec succès')
    print(f'Version: {kestra.__version__}')
except ImportError as e:
    print(f'❌ Erreur import Kestra: {e}')
    print('💡 Installez: pip install kestra==0.18.0')
"

# Tester l'API directement
python -c "
import requests
import os

api_key = os.getenv('SKYVERN_API_KEY', 'test')
if api_key != 'test':
    response = requests.post(
        'https://api.skyvern.com/v1/run/tasks',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={'prompt': 'Test connection'}
    )
    
    if response.status_code == 200:
        print('✅ API Skyvern accessible')
    else:
        print(f'❌ Erreur API: {response.status_code}')
else:
    print('⚠️ SKYVERN_API_KEY non configurée')
"
```

## 📚 Documentation Officielle

- **GitHub Repository** : https://github.com/Skyvern-AI/skyvern
- **Documentation** : https://www.skyvern.com/docs
- **API Reference** : https://www.skyvern.com/docs/api-reference
- **Installation Guide** : Vérifier le README du repository GitHub

## 🎯 Recommandation

### Pour le Développement
```bash
# Utiliser l'installation depuis GitHub
pip install git+https://github.com/Skyvern-AI/skyvern.git

# Avantages:
# - Toujours la dernière version
# - Compatible avec notre code
# - Mises à jour faciles avec pip install --upgrade
```

### Pour la Production
```bash
# Cloner et utiliser une version spécifique
git clone https://github.com/Skyvern-AI/skyvern.git
cd skyvern
git checkout v1.0.0  # Version stable
pip install -e .

# Avantages:
# - Version contrôlée
# - Possibilité de modifications locales
# - Installation reproductible
```

## 🔧 Dépannage

### Erreurs Communes

**"skyvern package not found"**
```bash
# Solution 1: Installer depuis GitHub
pip install git+https://github.com/Skyvern-AI/skyvern.git

# Solution 2: Utiliser l'API directement
# Commenteer les imports skyvern et utiliser requests
```

**"Version conflicts"**
```bash
# Désinstaller les anciennes versions
pip uninstall skyvern kestra python-dotenv

# Réinstaller proprement
pip install git+https://github.com/Skyvern-AI/skyvern.git
pip install kestra==0.18.0
pip install --upgrade python-dotenv

# Ou résoudre les conflits automatiquement
pip install --upgrade -r requirements.txt
```

**"Permission denied"**
```bash
# Utiliser --user pour l'installation
pip install --user git+https://github.com/Skyvern-AI/skyvern.git
```

---

## 🎯 Conclusion

Skyvern étant **open source**, l'installation doit se faire :
1. **Depuis GitHub** (recommandé) : `pip install git+https://github.com/Skyvern-AI/skyvern.git`
2. **En clonant** le repository pour le développement
3. **Via l'API REST** si le client Python pose problème

Le projet est maintenant configuré pour **gérer l'absence du package pip** Skyvern !
