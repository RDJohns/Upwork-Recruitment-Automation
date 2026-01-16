#!/bin/bash

# Script de lancement Docker pour Upwork Automation
# Usage: ./docker-run.sh [command]

set -e

# Configuration
IMAGE_NAME="upwork-automation"
CONTAINER_NAME="upwork-automation-container"
PORT=8080

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'aide
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier si Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé. Veuillez installer Docker d'abord."
        exit 1
    fi
    
    log_success "Docker est installé"
}

# Construire l'image Docker
build_image() {
    log_info "Construction de l'image Docker..."
    
    if docker images | grep -q "$IMAGE_NAME"; then
        log_warning "L'image $IMAGE_NAME existe déjà. Suppression de l'ancienne image..."
        docker rmi "$IMAGE_NAME" 2>/dev/null || true
    fi
    
    docker build -t "$IMAGE_NAME" .
    
    if [ $? -eq 0 ]; then
        log_success "Image Docker construite avec succès"
    else
        log_error "Échec de la construction de l'image Docker"
        exit 1
    fi
}

# Lancer le conteneur
run_container() {
    local command=${1:-"python -m src.main"}
    
    log_info "Lancement du conteneur Docker..."
    
    # Arrêter et supprimer le conteneur existant
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        log_warning "Arrêt du conteneur existant..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
    fi
    
    # Lancer le nouveau conteneur
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -p "$PORT:8080" \
        -v "$(pwd)/.env:/app/.env:ro" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/storage:/app/storage" \
        -e PYTHONPATH=/app \
        -e PYTHONUNBUFFERED=1 \
        "$IMAGE_NAME" \
        $command
    
    if [ $? -eq 0 ]; then
        log_success "Conteneur lancé avec succès"
        log_info "Conteneur: $CONTAINER_NAME"
        log_info "Port: $PORT"
        log_info "Logs: docker logs -f $CONTAINER_NAME"
    else
        log_error "Échec du lancement du conteneur"
        exit 1
    fi
}

# Lancer en mode interactif
run_interactive() {
    log_info "Lancement du conteneur en mode interactif..."
    
    # Arrêter le conteneur existant
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker stop "$CONTAINER_NAME"
    fi
    
    docker run -it --rm \
        --name "${CONTAINER_NAME}-interactive" \
        -v "$(pwd)/.env:/app/.env:ro" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/storage:/app/storage" \
        -e PYTHONPATH=/app \
        -e PYTHONUNBUFFERED=1 \
        "$IMAGE_NAME" \
        bash
}

# Lancer les tests
run_tests() {
    log_info "Lancement des tests dans le conteneur..."
    
    docker run --rm \
        --name "${CONTAINER_NAME}-tests" \
        -v "$(pwd)/.env:/app/.env:ro" \
        -v "$(pwd)/tests:/app/tests" \
        -e PYTHONPATH=/app \
        -e PYTHONUNBUFFERED=1 \
        "$IMAGE_NAME" \
        python tests/test_working.py
}

# Voir les logs
show_logs() {
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker logs -f "$CONTAINER_NAME"
    else
        log_error "Le conteneur $CONTAINER_NAME n'est pas en cours d'exécution"
        exit 1
    fi
}

# Arrêter le conteneur
stop_container() {
    if docker ps | grep -q "$CONTAINER_NAME"; then
        log_info "Arrêt du conteneur..."
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        log_success "Conteneur arrêté et supprimé"
    else
        log_warning "Le conteneur $CONTAINER_NAME n'est pas en cours d'exécution"
    fi
}

# Nettoyer les ressources
cleanup() {
    log_info "Nettoyage des ressources Docker..."
    
    # Arrêter les conteneurs
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker stop "${CONTAINER_NAME}-interactive" 2>/dev/null || true
    docker stop "${CONTAINER_NAME}-tests" 2>/dev/null || true
    
    # Supprimer les conteneurs
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}-interactive" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}-tests" 2>/dev/null || true
    
    # Supprimer l'image
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    
    log_success "Nettoyage terminé"
}

# Afficher l'aide
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build       - Construire l'image Docker"
    echo "  run         - Lancer le conteneur en mode détaché"
    echo "  interactive - Lancer le conteneur en mode interactif"
    echo "  test        - Lancer les tests dans le conteneur"
    echo "  logs        - Afficher les logs du conteneur"
    echo "  stop        - Arrêter le conteneur"
    echo "  cleanup     - Nettoyer toutes les ressources Docker"
    echo "  help        - Afficher cette aide"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 run"
    echo "  $0 interactive"
    echo "  $0 test"
    echo "  $0 logs"
    echo "  $0 stop"
}

# Point d'entrée principal
main() {
    case "${1:-help}" in
        "build")
            check_docker
            build_image
            ;;
        "run")
            check_docker
            run_container "${2:-}"
            ;;
        "interactive")
            check_docker
            run_interactive
            ;;
        "test")
            check_docker
            run_tests
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_container
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Exécuter la fonction principale avec tous les arguments
main "$@"
