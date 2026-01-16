import requests
import json
import time
from typing import Dict, Any, Optional, List
from .utils.config import config
from .utils.logger import logger


class SkyvernClient:
    """Client Skyvern pour l'automation web intelligente"""
    
    def __init__(self):
        """Initialise le client Skyvern"""
        if not config.SKYVERN_API_KEY:
            raise ValueError("Configuration Skyvern API key manquante")
        
        self.api_key = config.SKYVERN_API_KEY
        self.base_url = config.SKYVERN_BASE_URL.rstrip('/') or 'https://api.skyvern.com/v1'
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        logger.info("Client Skyvern initialisé")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Effectue une requête API avec gestion d'erreurs"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête Skyvern: {e}", url=url, method=method)
            raise
    
    @retry_on_exception(max_retries=3, delay=2.0)
    def execute_task(self, task_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une tâche Skyvern"""
        try:
            logger.info("🤖 Exécution tâche Skyvern", task_type=task_definition.get('navigation_goal'))
            
            # Créer la tâche
            task_response = self._make_request('POST', '/tasks', task_definition)
            task_id = task_response.get('task_id')
            
            if not task_id:
                raise ValueError("Réponse Skyvern invalide: task_id manquant")
            
            logger.info(f"Tâche créée: {task_id}")
            
            # Attendre la complétion
            result = self._wait_for_completion(task_id)
            
            logger.info(f"✅ Tâche complétée: {task_id}", status=result.get('status'))
            return result
            
        except Exception as e:
            logger.error(f"Échec exécution tâche Skyvern: {e}")
            raise
    
    def _wait_for_completion(self, task_id: str, timeout: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """Attend la complétion d'une tâche avec polling"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status_response = self._make_request('GET', f'/tasks/{task_id}')
                status = status_response.get('status', 'unknown')
                
                if status == 'completed':
                    return status_response
                elif status == 'failed':
                    error_msg = status_response.get('error', 'Échec inconnu')
                    raise Exception(f"Tâche Skyvern échouée: {error_msg}")
                elif status in ['running', 'pending']:
                    logger.debug(f"Tâche en cours: {status}")
                    time.sleep(poll_interval)
                else:
                    logger.warning(f"Statut inconnu: {status}")
                    time.sleep(poll_interval)
                    
            except Exception as e:
                logger.error(f"Erreur vérification statut tâche {task_id}: {e}")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Timeout attente complétion tâche {task_id}")
    
    def ensure_authenticated(self, platform: str) -> bool:
        """Vérifie l'authentification pour une plateforme"""
        try:
            # Tâche simple pour vérifier l'authentification
            if platform.lower() == 'upwork':
                test_task = {
                    "url": "https://www.upwork.com",
                    "navigation_goal": "Check if logged in to Upwork",
                    "data_extraction_goal": "Extract user name or login status"
                }
            else:
                raise ValueError(f"Plateforme non supportée: {platform}")
            
            result = self.execute_task(test_task)
            
            # Vérifier si on est bien authentifié
            extracted_data = result.get('extracted_data', {})
            if extracted_data.get('is_logged_in', False):
                logger.info(f"✅ Authentifié sur {platform}")
                return True
            else:
                logger.warning(f"❌ Non authentifié sur {platform}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur vérification authentification {platform}: {e}")
            return False
    
    def login_to_upwork(self, username: str, password: str, backup_code: Optional[str] = None) -> bool:
        """Connexion à Upwork avec gestion 2FA"""
        try:
            login_task = {
                "url": "https://www.upwork.com/ab/account-security/login",
                "navigation_goal": "Log in to Upwork account",
                "data_extraction_goal": "Confirm successful login and extract user name",
                "navigation_payload": {
                    "username": username,
                    "password": password
                },
                "error_handling": {
                    "captcha": "auto_solve",
                    "2fa": "use_backup_code" if backup_code else "manual"
                }
            }
            
            if backup_code:
                login_task["navigation_payload"]["2fa_code"] = backup_code
            
            result = self.execute_task(login_task)
            
            # Vérifier le succès
            if result.get('status') == 'completed':
                extracted = result.get('extracted_data', {})
                if extracted.get('login_success', False):
                    logger.info("✅ Connexion Upwork réussie")
                    return True
                else:
                    logger.error("❌ Connexion Upwork échouée")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur connexion Upwork: {e}")
            return False
    
    def publish_upwork_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Publie un job sur Upwork et retourne l'URL"""
        try:
            publish_task = {
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
            
            result = self.execute_task(publish_task)
            
            if result.get('status') == 'completed':
                extracted_data = result.get('extracted_data', {})
                job_url = extracted_data.get('job_url')
                
                if job_url and self._is_valid_upwork_url(job_url):
                    logger.info(f"✅ Job publié: {job_url}")
                    return job_url
                else:
                    logger.error("URL du job invalide ou manquant")
                    return None
            else:
                logger.error("Échec publication job")
                return None
                
        except Exception as e:
            logger.error(f"Erreur publication job Upwork: {e}")
            return None
    
    def search_upwork_candidates(self, search_criteria: Dict[str, Any], max_results: int = 50) -> List[Dict[str, Any]]:
        """Recherche des candidats sur Upwork"""
        try:
            search_task = {
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
            
            result = self.execute_task(search_task)
            
            if result.get('status') == 'completed':
                candidates = result.get('extracted_data', {}).get('candidates', [])
                logger.info(f"✅ {len(candidates)} candidats trouvés")
                return candidates
            else:
                logger.error("Échec recherche candidats")
                return []
                
        except Exception as e:
            logger.error(f"Erreur recherche candidats Upwork: {e}")
            return []
    
    def send_upwork_invitation(self, candidate_profile_url: str, job_data: Dict[str, Any], 
                              message_template: str) -> bool:
        """Envoie une invitation à un candidat"""
        try:
            invitation_task = {
                "url": candidate_profile_url,
                "navigation_goal": "Send job invitation to freelancer",
                "data_extraction_goal": "Confirm invitation was sent successfully",
                "navigation_payload": {
                    "job_title": job_data.get('Title', ''),
                    "message": message_template.format(
                        name="{{candidate_name}}",  # Skyvern remplacera automatiquement
                        job_title=job_data.get('Title', ''),
                        skills=", ".join(job_data.get('Skills', []))
                    )
                }
            }
            
            result = self.execute_task(invitation_task)
            
            if result.get('status') == 'completed':
                extracted = result.get('extracted_data', {})
                if extracted.get('invitation_sent', False):
                    logger.info(f"✅ Invitation envoyée: {candidate_profile_url}")
                    return True
                else:
                    logger.error("Invitation non confirmée")
                    return False
            else:
                logger.error("Échec envoi invitation")
                return False
                
        except Exception as e:
            logger.error(f"Erreur envoi invitation: {e}")
            return False
    
    def collect_upwork_responses(self, job_url: str) -> List[Dict[str, Any]]:
        """Collecte les réponses aux invitations pour un job"""
        try:
            response_task = {
                "url": job_url,
                "navigation_goal": "Check for new responses to job invitations",
                "data_extraction_goal": "Extract all new candidate responses and messages",
                "navigation_payload": {
                    "check_responses": True,
                    "extract_messages": True
                }
            }
            
            result = self.execute_task(response_task)
            
            if result.get('status') == 'completed':
                responses = result.get('extracted_data', {}).get('responses', [])
                logger.info(f"✅ {len(responses)} nouvelles réponses")
                return responses
            else:
                logger.error("Échec collecte réponses")
                return []
                
        except Exception as e:
            logger.error(f"Erreur collecte réponses: {e}")
            return []
    
    def _is_valid_upwork_url(self, url: str) -> bool:
        """Valide qu'une URL est bien une URL Upwork"""
        return url and ("upwork.com" in url and ("/jobs/" in url or "/proposals/" in url))
    
    def get_task_screenshot(self, task_id: str) -> Optional[str]:
        """Récupère l'URL du screenshot d'une tâche"""
        try:
            result = self._make_request('GET', f'/tasks/{task_id}/screenshot')
            return result.get('screenshot_url')
        except Exception as e:
            logger.error(f"Erreur récupération screenshot {task_id}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Teste la connexion à l'API Skyvern"""
        try:
            # Simple ping ou test endpoint
            response = self._make_request('GET', '/health')
            logger.info("✅ Connexion Skyvern API réussie")
            return True
        except Exception as e:
            logger.error(f"❌ Échec connexion Skyvern API: {e}")
            return False
