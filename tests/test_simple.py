"""
Test simple pour valider l'installation de base
"""

import sys
import os
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_basic_imports():
    """Test les imports de base"""
    try:
        # Test imports Python standards
        import json
        import os
        import requests
        import yaml
        print("✅ Modules Python standards OK")
        
        # Test imports du projet avec gestion d'erreur
        try:
            from utils.config import config
            print("✅ Config importé")
        except ImportError as e:
            print(f"⚠️ Config import échoué: {e}")
        
        try:
            from utils.logger import logger
            print("✅ Logger importé")
        except ImportError as e:
            print(f"⚠️ Logger import échoué: {e}")
        
        # Test dépendances externes
        try:
            import pyairtable
            print("✅ pyairtable disponible")
        except ImportError as e:
            print(f"⚠️ pyairtable manquant: {e}")
        
        try:
            import google.cloud.storage
            print("✅ google-cloud-storage disponible")
        except ImportError as e:
            print(f"⚠️ google-cloud-storage manquant: {e}")
        
        try:
            import textblob
            print("✅ textblob disponible")
        except ImportError as e:
            print(f"⚠️ textblob manquant: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_configuration():
    """Test la configuration"""
    try:
        # Recharger python-dotev pour éviter les erreurs de cache
        from dotenv import load_dotenv
        load_dotenv(override=True)  # Forcer le rechargement
        
        from utils.config import config
        
        # Test variables de configuration
        print(f"✅ Airtable API Key: {'✓' if config.AIRTABLE_API_KEY else '✗'}")
        print(f"✅ Skyvern API Key: {'✓' if config.SKYVERN_API_KEY else '✗'}")
        print(f"✅ Upwork Username: {'✓' if config.UPWORK_USERNAME else '✗'}")
        print(f"✅ Upwork Password: {'✓' if config.UPWORK_PASSWORD else '✗'}")
        print(f"✅ GCS Bucket: {config.GCS_BUCKET_NAME}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        print("💡 Solution: Vérifiez le format du fichier .env")
        print("   - Pas de caractères spéciaux non échappés")
        print("   - Pas de sauts de ligne dans les valeurs")
        print("   - Utilisez des guillemets si nécessaire")
        return False

def test_basic_functionality():
    """Test les fonctionnalités de base"""
    try:
        # Import requests ici pour éviter l'erreur de portée
        import requests
        
        # Test création de fichier
        test_file = Path("test_output.txt")
        test_file.write_text("Test de fonctionnement")
        test_file.unlink()
        print("✅ Système de fichiers OK")
        
        # Test requête HTTP
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ Connexion internet OK")
        else:
            print(f"⚠️ Connexion internet: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur fonctionnalité: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 Tests simples du projet Upwork Automation")
    print("=" * 50)
    
    tests = [
        ("Imports de base", test_basic_imports),
        ("Configuration", test_configuration),
        ("Fonctionnalités de base", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Résultats: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tests de base réussis! L'installation fonctionne.")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez l'installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
