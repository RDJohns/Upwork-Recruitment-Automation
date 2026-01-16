from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pyairtable import Api, Table
from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import safe_json_loads, safe_json_dumps


class AirtableClient:
    """Client Airtable avec méthodes spécialisées pour le recrutement"""
    
    def __init__(self):
        """Initialise le client Airtable"""
        if not config.AIRTABLE_API_KEY or not config.AIRTABLE_BASE_ID:
            raise ValueError("Configuration Airtable manquante")
        
        self.api = Api(config.AIRTABLE_API_KEY)
        self.base = self.api.base(config.AIRTABLE_BASE_ID)
        
        # Références aux tables
        self.jobs_table = self.base.table("Jobs")
        self.candidates_table = self.base.table("Candidates")
        self.interactions_table = self.base.table("Interactions")
        self.metrics_table = self.base.table("System_Metrics")
        
        logger.info("Client Airtable initialisé")
    
    # ===== JOBS METHODS =====
    
    def get_jobs(self, filter_formula: str = "", platform: str = "Upwork") -> List[Dict[str, Any]]:
        """Récupère les jobs avec filtre optionnel"""
        try:
            if filter_formula:
                records = self.jobs_table.all(formula=filter_formula)
            else:
                records = self.jobs_table.all()
            
            # Filtrer par plateforme si spécifié
            if platform:
                records = [r for r in records if r.get('fields', {}).get('Platform') == platform]
            
            logger.info(f"Récupéré {len(records)} jobs", platform=platform, filter=filter_formula)
            return records
            
        except Exception as e:
            logger.error(f"Erreur récupération jobs: {e}")
            return []
    
    def get_jobs_to_publish(self, platform: str = "Upwork") -> List[Dict[str, Any]]:
        """Récupère les jobs à publier"""
        filter_formula = "{Status} = 'To Publish'"
        return self.get_jobs(filter_formula, platform)
    
    def get_published_jobs(self, platform: str = "Upwork") -> List[Dict[str, Any]]:
        """Récupère les jobs publiés"""
        filter_formula = "{Status} = 'Published'"
        return self.get_jobs(filter_formula, platform)
    
    def create_job(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un nouveau job"""
        try:
            record = self.jobs_table.create(job_data)
            logger.log_job_action("créé", record['id'], job_data=job_data)
            return record
        except Exception as e:
            logger.error(f"Erreur création job: {e}", job_data=job_data)
            return None
    
    def update_job(self, job_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un job"""
        try:
            record = self.jobs_table.update(job_id, update_data)
            logger.log_job_action("mis à jour", job_id, update_data=update_data)
            return record
        except Exception as e:
            logger.error(f"Erreur mise à jour job {job_id}: {e}", update_data=update_data)
            return None
    
    # ===== CANDIDATES METHODS =====
    
    def candidate_exists(self, profile_url: str) -> bool:
        """Vérifie si un candidat existe déjà via son URL"""
        try:
            formula = f"{{Profile URL}} = '{profile_url}'"
            records = self.candidates_table.all(formula=formula)
            return len(records) > 0
        except Exception as e:
            logger.error(f"Erreur vérification existence candidat: {e}", profile_url=profile_url)
            return False
    
    def get_or_create_candidate(self, profile_url: str, candidate_data: Dict[str, Any], job_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un candidat existant ou en crée un nouveau"""
        try:
            # Vérifier si le candidat existe
            formula = f"{{Profile URL}} = '{profile_url}'"
            existing = self.candidates_table.all(formula=formula)
            
            if existing:
                logger.info(f"Candidat déjà existant: {profile_url}")
                return existing[0]
            
            # Créer le nouveau candidat
            candidate_data['Profile URL'] = profile_url
            candidate_data['Job ID'] = [job_id]  # Airtable utilise des listes pour les liens
            
            record = self.candidates_table.create(candidate_data)
            logger.log_candidate_action("créé", record['id'], profile_url=profile_url)
            return record
            
        except Exception as e:
            logger.error(f"Erreur création/récupération candidat: {e}", profile_url=profile_url)
            return None
    
    def get_candidates(self, filter_formula: str = "") -> List[Dict[str, Any]]:
        """Récupère les candidats avec filtre optionnel"""
        try:
            if filter_formula:
                records = self.candidates_table.all(formula=filter_formula)
            else:
                records = self.candidates_table.all()
            
            logger.info(f"Récupéré {len(records)} candidats", filter=filter_formula)
            return records
            
        except Exception as e:
            logger.error(f"Erreur récupération candidats: {e}")
            return []
    
    def get_qualified_candidates(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère les candidats qualifiés non invités"""
        base_filter = "AND({Qualification Status} = 'Qualified', {Invitation Status} = 'Not Invited')"
        
        if job_id:
            formula = f"AND({base_filter}, {{Job ID}} = '{job_id}')"
        else:
            formula = base_filter
        
        return self.get_candidates(formula)
    
    def update_candidate(self, candidate_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un candidat"""
        try:
            record = self.candidates_table.update(candidate_id, update_data)
            logger.log_candidate_action("mis à jour", candidate_id, update_data=update_data)
            return record
        except Exception as e:
            logger.error(f"Erreur mise à jour candidat {candidate_id}: {e}", update_data=update_data)
            return None
    
    def count_invitations_today(self) -> int:
        """Compte le nombre d'invitations envoyées aujourd'hui"""
        try:
            today = date.today().isoformat()
            formula = f"AND({{Invitation Status}} = 'Sent', {{Invited Date}} = '{today}')"
            records = self.candidates_table.all(formula=formula)
            return len(records)
        except Exception as e:
            logger.error(f"Erreur comptage invitations aujourd'hui: {e}")
            return 0
    
    # ===== INTERACTIONS METHODS =====
    
    def create_interaction(self, interaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée une nouvelle interaction"""
        try:
            # Ajouter timestamp automatique si non fourni
            if 'Timestamp' not in interaction_data:
                interaction_data['Timestamp'] = datetime.now().isoformat()
            
            record = self.interactions_table.create(interaction_data)
            logger.info(f"Interaction créée: {record['id']}", type=interaction_data.get('Type'))
            return record
        except Exception as e:
            logger.error(f"Erreur création interaction: {e}", interaction_data=interaction_data)
            return None
    
    def log_error(self, error_message: str, severity: str = "Error", 
                  job_id: Optional[str] = None, candidate_id: Optional[str] = None,
                  screenshot_url: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log une erreur dans la table Interactions"""
        interaction_data = {
            'Type': 'Error Log',
            'Content': error_message,
            'Severity': severity,
            'Screenshot URL': screenshot_url,
            'Metadata': safe_json_dumps(metadata) if metadata else None
        }
        
        # Ajouter les liens si fournis
        if job_id:
            interaction_data['Job ID'] = [job_id]
        if candidate_id:
            interaction_data['Candidate ID'] = [candidate_id]
        
        return self.create_interaction(interaction_data)
    
    def log_system_event(self, message: str, job_id: Optional[str] = None, 
                        candidate_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log un événement système"""
        interaction_data = {
            'Type': 'System Event',
            'Content': message,
            'Severity': 'Info',
            'Metadata': safe_json_dumps(metadata) if metadata else None
        }
        
        if job_id:
            interaction_data['Job ID'] = [job_id]
        if candidate_id:
            interaction_data['Candidate ID'] = [candidate_id]
        
        return self.create_interaction(interaction_data)
    
    # ===== METRICS METHODS =====
    
    def create_metric(self, metric_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée une nouvelle métrique"""
        try:
            # Ajouter date automatique si non fournie
            if 'Date' not in metric_data:
                metric_data['Date'] = date.today().isoformat()
            
            record = self.metrics_table.create(metric_data)
            logger.info(f"Métrique créée: {record['id']}", metric=metric_data.get('Metric Name'))
            return record
        except Exception as e:
            logger.error(f"Erreur création métrique: {e}", metric_data=metric_data)
            return None
    
    def get_metric_value(self, metric_name: str, target_date: Optional[str] = None) -> int:
        """Récupère la valeur d'une métrique pour une date"""
        try:
            search_date = target_date or date.today().isoformat()
            formula = f"AND({{Metric Name}} = '{metric_name}', {{Date}} = '{search_date}')"
            records = self.metrics_table.all(formula=formula)
            
            total = sum(r['fields'].get('Value', 0) for r in records)
            return total
        except Exception as e:
            logger.error(f"Erreur récupération métrique {metric_name}: {e}")
            return 0
    
    def increment_metric(self, metric_name: str, value: int = 1, 
                        platform: str = "Upwork", target_date: Optional[str] = None) -> bool:
        """Incrémente une métrique (crée ou met à jour)"""
        try:
            search_date = target_date or date.today().isoformat()
            
            # Vérifier si la métrique existe pour cette date
            formula = f"AND({{Metric Name}} = '{metric_name}', {{Date}} = '{search_date}', {{Platform}} = '{platform}')"
            existing = self.metrics_table.all(formula=formula)
            
            if existing:
                # Mettre à jour la valeur existante
                current_value = existing[0]['fields'].get('Value', 0)
                new_value = current_value + value
                self.metrics_table.update(existing[0]['id'], {'Value': new_value})
                logger.info(f"Métrique mise à jour: {metric_name} = {new_value}")
            else:
                # Créer une nouvelle métrique
                self.create_metric({
                    'Metric Name': metric_name,
                    'Value': value,
                    'Platform': platform,
                    'Date': search_date
                })
                logger.info(f"Nouvelle métrique créée: {metric_name} = {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur incrémentation métrique {metric_name}: {e}")
            return False
    
    # ===== UTILITY METHODS =====
    
    def test_connection(self) -> bool:
        """Teste la connexion à Airtable"""
        try:
            # Tenter de récupérer le premier record de chaque table
            self.jobs_table.first()
            self.candidates_table.first()
            self.interactions_table.first()
            self.metrics_table.first()
            
            logger.info("✅ Connexion Airtable réussie")
            return True
        except Exception as e:
            logger.error(f"❌ Échec connexion Airtable: {e}")
            return False
