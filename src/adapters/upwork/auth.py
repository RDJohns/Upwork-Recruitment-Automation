"""
Gestionnaire d'authentification Upwork avec Skyvern
"""

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
        """Connexion à Upwork avec gestion automatique des emails 2FA"""
        try:
            # Utiliser les credentials par défaut si non fournis
            username = username or config.UPWORK_USERNAME
            password = password or config.UPWORK_PASSWORD
            
            if not username or not password:
                logger.error("Credentials Upwork manquants")
                return False
            
            logger.info("🔐 Tentative de connexion Upwork...")
            
            # Créer la tâche de connexion initiale
            task = UpworkTasks.login_task(username, password)
            
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
            
            # Gérer les challenges (2FA, CAPTCHA)
            return self._handle_login_challenges(result, username, password)
                
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
                               password: str) -> bool:
        """Gère les challenges de connexion (2FA, CAPTCHA) avec méthode automatique"""
        try:
            challenges = result.get('challenges', [])
            
            if 'captcha' in challenges:
                logger.warning("🤖 CAPTCHA détecté - Skyvern AI en cours de résolution...")
                return self._handle_captcha_challenge(result, username, password)
            
            elif '2fa' in challenges:
                logger.info("🔐 2FA requis - Vérification méthode configurée")
                
                # Utiliser la méthode configurée
                if config.UPWORK_2FA_METHOD == "email" and config.UPWORK_EMAIL_ACCESS:
                    return self._handle_2fa_email_automatic(result, username, password)
                else:
                    # Fallback vers backup code manuel
                    backup_code = config.UPWORK_2FA_EMAIL if '@' in config.UPWORK_2FA_EMAIL else config.UPWORK_2FA_EMAIL
                    return self._handle_2fa_manual(result, username, password, backup_code)
            
            else:
                error_msg = result.get('error', 'Erreur inconnue')
                logger.error(f"❌ Échec connexion: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion challenges: {e}")
            return False
    
    def _handle_2fa_email_automatic(self, result: Dict[str, Any], username: str, 
                                   password: str) -> bool:
        """Gère 2FA avec lecture automatique d'email"""
        try:
            # Vérifier que la configuration email est complète
            if not config.UPWORK_2FA_EMAIL or not config.UPWORK_EMAIL_PASSWORD:
                logger.warning("⚠️ Configuration email 2FA incomplète - fallback vers manuel")
                return self._handle_2fa_manual_fallback(result, username, password)
            
            logger.info("📧 Démarrage lecture automatique email 2FA...")
            
            # Import dynamique pour éviter les erreurs si module non disponible
            try:
                from ...services.email_reader import Upwork2FAEmailHandler
            except ImportError as e:
                logger.error(f"❌ Module email_reader non disponible: {e}")
                logger.info("💡 Installez: pip install imaplib2")
                return self._handle_2fa_manual_fallback(result, username, password)
            
            # Créer le gestionnaire d'email
            email_handler = Upwork2FAEmailHandler(
                config.UPWORK_2FA_EMAIL, 
                config.UPWORK_EMAIL_PASSWORD
            )
            
            # Tester l'accès email d'abord
            if not email_handler.test_email_access():
                logger.error("❌ Échec accès à la boîte email 2FA - fallback vers manuel")
                return self._handle_2fa_manual_fallback(result, username, password)
            
            # Attendre et récupérer le code automatiquement
            code = email_handler.get_2fa_code(max_wait_seconds=120)
            
            if code:
                logger.info(f"✅ Code 2FA récupéré automatiquement: {code}")
                return self._submit_2fa_code(result, code)
            else:
                logger.error("❌ Aucun code 2FA reçu automatiquement - fallback vers manuel")
                return self._handle_2fa_manual_fallback(result, username, password)
                
        except Exception as e:
            logger.error(f"❌ Erreur gestion 2FA email automatique: {e} - fallback vers manuel")
            return self._handle_2fa_manual_fallback(result, username, password)
    
    def _handle_2fa_manual_fallback(self, result: Dict[str, Any], username: str, 
                                   password: str) -> bool:
        """Fallback manuel quand l'automation email n'est pas disponible"""
        logger.warning("⚠️ 2FA manuel requis - intervention humaine nécessaire")
        logger.info("📋 Options:")
        logger.info("   1. Configurer UPWORK_2FA_EMAIL et UPWORK_EMAIL_PASSWORD pour automation complète")
        logger.info("   2. Utiliser un backup code numérique dans UPWORK_2FA_EMAIL")
        logger.info("   3. Saisir manuellement le code dans l'interface Skyvern")
        
        # Essayer avec backup code si disponible
        backup_code = config.UPWORK_2FA_EMAIL
        if backup_code and backup_code.isdigit():
            logger.info(f"🔐 Tentative avec backup code numérique: {backup_code}")
            return self._handle_2fa_manual(result, username, password, backup_code)
        
        # Retourner False pour indiquer l'échec
        logger.error("❌ Aucune méthode 2FA configurée - intervention manuelle requise")
        return False
    
    def _submit_2fa_code(self, result: Dict[str, Any], code: str) -> bool:
        """Soumet le code 2FA à Upwork"""
        try:
            retry_suggestion = result.get('retry_suggestion')
            
            if retry_suggestion:
                retry_suggestion['navigation_payload']['2fa_code'] = code
                retry_suggestion['navigation_payload']['2fa_method'] = 'manual_code'
                
                logger.info(f"🔐 Soumission code 2FA: {code}")
                
                retry_result = self.skyvern.execute_task(retry_suggestion)
                
                if retry_result.get('status') == 'completed':
                    extracted = retry_result.get('extracted_data', {})
                    
                    if extracted.get('login_success', False):
                        self._session_active = True
                        self._last_check = self._get_current_time()
                        
                        logger.info("✅ 2FA validé avec succès")
                        return True
                    else:
                        logger.error("❌ Code 2FA invalide")
                        return False
                else:
                    logger.error("❌ Échec soumission code 2FA")
                    return False
            else:
                logger.error("❌ Pas de suggestion de retry pour 2FA")
                return False
                
        except Exception as e:
            logger.error(f"Erreur soumission code 2FA: {e}")
            return False
    
    def _handle_2fa_manual(self, result: Dict[str, Any], username: str, 
                           password: str, backup_code: str) -> bool:
        """Gère 2FA avec backup code manuel (fallback)"""
        try:
            if not backup_code:
                logger.warning("⚠️ Backup code 2FA non fourni")
                logger.info("💡 Pour configurer un backup code:")
                logger.info("   UPWORK_2FA_EMAIL=12345678  # Code numérique à 6-8 chiffres")
                logger.info("   Ou configurer l'automation email complète:")
                logger.info("   UPWORK_2FA_METHOD=email")
                logger.info("   UPWORK_EMAIL_ACCESS=true")
                logger.info("   UPWORK_2FA_EMAIL=votre-email-2fa@domaine.com")
                logger.info("   UPWORK_EMAIL_PASSWORD=votre-mot-de-passe-email")
                return False
            
            retry_suggestion = result.get('retry_suggestion')
            
            if retry_suggestion:
                retry_suggestion['navigation_payload']['2fa_code'] = backup_code
                retry_suggestion['navigation_payload']['2fa_method'] = 'backup_code'
                
                logger.info(f"🔐 Utilisation backup code manuel: {backup_code}")
                
                retry_result = self.skyvern.execute_task(retry_suggestion)
                
                if retry_result.get('status') == 'completed':
                    extracted = retry_result.get('extracted_data', {})
                    
                    if extracted.get('login_success', False):
                        self._session_active = True
                        self._last_check = self._get_current_time()
                        
                        logger.info("✅ 2FA backup validé")
                        return True
                    else:
                        logger.error("❌ Backup code 2FA invalide")
                        return False
                else:
                    logger.error("❌ Échec validation backup code")
                    return False
            else:
                logger.error("❌ Pas de suggestion de retry pour 2FA")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion backup code: {e}")
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
        """Gère un challenge 2FA avec email passcode ou backup code"""
        try:
            # Vérifier si c'est un email passcode (méthode préférée)
            if backup_code and '@' in backup_code:
                logger.info("🔧 Utilisation email passcode pour 2FA")
                return self._handle_email_passcode_2fa(result, backup_code)
            
            # Sinon, utiliser le backup code numérique traditionnel
            elif backup_code and backup_code.isdigit():
                logger.info("🔐 Utilisation backup code numérique pour 2FA")
                return self._handle_backup_code_2fa(result, backup_code)
            
            else:
                logger.error("❌ Aucun méthode 2FA valide configurée")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion 2FA: {e}")
            return False
    
    def _handle_email_passcode_2fa(self, result: Dict[str, Any], backup_email: str) -> bool:
        """Gère 2FA avec email passcode (méthode préférée)"""
        try:
            retry_suggestion = result.get('retry_suggestion')
            
            if retry_suggestion:
                # Configurer pour utiliser l'email passcode
                retry_suggestion['navigation_payload']['2fa_method'] = 'email_passcode'
                retry_suggestion['navigation_payload']['2fa_email'] = backup_email
                
                logger.info(f"📧 Envoi code vers: {backup_email}")
                
                retry_result = self.skyvern.execute_task(retry_suggestion)
                
                if retry_result.get('status') == 'completed':
                    extracted = retry_result.get('extracted_data', {})
                    if extracted.get('login_success', False):
                        self._session_active = True
                        self._last_check = self._get_current_time()
                        
                        logger.info("✅ 2FA email passcode validé avec succès")
                        return True
                    else:
                        logger.error("❌ Email passcode invalide")
                        return False
                else:
                    logger.error("❌ Échec validation email passcode")
                    return False
            else:
                logger.error("❌ Pas de suggestion de retry pour 2FA email")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion 2FA email: {e}")
            return False
    
    def _handle_backup_code_2fa(self, result: Dict[str, Any], backup_code: str) -> bool:
        """Gère 2FA avec backup code numérique (fallback)"""
        try:
            retry_suggestion = result.get('retry_suggestion')
            
            if retry_suggestion:
                retry_suggestion['navigation_payload']['2fa_code'] = backup_code
                
                logger.info("🔐 Envoi backup code numérique")
                
                retry_result = self.skyvern.execute_task(retry_suggestion)
                
                if retry_result.get('status') == 'completed':
                    extracted = retry_result.get('extracted_data', {})
                    if extracted.get('login_success', False):
                        self._session_active = True
                        self._last_check = self._get_current_time()
                        
                        logger.info("✅ 2FA backup code validé")
                        return True
                    else:
                        logger.error("❌ Backup code invalide")
                        return False
                else:
                    logger.error("❌ Échec validation backup code")
                    return False
            else:
                logger.error("❌ Pas de suggestion de retry pour 2FA")
                return False
                
        except Exception as e:
            logger.error(f"Erreur gestion backup code: {e}")
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
