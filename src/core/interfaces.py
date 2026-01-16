"""
Interfaces abstraites pour les adapters de plateforme
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class JobPoster(ABC):
    """Interface pour la publication d'offres d'emploi"""
    
    @abstractmethod
    def publish_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """
        Publie une offre d'emploi
        
        Args:
            job_data: Données du job (titre, description, compétences, etc.)
            
        Returns:
            URL du job publié ou None en cas d'échec
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        pass
    
    @abstractmethod
    def login(self, username: str, password: str, **kwargs) -> bool:
        """Connexion à la plateforme"""
        pass


class CandidateSearcher(ABC):
    """Interface pour la recherche de candidats"""
    
    @abstractmethod
    def search_candidates(self, search_criteria: Dict[str, Any], 
                         max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Recherche des candidats selon des critères
        
        Args:
            search_criteria: Critères de recherche (compétences, JSS, etc.)
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des candidats trouvés
        """
        pass
    
    @abstractmethod
    def extract_candidate_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrait le profil détaillé d'un candidat
        
        Args:
            profile_url: URL du profil du candidat
            
        Returns:
            Données détaillées du candidat ou None
        """
        pass


class CandidateInviter(ABC):
    """Interface pour l'envoi d'invitations"""
    
    @abstractmethod
    def send_invitation(self, candidate_profile_url: str, job_data: Dict[str, Any], 
                      message_template: str) -> bool:
        """
        Envoie une invitation à un candidat
        
        Args:
            candidate_profile_url: URL du profil du candidat
            job_data: Données du job
            message_template: Template du message d'invitation
            
        Returns:
            True si l'invitation a été envoyée avec succès
        """
        pass
    
    @abstractmethod
    def collect_responses(self, job_url: str) -> List[Dict[str, Any]]:
        """
        Collecte les réponses aux invitations
        
        Args:
            job_url: URL du job
            
        Returns:
            Liste des réponses reçues
        """
        pass


class PlatformAdapter(JobPoster, CandidateSearcher, CandidateInviter):
    """Interface combinée pour un adapter de plateforme complet"""
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Retourne le nom de la plateforme"""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Valide les credentials de la plateforme"""
        pass
    
    @abstractmethod
    def get_rate_limits(self) -> Dict[str, Any]:
        """Retourne les limites de taux de la plateforme"""
        pass
