# 🐳 Configuration Docker pour Upwork Automation

## 🎯 Objectif

Utiliser Docker pour l'isolation et la reproductibilité de l'environnement, **sans Docker Compose**.

## 📦 Prérequis

### 1. Docker Installé
```bash
# Vérifier l'installation
docker --version

# Si non installé:
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS:
# Installer Docker Desktop depuis https://www.docker.com/products/docker-desktop
```

### 2. Fichier .env Configuré
```bash
# Copier et configurer
cp .env.example .env
nano .env

# Variables obligatoires:
UPWORK_USERNAME=votre-email@domain.com
UPWORK_PASSWORD=votre-mot-de-passe
```

## 🚀 Utilisation

### 1. Construction de l'Image
```bash
# Construire l'image Docker
./docker-run.sh build

# Ou manuellement:
docker build -t upwork-automation .
```

### 2. Lancement du Conteneur
```bash
# Lancer en mode détaché
./docker-run.sh run

# Vérifier le statut
docker ps
```

### 3. Mode Interactif (Développement)
```bash
# Lancer en mode interactif
./docker-run.sh interactive

# À l'intérieur du conteneur:
python tests/test_working.py
python -m src.main
```

### 4. Tests
```bash
# Lancer les tests dans Docker
./docker-run.sh test
```

### 5. Logs
```bash
# Voir les logs en temps réel
./docker-run.sh logs

# Ou directement:
docker logs -f upwork-automation-container
```

### 6. Arrêt
```bash
# Arrêter le conteneur
./docker-run.sh stop

# Nettoyer tout
./docker-run.sh cleanup
```

## 📁 Structure des Fichiers

```
upwork-automation/
├── Dockerfile                 # Configuration de l'image
├── docker-run.sh             # Script de lancement
├── .env                      # Variables d'environnement
├── src/                      # Code source
├── tests/                    # Tests
├── logs/                     # Logs (créé par Docker)
├── storage/                  # Stockage (créé par Docker)
└── docs/DOCKER_SETUP.md     # Cette documentation
```

## 🔧 Configuration Docker

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY src/ ./src/
COPY .env.example .env

# Dossiers nécessaires
RUN mkdir -p logs tmp storage

# Environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Commande par défaut
CMD ["python", "-m", "src.main"]
```

### Volumes Docker
```bash
# .env (lecture seule)
-v "$(pwd)/.env:/app/.env:ro"

# Logs (écriture)
-v "$(pwd)/logs:/app/logs"

# Storage (écriture)
-v "$(pwd)/storage:/app/storage"
```

## 🎯 Cas d'Usage

### Développement
```bash
# Mode interactif pour le développement
./docker-run.sh interactive

# Tests rapides
./docker-run.sh test
```

### Production
```bash
# Lancement stable
./docker-run.sh build
./docker-run.sh run

# Monitoring
./docker-run.sh logs
```

### CI/CD
```bash
# Dans un pipeline GitHub Actions:
docker build -t upwork-automation .
docker run --rm upwork-automation python tests/test_working.py
```

## 📊 Avantages du Docker (sans Compose)

| Avantage | Description |
|----------|-------------|
| **Isolation** | Environnement Python isolé et reproductible |
| **Simplicité** | Script unique pour toutes les opérations |
| **Portabilité** | Fonctionne sur n'importe quelle machine avec Docker |
| **Versioning** | Image versionnée et testée |
| **Débogage** | Logs centralisés et accessibles |
| **Déploiement** | Déploiement unifié via Docker Hub |

## 🔍 Dépannage

### Problèmes Communs

**"Docker n'est pas installé"**
```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**"Port déjà utilisé"**
```bash
# Changer le port dans docker-run.sh
PORT=8081  # Modifier cette ligne
```

**"Permission denied"**
```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
# Se déconnecter et se reconnecter
```

**"Image non trouvée"**
```bash
# Construire l'image d'abord
./docker-run.sh build
```

### Debugging

```bash
# Vérifier les conteneurs
docker ps -a

# Inspecter un conteneur
docker inspect upwork-automation-container

# Entrer dans un conteneur en cours d'exécution
docker exec -it upwork-automation-container bash

# Voir les logs détaillés
docker logs --tail 100 upwork-automation-container
```

## 🚀 Bonnes Pratiques

### 1. Variables d'Environnement
```bash
# Toujours utiliser .env pour les secrets
# Ne jamais mettre de secrets dans le Dockerfile
```

### 2. Volumes
```bash
# Utiliser des volumes nommés pour la persistance
docker volume create upwork-logs
docker run -v upwork-logs:/app/logs upwork-automation
```

### 3. Réseaux
```bash
# Créer un réseau dédié si nécessaire
docker network create upwork-net
docker run --network upwork-net upwork-automation
```

### 4. Ressources
```bash
# Limiter les ressources si nécessaire
docker run --memory=512m --cpus=1 upwork-automation
```

## 📋 Commandes Rapides

```bash
# Cycle de vie complet
./docker-run.sh build && ./docker-run.sh run && ./docker-run.sh logs

# Développement
./docker-run.sh interactive

# Tests
./docker-run.sh test

# Nettoyage
./docker-run.sh cleanup
```

---

## 🎯 Conclusion

Cette configuration Docker offre :

- ✅ **Simplicité** : Un script pour tout gérer
- ✅ **Isolation** : Environnement propre et reproductible
- ✅ **Flexibilité** : Mode détaché ou interactif
- ✅ **Monitoring** : Logs accessibles et centralisés
- ✅ **Portabilité** : Fonctionne partout avec Docker

Le projet est maintenant **prêt pour Docker** sans la complexité de Docker Compose !
