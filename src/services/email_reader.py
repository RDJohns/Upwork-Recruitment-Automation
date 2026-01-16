"""
Service de lecture automatique d'emails pour 2FA Upwork
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import re
import time
from typing import Optional, List, Dict
from ..utils.logger import logger
from ..utils.config import config


class EmailReader:
    """Lecteur d'emails pour récupérer automatiquement les codes 2FA Upwork"""
    
    def __init__(self):
        self.imap_server = None
        self.email_address = None
        self.password = None
        self.folder = "INBOX"
        
    def connect(self, email_address: str, password: str, 
                imap_server: str = "imap.gmail.com", imap_port: int = 993) -> bool:
        """Connexion au serveur IMAP"""
        try:
            self.imap_server = imaplib.IMAP4_SSL(imap_server, imap_port)
            self.email_address = email_address
            self.password = password
            
            # Connexion
            self.imap_server.login(email_address, password)
            
            # Sélectionner la boîte de réception
            self.imap_server.select(self.folder)
            
            logger.info(f"✅ Connecté à {email_address}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion email: {e}")
            return False
    
    def get_latest_upwork_code(self, max_age_minutes: int = 10) -> Optional[str]:
        """
        Récupère le dernier code 2FA d'Upwork
        
        Args:
            max_age_minutes: Age maximum du message en minutes
            
        Returns:
            Code 2FA ou None
        """
        if not self.imap_server:
            logger.error("❌ Non connecté au serveur email")
            return None
        
        try:
            # Calculer la date limite
            date_limit = (datetime.now() - timedelta(minutes=max_age_minutes)).strftime("%d-%b-%Y")
            
            # Rechercher les emails d'Upwork
            search_criteria = f'(FROM "noreply@upwork.com" SINCE {date_limit})'
            status, messages = self.imap_server.search(None, search_criteria)
            
            if status != "OK" or not messages:
                logger.info(f"ℹ️ Aucun email Upwork trouvé depuis {max_age_minutes} minutes")
                return None
            
            # Prendre le message le plus récent
            latest_email_id = messages[-1]
            status, msg_data = self.imap_server.fetch(latest_email_id, "(RFC822)")
            
            if status != "OK":
                logger.error("❌ Erreur récupération email")
                return None
            
            # Parser l'email
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extraire le sujet et le corps
            subject = self._decode_header(msg["Subject"])
            body = self._extract_body(msg)
            
            logger.info(f"📧 Email trouvé: {subject}")
            
            # Chercher le code 2FA dans le sujet et le corps
            code = self._extract_2fa_code(subject, body)
            
            if code:
                logger.info(f"✅ Code 2FA extrait: {code}")
                return code
            else:
                logger.warning("⚠️ Aucun code 2FA trouvé dans l'email")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur lecture email: {e}")
            return None
    
    def wait_for_upwork_code(self, max_wait_seconds: int = 300, 
                           check_interval: int = 10) -> Optional[str]:
        """
        Attend l'arrivée d'un nouveau code 2FA Upwork
        
        Args:
            max_wait_seconds: Temps maximum d'attente
            check_interval: Intervalle de vérification en secondes
            
        Returns:
            Code 2FA ou None
        """
        logger.info(f"⏳ Attente code 2FA Upwork (max {max_wait_seconds}s)")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            code = self.get_latest_upwork_code(max_age_minutes=1)
            
            if code:
                return code
            
            logger.debug(f"🔄 Nouvelle vérification dans {check_interval}s...")
            time.sleep(check_interval)
        
        logger.warning(f"⏰ Timeout: aucun code reçu en {max_wait_seconds}s")
        return None
    
    def mark_email_as_read(self, email_id: int) -> bool:
        """Marque un email comme lu"""
        try:
            self.imap_server.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"❌ Erreur marquage email lu: {e}")
            return False
    
    def cleanup_old_codes(self, days_to_keep: int = 1) -> int:
        """Supprime les anciens emails de codes 2FA"""
        try:
            # Calculer la date limite
            date_limit = (datetime.now() - timedelta(days=days_to_keep)).strftime("%d-%b-%Y")
            
            # Rechercher les anciens emails
            search_criteria = f'(FROM "noreply@upwork.com" BEFORE {date_limit})'
            status, messages = self.imap_server.search(None, search_criteria)
            
            if status != "OK" or not messages:
                logger.info("ℹ️ Aucun ancien email à supprimer")
                return 0
            
            # Supprimer les messages
            deleted_count = 0
            for msg_id in messages:
                status, _ = self.imap_server.store(msg_id, '+FLAGS', '\\Deleted')
                if status == "OK":
                    deleted_count += 1
            
            # Appliquer les suppressions
            self.imap_server.expunge()
            
            logger.info(f"🗑️ {deleted_count} anciens emails supprimés")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage emails: {e}")
            return 0
    
    def _decode_header(self, header_value: str) -> str:
        """Décode un header email"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        if decoded_parts:
            return decoded_parts[0][0] if decoded_parts[0][0] else ""
        return header_value
    
    def _extract_body(self, msg) -> str:
        """Extrait le corps du message (texte ou HTML)"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True)
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        html_body = part.get_payload(decode=True)
                        # Extraire le texte du HTML (simple)
                        import re
                        text = re.sub(r'<[^>]+>', '', html_body)
                        body += text
                    except:
                        pass
        else:
            # Message simple
            try:
                body = msg.get_payload(decode=True)
            except:
                body = str(msg.get_payload())
        
        return body
    
    def _extract_2fa_code(self, subject: str, body: str) -> Optional[str]:
        """Extrait un code 2FA du sujet et du corps"""
        # Patterns de codes 2FA courants
        patterns = [
            r'\b(\d{6})\b',  # Code à 6 chiffres
            r'\b(\d{8})\b',  # Code à 8 chiffres
            r'code[:\s]*(\d{4,8})',  # "code: 123456"
            r'verification[:\s]*(\d{4,8})',  # "verification: 123456"
            r'security[:\s]*(\d{4,8})',  # "security: 123456"
            r'upwork[:\s]*code[:\s]*(\d{4,8})',  # "upwork code: 123456"
        ]
        
        # Combiner sujet et corps pour la recherche
        text_to_search = f"{subject} {body}".lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_to_search, re.IGNORECASE)
            if matches:
                return matches[0]  # Prendre le premier match
        
        return None
    
    def disconnect(self):
        """Déconnexion du serveur IMAP"""
        try:
            if self.imap_server:
                self.imap_server.close()
                self.imap_server.logout()
                logger.info("🔌 Déconnecté du serveur email")
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class Upwork2FAEmailHandler:
    """Gestionnaire spécialisé pour 2FA Upwork par email"""
    
    def __init__(self, email_address: str, password: str):
        self.email_address = email_address
        self.password = password
        self.reader = EmailReader()
    
    def get_2fa_code(self, max_wait_seconds: int = 300) -> Optional[str]:
        """
        Méthode principale pour obtenir un code 2FA Upwork
        
        Processus:
        1. Se connecter à la boîte email
        2. Attendre l'arrivée d'un email d'Upwork
        3. Extraire le code 2FA
        4. Retourner le code
        """
        logger.info("🔐 Démarrage récupération code 2FA Upwork")
        
        # Détection automatique du serveur IMAP
        domain = self.email_address.split('@')[1].lower()
        
        imap_servers = {
            'gmail.com': ('imap.gmail.com', 993),
            'yahoo.com': ('imap.mail.yahoo.com', 993),
            'outlook.com': ('outlook.office365.com', 993),
            'hotmail.com': ('outlook.office365.com', 993),
        }
        
        imap_server, imap_port = imap_servers.get(domain, ('imap.' + domain, 993))
        
        try:
            # Connexion au serveur email
            if not self.reader.connect(self.email_address, self.password, imap_server, imap_port):
                return None
            
            # Nettoyer les anciens codes
            self.reader.cleanup_old_codes(days_to_keep=1)
            
            # Attendre le nouveau code
            code = self.reader.wait_for_upwork_code(
                max_wait_seconds=max_wait_seconds,
                check_interval=5
            )
            
            return code
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion 2FA email: {e}")
            return None
        
        finally:
            self.reader.disconnect()
    
    def test_email_access(self) -> bool:
        """Test l'accès à la boîte email"""
        try:
            domain = self.email_address.split('@')[1].lower()
            imap_servers = {
                'gmail.com': ('imap.gmail.com', 993),
                'yahoo.com': ('imap.mail.yahoo.com', 993),
                'outlook.com': ('outlook.office365.com', 993),
            }
            
            imap_server, imap_port = imap_servers.get(domain, ('imap.' + domain, 993))
            
            with EmailReader() as reader:
                return reader.connect(self.email_address, self.password, imap_server, imap_port)
                
        except Exception as e:
            logger.error(f"❌ Erreur test accès email: {e}")
            return False
