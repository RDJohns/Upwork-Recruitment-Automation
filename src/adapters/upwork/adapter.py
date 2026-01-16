"""
Adapter Upwork complet implémentant les interfaces de plateforme
"""

from typing import Dict, Any, List, Optional
from ...core.interfaces import PlatformAdapter
from ...services.skyvern_client import SkyvernClient
from ...utils.logger import logger
from .tasks import UpworkTasks
from .parser import UpworkDataParser
from .auth import UpworkAuthHandler


class UpworkAdapter(PlatformAdapter):
    """Adapter Upwork complet utilisant Skyvern pour l'automation"""
    
    def __init__(self, skyvern_client: SkyvernClient):
        self.skyvern = skyvern_client
        self.auth_handler = UpworkAuthHandler(skyvern_client)
        self.parser = UpworkDataParser()
        
        logger.info("Adapter Upwork initialisé")
    
    # ===== JobPoster Interface =====
    
    def publish_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Publie une offre d'emploi sur Upwork"""
        try:
            if not self.ensure_authenticated():
                logger.error("❌ Non authentifié - impossible de publier le job")
                return None
            
            logger.info(f"📋 Publication job: {job_data.get('Title', 'Sans titre')}")
            
            # Créer la tâche de publication
            task = UpworkTasks.publish_job_task(job_data)
            
            # Exécuter la tâche
            result = self.skyvern.execute_task(task)
            
            # Parser le résultat pour extraire l'URL
            job_url = self.parser.parse_job_publication_result(result)
            
            if job_url:
                logger.info(f"✅ Job publié: {job_url}")
                return job_url
            else:
                logger.error("❌ Échec publication job")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur publication job: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Vérifie si on est authentifié sur Upwork"""
        return self.auth_handler.is_authenticated()
    
    def login(self, username: str, password: str, **kwargs) -> bool:
        """Connexion à Upwork"""
        backup_code = kwargs.get('backup_code')
        return self.auth_handler.login(username, password, backup_code)
    
    # ===== CandidateSearcher Interface =====
    
    def search_candidates(self, search_criteria: Dict[str, Any], 
                         max_results: int = 50) -> List[Dict[str, Any]]:
        """Recherche des candidats sur Upwork"""
        try:
            if not self.ensure_authenticated():
                logger.error("❌ Non authentifié - impossible de rechercher des candidats")
                return []
            
            logger.info(f"🔍 Recherche candidats: {max_results} max")
            
            # Créer la tâche de recherche
            task = UpworkTasks.search_candidates_task(search_criteria, max_results)
            
            # Exécuter la tâche
            result = self.skyvern.execute_task(task)
            
            # Parser les résultats
            candidates = self.parser.parse_search_results(result)
            
            logger.info(f"✅ {len(candidates)} candidats trouvés")
            return candidates
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche candidats: {e}")
            return []
    
    def extract_candidate_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """Extrait le profil détaillé d'un candidat"""
        try:
            if not self.ensure_authenticated():
                logger.error("❌ Non authentifié - impossible d'extraire le profil")
                return None
            
            logger.info(f"👤 Extraction profil: {profile_url}")
            
            # Créer la tâche d'extraction
            task = UpworkTasks.extract_candidate_profile_task(profile_url)
            
            # Exécuter la tâche
            result = self.skyvern.execute_task(task)
            
            # Parser le profil
            profile = self.parser.parse_candidate_profile(result)
            
            if profile['name']:
                logger.info(f"✅ Profil extrait: {profile['name']}")
                return profile
            else:
                logger.warning("⚠️ Profil vide ou invalide")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur extraction profil: {e}")
            return None
    
    # ===== CandidateInviter Interface =====
    
    def send_invitation(self, candidate_profile_url: str, job_data: Dict[str, Any], 
                      message_template: str) -> bool:
        """Envoie une invitation à un candidat"""
        try:
            if not self.ensure_authenticated():
                logger.error("❌ Non authentifié - impossible d'envoyer l'invitation")
                return False
            
            logger.info(f"📧 Envoi invitation: {candidate_profile_url}")
            
            # Créer la tâche d'invitation
            task = UpworkTasks.send_invitation_task(candidate_profile_url, job_data, message_template)
            
            # Exécuter la tâche
            result = self.skyvern.execute_task(task)
            
            # Parser le résultat
            success = self.parser.parse_invitation_result(result)
            
            if success:
                logger.info(f"✅ Invitation envoyée: {candidate_profile_url}")
                return True
            else:
                logger.error(f"❌ Échec invitation: {candidate_profile_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur envoi invitation: {e}")
            return False
    
    def collect_responses(self, job_url: str) -> List[Dict[str, Any]]:
        """Collecte les réponses aux invitations"""
        try:
            if not self.ensure_authenticated():
                logger.error("❌ Non authentifié - impossible de collecter les réponses")
                return []
            
            logger.info(f"📨 Collecte réponses: {job_url}")
            
            # Créer la tâche de collecte
            task = UpworkTasks.collect_responses_task(job_url)
            
            # Exécuter la tâche
            result = self.skyvern.execute_task(result)
            
            # Parser les réponses
            responses = self.parser.parse_responses(result)
            
            logger.info(f"✅ {len(responses)} réponses collectées")
            return responses
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte réponses: {e}")
            return []
    
    # ===== PlatformAdapter Interface =====
    
    def get_platform_name(self) -> str:
        """Retourne le nom de la plateforme"""
        return "Upwork"
    
    def validate_credentials(self) -> bool:
        """Valide les credentials Upwork"""
        try:
            return self.ensure_authenticated()
        except Exception as e:
            logger.error(f"❌ Erreur validation credentials: {e}")
            return False
    
    def get_rate_limits(self) -> Dict[str, Any]:
        """Retourne les limites de taux Upwork"""
        return {
            'max_invitations_per_day': 50,
            'max_profiles_scraped_per_hour': 100,
            'max_page_loads_per_minute': 20,
            'recommended_delays': {
                'between_invitations': 5,  # secondes
                'between_profile_scrapes': 3,  # secondes
                'between_job_publishing': 10  # secondes
            }
        }
    
    # ===== Méthodes utilitaires =====
    
    def ensure_authenticated(self, **kwargs) -> bool:
        """S'assure qu'on est authentifié (connexion si nécessaire)"""
        return self.auth_handler.ensure_authenticated(**kwargs)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Retourne les informations de session"""
        return self.auth_handler.get_session_info()
    
    def logout(self) -> bool:
        """Déconnexion de Upwork"""
        return self.auth_handler.logout()
    
    # ===== Méthodes spécifiques Upwork =====
    
    def search_by_skills(self, skills: List[str], min_jss: int = 90, 
                        max_rate: float = 999, max_results: int = 50) -> List[Dict[str, Any]]:
        """Recherche spécifique par compétences"""
        search_criteria = {
            'skills': skills,
            'min_jss': min_jss,
            'max_rate': max_rate
        }
        return self.search_candidates(search_criteria, max_results)
    
    def get_candidate_score(self, candidate_data: Dict[str, Any], 
                          job_requirements: Dict[str, Any]) -> float:
        """Calcule un score de compatibilité simple (utilise le scoring engine externe pour plus de détails)"""
        # Implémentation simple - le scoring détaillé est dans scoring_engine.py
        score = 0.0
        
        # Correspondance des compétences
        candidate_skills = set(candidate_data.get('skills', []))
        required_skills = set(job_requirements.get('skills', []))
        
        if required_skills:
            match_ratio = len(candidate_skills & required_skills) / len(required_skills)
            score += match_ratio * 40  # 40% pour les compétences
        
        # Job Success Score
        jss = candidate_data.get('job_success_score', 0)
        score += min(jss, 100) * 0.2  # 20% pour le JSS
        
        # Compatibilité tarifaire
        candidate_rate = candidate_data.get('hourly_rate', 0)
        max_budget = job_requirements.get('max_rate', 999)
        
        if candidate_rate <= max_budget:
            score += 20  # 20% si compatible
        elif candidate_rate <= max_budget * 1.2:
            score += 10  # 10% si légèrement au-dessus
        
        # Expérience
        total_earned = candidate_data.get('total_earned', 0)
        if total_earned > 10000:
            score += 20  # 20% si bonne expérience
        
        return min(score, 100)
