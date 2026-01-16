import os
from dotenv import load_dotenv
from typing import Optional

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration centralisée de l'application"""
    
    # Airtable Configuration
    AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
    
    # Skyvern Configuration
    SKYVERN_API_KEY: str = os.getenv("SKYVERN_API_KEY", "")
    SKYVERN_BASE_URL: str = os.getenv("SKYVERN_BASE_URL", "https://api.skyvern.com/v1")
    
    # Upwork Credentials
    UPWORK_USERNAME: str = os.getenv("UPWORK_USERNAME", "")
    UPWORK_PASSWORD: str = os.getenv("UPWORK_PASSWORD", "")
    UPWORK_2FA_METHOD: str = os.getenv("UPWORK_2FA_METHOD", "email")  # email, backup_code, authenticator
    UPWORK_EMAIL_ACCESS: bool = os.getenv("UPWORK_EMAIL_ACCESS", "false").lower() == "true"
    UPWORK_2FA_EMAIL: str = os.getenv("UPWORK_2FA_EMAIL", "")
    UPWORK_EMAIL_PASSWORD: str = os.getenv("UPWORK_EMAIL_PASSWORD", "")
    
    # Google Cloud Storage
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "upwork-automation-screenshots")  # Remplacer avec votre nom unique
    GCS_CREDENTIALS_PATH: str = os.getenv("GCS_CREDENTIALS_PATH", "")
    
    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_INVITATIONS_PER_DAY: int = int(os.getenv("MAX_INVITATIONS_PER_DAY", "50"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    MAX_PARALLEL_JOBS: int = int(os.getenv("MAX_PARALLEL_JOBS", "3"))
    SESSION_TTL_MINUTES: int = int(os.getenv("SESSION_TTL_MINUTES", "30"))
    SCRAPING_DELAY_SECONDS: int = int(os.getenv("SCRAPING_DELAY_SECONDS", "3"))
    
    # Scoring Configuration
    MIN_QUALIFICATION_SCORE: int = int(os.getenv("MIN_QUALIFICATION_SCORE", "70"))
    REVIEW_SCORE_THRESHOLD: int = int(os.getenv("REVIEW_SCORE_THRESHOLD", "40"))
    
    # Rate Limiting
    MAX_PROFILES_PER_JOB: int = int(os.getenv("MAX_PROFILES_PER_JOB", "50"))
    MAX_PAGE_LOADS_PER_MINUTE: int = int(os.getenv("MAX_PAGE_LOADS_PER_MINUTE", "20"))
    MAX_INVITATIONS_PER_HOUR: int = int(os.getenv("MAX_INVITATIONS_PER_HOUR", "10"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valide que toutes les configurations requises sont présentes"""
        required_vars = [
            "AIRTABLE_API_KEY",
            "AIRTABLE_BASE_ID", 
            "SKYVERN_API_KEY",
            "UPWORK_USERNAME",
            "UPWORK_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
            return False
        
        print("✅ Configuration validée")
        return True


# Instance globale de configuration
config = Config()
