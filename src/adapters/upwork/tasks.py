"""
Définitions des tâches Skyvern pour l'automation Upwork
"""

from typing import Dict, Any, List
from ...utils.logger import logger


class UpworkTasks:
    """Définition des tâches Skyvern pour Upwork en langage naturel"""
    
    @staticmethod
    def login_task(username: str, password: str) -> Dict[str, Any]:
        """Tâche de connexion à Upwork (sans 2FA - géré automatiquement)"""
        return {
            "url": "https://www.upwork.com/ab/account-security/login",
            "navigation_goal": "Log in to Upwork account",
            "data_extraction_goal": "Confirm successful login and extract user name",
            "navigation_payload": {
                "username": username,
                "password": password
            },
            "error_handling": {
                "captcha": "auto_solve",
                "2fa": "wait_for_automation"  # Indique que le système gérera 2FA
            }
        }
    
    @staticmethod
    def publish_job_task(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tâche de publication d'un job sur Upwork"""
        return {
            "url": "https://www.upwork.com/nx/jobs/post/",
            "navigation_goal": "Post a new job on Upwork",
            "data_extraction_goal": "Extract the posted job URL",
            "navigation_payload": {
                "job_title": job_data.get('Title', ''),
                "job_description": job_data.get('Description', ''),
                "skills": ", ".join(job_data.get('Skills', [])),
                "budget": str(job_data.get('Budget', '')),
                "contract_type": job_data.get('Contract Type', 'Hourly'),
                "duration": job_data.get('Duration', '1-3 months')
            }
        }
    
    @staticmethod
    def search_candidates_task(search_criteria: Dict[str, Any], max_results: int = 50) -> Dict[str, Any]:
        """Tâche de recherche de candidats sur Upwork"""
        return {
            "url": "https://www.upwork.com/nx/search/talents/",
            "navigation_goal": f"Search for freelancers with specific criteria",
            "data_extraction_goal": f"Extract top {max_results} candidate profiles",
            "navigation_payload": {
                "keywords": ", ".join(search_criteria.get('skills', [])),
                "job_success_score_min": search_criteria.get('min_jss', 90),
                "hourly_rate_max": search_criteria.get('max_rate', 999),
                "total_earned_min": search_criteria.get('min_earned', 1000),
                "max_results": max_results
            }
        }
    
    @staticmethod
    def send_invitation_task(candidate_profile_url: str, job_data: Dict[str, Any], 
                          message_template: str) -> Dict[str, Any]:
        """Tâche d'envoi d'invitation à un candidat"""
        return {
            "url": candidate_profile_url,
            "navigation_goal": "Send job invitation to freelancer",
            "data_extraction_goal": "Confirm invitation was sent successfully",
            "navigation_payload": {
                "job_title": job_data.get('Title', ''),
                "message": message_template.format(
                    name="{{candidate_name}}",
                    job_title=job_data.get('Title', ''),
                    skills=", ".join(job_data.get('Skills', []))
                )
            }
        }
    
    @staticmethod
    def collect_responses_task(job_url: str) -> Dict[str, Any]:
        """Tâche de collecte des réponses pour un job"""
        return {
            "url": job_url,
            "navigation_goal": "Check for new responses to job invitations",
            "data_extraction_goal": "Extract all new candidate responses and messages",
            "navigation_payload": {
                "check_responses": True,
                "extract_messages": True
            }
        }
    
    @staticmethod
    def check_authentication_task() -> Dict[str, Any]:
        """Tâche de vérification d'authentification"""
        return {
            "url": "https://www.upwork.com",
            "navigation_goal": "Check if logged in to Upwork",
            "data_extraction_goal": "Extract user name or login status"
        }
    
    @staticmethod
    def extract_candidate_profile_task(profile_url: str) -> Dict[str, Any]:
        """Tâche d'extraction détaillée d'un profil candidat"""
        return {
            "url": profile_url,
            "navigation_goal": "Extract detailed candidate profile information",
            "data_extraction_goal": "Extract name, skills, JSS, earnings, job history, portfolio",
            "navigation_payload": {
                "extract_detailed_info": True,
                "include_portfolio": True,
                "include_job_history": True
            }
        }
