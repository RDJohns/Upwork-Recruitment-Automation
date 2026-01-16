"""
Gestionnaire d'authentification Upwork avec Skyvern
"""

import os
from typing import Optional, Dict, Any
from ...utils.config import config
from ...utils.logger import logger
from ...services.skyvern_client import SkyvernClient
from .tasks import UpworkTasks


class UpworkAuthHandler:
    """Gère l'authentification Upwork via Skyvern"""
    
    def __init__(self, skyvern_client: SkyvernClient):
        self.skyvern = skyvern_client
        self._session_active = False
        self._last_check = None
    
    def is_authenticated(self) -> bool:
        """Vérifie si on est authentifié sur Upwork"""
        try:
            # Utiliser le cache si récent (< 30 minutes)
            if (self._session_active and self._last_check and 
                self._time_since_last_check() < 1800):  # 30 minutes
                return True
            
            # Vérifier via Skyvern
            task = UpworkTasks.check_authentication_task()
            result = self.skyvern.execute_task(task)
            
            if result.get('status') == 'completed':
                extracted = result.get('extracted_data', {})
                is_logged_in = extracted.get('is_logged_in', False)
                
                self._session_active = is_logged_in
                self._last_check = self._get_current_time()
                
                if is_logged_in:
                    logger.info("✅ Session Upwork active")
                else:
                    logger.warning("❌ Session Upwork inactive")
                
                return is_logged_in
            else:
                logger.error("Échec vérification authentification")
                self._session_active = False
                return False
                
        except Exception as e:
            logger.error(f"Erreur vérification authentification: {e}")
            self._session_active = False
            return False
    
    def login(self, username: str = None, password: str = None, 
              backup_code: str = None) -> bool:
        """Connexion à Upwork avec gestion des challenges"""
        try:
            # Utiliser les credentials par défaut si non fournis
            username = username or config.UPWORK_USERNAME
            password = password or config.UPWORK_PASSWORD
            backup_code = backup_code or config.UPWORK_2FA_BACKUP
            
            if not username or not password:
                logger.error("Credentials Upwork manquants")
                return False
            
            logger.info("🔐 Tentative de connexion Upwork...")
            
            # Créer la tâche de connexion
            task = UpworkTasks.login_task(username, password, backup_code)
            
            # Exécuter la tâche
            result = self.skyvern.execute_task(task)
            
            if result.get('status') == 'completed':
                extracted = result.get('extracted_data', {})
                
                if extracted.get('login_success', False):
                    self._session_active = True
                    self._last_check = self._get_current_time()
                    
                    user_name = extracted.get('user_name', 'Unknown')
                    logger.info(f"✅ Connexion réussie: {user_name}")
                    return True
                else:
                    logger.error("❌ Connexion échouée")
                    return False
            else:
                # Gérer les cas spéciaux (captcha, 2FA)
                return self._handle_login_challenges(result, username, password, backup_code)
                
        except Exception as e:
            logger.error(f"Erreur connexion Upwork: {e}")
            return False
    
    def ensure_authenticated(self, username: str = None, password: str = None, 
                           backup_code: str = None) -> bool:
        """S'assure qu'on est authentifié (connexion si nécessaire)"""
        if self.is_authenticated():
            return True
        
        return self.login(username, password, backup_code)
    
    def logout(self) -> bool:
        """Déconnexion de Upwork"""
        try:
            # Pour l'instant, on invalide juste le cache
            self._session_active = False
            self._last_check = None
            
            logger.info("🔓 Session Upwork terminée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
            return False
    
    def _handle_login_challenges(self, result: Dict[str, Any], username: str, 
                               password: str, backup_code: str) -> bool:
        """Gère les challenges de connexion (captcha, 2FA)"""
        try:
            challenges = result.get('challenges', [])
            
            if 'captcha' in challenges:
                logger.warning("🤖 CAPTCHA détecté - Skyvern AI en cours de résolution...")
                return self._handle_captcha_challenge(result, username, password, backup_code)
            
            elif '2fa' in challenges:
                logger.warning("🔐 2FA requis")
                return self._handle_2fa_challenge(result, username, password, backup_code)
            
            else:
                error_msg = result.get('error', 'Erreur inconnue')
                logger.error(f"❌ Échec connexion: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion challenges: {e}")
            return False
    
    def _handle_captcha_challenge(self, result: Dict[str, Any], username: str, 
                                 password: str, backup_code: str) -> bool:
        """Gère un challenge CAPTCHA"""
        try:
            # Skyvern utilise l'IA pour résoudre automatiquement
            retry_suggestion = result.get('retry_suggestion')
            
            if retry_suggestion:
                logger.info("🤖 Tentative de résolution CAPTCHA par Skyvern AI...")
                
                retry_result = self.skyvern.execute_task(retry_suggestion)
                
                if retry_result.get('status') == 'completed':
                    extracted = retry_result.get('extracted_data', {})
                    
                    if extracted.get('login_success', False):
                        self._session_active = True
                        self._last_check = self._get_current_time()
                        
                        logger.info("✅ CAPTCHA résolu et connexion réussie")
                        return True
                    else:
                        logger.error("❌ CAPTCHA résolu mais connexion échouée")
                        return False
                else:
                    logger.error("❌ Échec résolution CAPTCHA")
                    return False
            else:
                logger.error("❌ Pas de suggestion de retry pour CAPTCHA")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion CAPTCHA: {e}")
            return False
    
    def _handle_2fa_challenge(self, result: Dict[str, Any], username: str, 
                              password: str, backup_code: str) -> bool:
        """Gère un challenge 2FA"""
        try:
            if not backup_code:
                logger.error("❌ Code backup 2FA manquant")
                return False
            
            retry_suggestion = result.get('retry_suggestion')
            
            if retry_suggestion:
                # Ajouter le code backup à la retry suggestion
                retry_suggestion['navigation_payload']['2fa_code'] = backup_code
                
                logger.info("🔐 Envoi code backup 2FA...")
                
                retry_result = self.skyvern.execute_task(retry_suggestion)
                
                if retry_result.get('status') == 'completed':
                    extracted = retry_result.get('extracted_data', {})
                    
                    if extracted.get('login_success', False):
                        self._session_active = True
                        self._last_check = self._get_current_time()
                        
                        logger.info("✅ 2FA validé et connexion réussie")
                        return True
                    else:
                        logger.error("❌ Code 2FA invalide")
                        return False
                else:
                    logger.error("❌ Échec validation 2FA")
                    return False
            else:
                logger.error("❌ Pas de suggestion de retry pour 2FA")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion 2FA: {e}")
            return False
    
    def _time_since_last_check(self) -> int:
        """Retourne le temps en secondes depuis la dernière vérification"""
        if not self._last_check:
            return 999999
        
        return self._get_current_time() - self._last_check
    
    def _get_current_time(self) -> int:
        """Retourne le timestamp actuel"""
        import time
        return int(time.time())
    
    def get_session_info(self) -> Dict[str, Any]:
        """Retourne les informations de la session actuelle"""
        return {
            'authenticated': self._session_active,
            'last_check': self._last_check,
            'time_since_check': self._time_since_last_check() if self._last_check else None
        }
