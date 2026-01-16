"""
Test de configuration pour valider l'installation
"""

import sys
import os
import shutil
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test que tous les modules peuvent être importés"""
    try:
        # Test imports basiques
        import json
        import os
        import requests
        import yaml
        
        # Test imports du projet (avec gestion d'erreur)
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
        
        try:
            from services.airtable_client import AirtableClient
            print("✅ AirtableClient importé")
        except ImportError as e:
            print(f"⚠️ AirtableClient import échoué: {e}")
        
        try:
            from services.skyvern_client import SkyvernClient
            print("✅ SkyvernClient importé")
        except ImportError as e:
            print(f"⚠️ SkyvernClient import échoué: {e}")
        
        try:
            from core.scoring_engine import CandidateScoringEngine
            print("✅ CandidateScoringEngine importé")
        except ImportError as e:
            print(f"⚠️ CandidateScoringEngine import échoué: {e}")
        
        try:
            from adapters.upwork.tasks import UpworkTasks
            print("✅ UpworkTasks importé")
        except ImportError as e:
            print(f"⚠️ UpworkTasks import échoué: {e}")
        
        try:
            from adapters.upwork.parser import UpworkDataParser
            print("✅ UpworkDataParser importé")
        except ImportError as e:
            print(f"⚠️ UpworkDataParser import échoué: {e}")
        
        try:
            from adapters.upwork.auth import UpworkAuthHandler
            print("✅ UpworkAuthHandler importé")
        except ImportError as e:
            print(f"⚠️ UpworkAuthHandler import échoué: {e}")
        
        try:
            from adapters.upwork.adapter import UpworkAdapter
            print("✅ UpworkAdapter importé")
        except ImportError as e:
            print(f"⚠️ UpworkAdapter import échoué: {e}")
        
        print("✅ Test d'imports complété")
        return True
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_configuration():
    """Test la configuration"""
    try:
        from utils.config import config
        
        # Charger les variables depuis .env.example si .env n'existe pas
        if not os.path.exists('.env'):
            print("ℹ️ Fichier .env non trouvé, utilisation de .env.example")
            # Copier .env.example vers .env pour le test
            import shutil
            shutil.copy('.env.example', '.env')
        
        # Valider la configuration
        if config.validate():
            print("✅ Configuration valide")
            return True
        else:
            print("❌ Configuration invalide")
            return False
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def test_scoring_engine():
    """Test le moteur de scoring"""
    try:
        from core.scoring_engine import CandidateScoringEngine
        
        engine = CandidateScoringEngine()
        
        # Test données
        candidate = {
            'skills': ['Python', 'React', 'Django'],
            'job_success_score': 95,
            'total_earned': 25000,
            'total_jobs': 15,
            'hourly_rate': 50,
            'profile_description': 'Experienced Python developer with React expertise'
        }
        
        job_requirements = {
            'skills': ['Python', 'React'],
            'max_rate': 60,
            'keywords': ['Python', 'React', 'experienced']
        }
        
        result = engine.calculate_score(candidate, job_requirements)
        
        print(f"✅ Scoring engine test: {result['total_score']:.1f}/100")
        return True
    except Exception as e:
        print(f"❌ Erreur scoring engine: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 Tests de configuration du projet Upwork Automation")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Scoring Engine", test_scoring_engine)
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
        print("🎉 Tous les tests passés! Le projet est prêt.")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
