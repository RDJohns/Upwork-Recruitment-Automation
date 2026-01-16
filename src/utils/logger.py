import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from .config import config


class ColoredFormatter(logging.Formatter):
    """Formatter pour logs avec couleurs"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [LEVEL] [TIMESTAMP] Message
        record.levelname = f"{log_color}{record.levelname}{reset}"
        record.msg = f"{log_color}{record.msg}{reset}"
        
        return super().format(record)


class RecruitmentLogger:
    """Logger structuré pour l'application de recrutement"""
    
    def __init__(self, name: str = "recruitment_automation"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure le logger avec formatage et handlers"""
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '[%(levelname)s] [%(asctime)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for persistent logs
        try:
            from pathlib import Path
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"recruitment_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_formatter = logging.Formatter(
                '[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Impossible de créer le fichier de log: {e}")
    
    def info(self, message: str, **kwargs):
        """Log niveau INFO avec metadata optionnelle"""
        if kwargs:
            message = f"{message} | Metadata: {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log niveau WARNING avec metadata optionnelle"""
        if kwargs:
            message = f"{message} | Metadata: {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log niveau ERROR avec metadata optionnelle"""
        if kwargs:
            message = f"{message} | Metadata: {kwargs}"
        self.logger.error(message)
    
    def debug(self, message: str, **kwargs):
        """Log niveau DEBUG avec metadata optionnelle"""
        if kwargs:
            message = f"{message} | Metadata: {kwargs}"
        self.logger.debug(message)
    
    def critical(self, message: str, **kwargs):
        """Log niveau CRITICAL avec metadata optionnelle"""
        if kwargs:
            message = f"{message} | Metadata: {kwargs}"
        self.logger.critical(message)
    
    def log_workflow_start(self, workflow_name: str, **context):
        """Log le début d'un workflow"""
        self.info(f"🚀 Début du workflow: {workflow_name}", **context)
    
    def log_workflow_end(self, workflow_name: str, success: bool, **context):
        """Log la fin d'un workflow"""
        status = "✅ Succès" if success else "❌ Échec"
        self.info(f"{status} du workflow: {workflow_name}", **context)
    
    def log_job_action(self, action: str, job_id: str, **details):
        """Log une action sur un job"""
        self.info(f"📋 Job {action}: {job_id}", **details)
    
    def log_candidate_action(self, action: str, candidate_id: str, **details):
        """Log une action sur un candidat"""
        self.info(f"👤 Candidat {action}: {candidate_id}", **details)
    
    def log_invitation_sent(self, candidate_id: str, job_id: str, **details):
        """Log l'envoi d'une invitation"""
        self.info(f"📧 Invitation envoyée: Candidat {candidate_id} → Job {job_id}", **details)
    
    def log_error_with_screenshot(self, error: Exception, screenshot_url: Optional[str] = None, **context):
        """Log une erreur avec capture d'écran"""
        error_msg = f"Erreur: {str(error)}"
        if screenshot_url:
            error_msg += f" | Screenshot: {screenshot_url}"
        self.error(error_msg, error_type=type(error).__name__, **context)


# Logger global
logger = RecruitmentLogger()
