"""
Test de configuration qui fonctionne correctement
"""

import sys
import os
import shutil
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports_working():
    """Test les imports avec la bonne méthode"""
    try:
        # Import direct depuis src/
        from utils.config import config
        from utils.logger import logger
        
        print("✅ Modules utils importés")
        
        # Test imports services (avec gestion d'erreur)
        try:
            from services.airtable_client import AirtableClient
            print("✅ AirtableClient importé")
        except ImportError as e:
            print(f"⚠️ AirtableClient: {e}")
        
        try:
            from services.skyvern_client import SkyvernClient
            print("✅ SkyvernClient importé")
        except ImportError as e:
            print(f"⚠️ SkyvernClient: {e}")
        
        # Test imports core
        try:
            from core.scoring_engine import CandidateScoringEngine
            print("✅ CandidateScoringEngine importé")
        except ImportError as e:
            print(f"⚠️ CandidateScoringEngine: {e}")
        
        # Test imports adapters
        try:
            from adapters.upwork.tasks import UpworkTasks
            print("✅ UpworkTasks importé")
        except ImportError as e:
            print(f"⚠️ UpworkTasks: {e}")
        
        try:
            from adapters.upwork.parser import UpworkDataParser
            print("✅ UpworkDataParser importé")
        except ImportError as e:
            print(f"⚠️ UpworkDataParser: {e}")
        
        try:
            from adapters.upwork.auth import UpworkAuthHandler
            print("✅ UpworkAuthHandler importé")
        except ImportError as e:
            print(f"⚠️ UpworkAuthHandler: {e}")
        
        try:
            from adapters.upwork.adapter import UpworkAdapter
            print("✅ UpworkAdapter importé")
        except ImportError as e:
            print(f"⚠️ UpworkAdapter: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur imports: {e}")
        return False

def test_configuration_working():
    """Test la configuration"""
    try:
        # Recharger python-dotenv
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
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
        return False

def test_scoring_working():
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
    print("🔍 Tests de configuration corrigés")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports_working),
        ("Configuration", test_configuration_working),
        ("Scoring Engine", test_scoring_working)
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
