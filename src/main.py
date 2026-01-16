#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application d'automatisation de recrutement Upwork
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire src au Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config
from utils.logger import logger
from services.airtable_client import AirtableClient
from services.skyvern_client import SkyvernClient
from core.scoring_engine import CandidateScoringEngine


def test_configuration():
    """Teste la configuration de tous les services"""
    logger.info("🔍 Test de la configuration...")
    
    # Valider la configuration
    if not config.validate():
        logger.error("❌ Configuration invalide")
        return False
    
    # Tester Airtable
    try:
        airtable = AirtableClient()
        if airtable.test_connection():
            logger.info("✅ Airtable connecté")
        else:
            logger.error("❌ Échec connexion Airtable")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur Airtable: {e}")
        return False
    
    # Tester Skyvern
    try:
        skyvern = SkyvernClient()
        if skyvern.test_connection():
            logger.info("✅ Skyvern connecté")
        else:
            logger.error("❌ Échec connexion Skyvern")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur Skyvern: {e}")
        return False
    
    logger.info("✅ Tous les services sont configurés correctement")
    return True


def run_job_publishing():
    """Exécute le workflow de publication de jobs"""
    logger.log_workflow_start("Job Publishing")
    
    try:
        airtable = AirtableClient()
        skyvern = SkyvernClient()
        
        # Récupérer les jobs à publier
        jobs_to_publish = airtable.get_jobs_to_publish()
        
        if not jobs_to_publish:
            logger.info("ℹ️ Aucun job à publier")
            return True
        
        logger.info(f"📋 {len(jobs_to_publish)} jobs à publier")
        
        # S'assurer d'être authentifié sur Upwork
        if not skyvern.ensure_authenticated("upwork"):
            logger.error("❌ Échec authentification Upwork")
            return False
        
        published_count = 0
        for job in jobs_to_publish:
            job_data = job['fields']
            job_id = job['id']
            
            try:
                logger.log_job_action("publication en cours", job_id, title=job_data.get('Title'))
                
                # Publier le job
                job_url = skyvern.publish_upwork_job(job_data)
                
                if job_url:
                    # Mettre à jour Airtable
                    airtable.update_job(job_id, {
                        'Status': 'Published',
                        'Upwork URL': job_url,
                        'Published Date': datetime.now().isoformat()
                    })
                    
                    # Logger l'événement
                    airtable.log_system_event(
                        f"Job publié avec succès: {job_url}",
                        job_id=job_id
                    )
                    
                    # Incrémenter la métrique
                    airtable.increment_metric('Jobs Published')
                    
                    published_count += 1
                    logger.log_job_action("publié", job_id, url=job_url)
                else:
                    logger.error(f"❌ Échec publication job {job_id}")
                    airtable.log_error(
                        "Échec publication job",
                        job_id=job_id,
                        severity="Error"
                    )
                
            except Exception as e:
                logger.error(f"❌ Erreur publication job {job_id}: {e}")
                airtable.log_error(
                    f"Erreur publication job: {str(e)}",
                    job_id=job_id,
                    severity="Error"
                )
        
        logger.log_workflow_end("Job Publishing", True, published_jobs=published_count)
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur workflow Job Publishing: {e}")
        logger.log_workflow_end("Job Publishing", False, error=str(e))
        return False


def run_candidate_search():
    """Exécute le workflow de recherche de candidats"""
    logger.log_workflow_start("Candidate Search")
    
    try:
        airtable = AirtableClient()
        skyvern = SkyvernClient()
        scoring_engine = CandidateScoringEngine()
        
        # Récupérer les jobs publiés
        published_jobs = airtable.get_published_jobs()
        
        if not published_jobs:
            logger.info("ℹ️ Aucun job publié à traiter")
            return True
        
        logger.info(f"📋 Recherche pour {len(published_jobs)} jobs publiés")
        
        total_candidates_found = 0
        
        for job in published_jobs:
            job_data = job['fields']
            job_id = job['id']
            
            try:
                logger.info(f"🔍 Recherche candidats pour job: {job_data.get('Title')}")
                
                # Définir les critères de recherche
                search_criteria = {
                    'skills': job_data.get('Skills', []),
                    'min_jss': 90,
                    'max_rate': 999,  # À adapter selon le budget
                    'min_earned': 1000
                }
                
                # Rechercher des candidats
                candidates = skyvern.search_upwork_candidates(
                    search_criteria, 
                    max_results=config.MAX_PROFILES_PER_JOB
                )
                
                if not candidates:
                    logger.info(f"ℹ️ Aucun candidat trouvé pour job {job_id}")
                    continue
                
                logger.info(f"👤 {len(candidates)} candidats trouvés pour job {job_id}")
                
                # Traiter chaque candidat
                processed_count = 0
                for candidate in candidates:
                    try:
                        profile_url = candidate.get('profile_url')
                        if not profile_url:
                            continue
                        
                        # Vérifier si le candidat existe déjà
                        if airtable.candidate_exists(profile_url):
                            continue
                        
                        # Préparer les données du candidat
                        candidate_data = {
                            'Name': candidate.get('name', ''),
                            'Profile URL': profile_url,
                            'Platform': 'Upwork',
                            'Qualification Status': 'To Review',
                            'Invitation Status': 'Not Invited',
                            'Hourly Rate': candidate.get('hourly_rate', 0),
                            'Job Success Score (JSS)': candidate.get('job_success_score', 0),
                            'Total Earned': candidate.get('total_earned', 0),
                            'Total Jobs': candidate.get('total_jobs', 0),
                            'Location': candidate.get('location', ''),
                            'Skills': candidate.get('skills', []),
                            'profile_description': candidate.get('description', '')
                        }
                        
                        # Calculer le score
                        job_requirements = {
                            'skills': job_data.get('Skills', []),
                            'max_rate': 999,  # À adapter
                            'keywords': job_data.get('Skills', [])
                        }
                        
                        score_result = scoring_engine.calculate_score(candidate_data, job_requirements)
                        candidate_data['Algorithm Score'] = score_result['total_score']
                        candidate_data['Qualification Status'] = score_result['qualification_status']
                        
                        # Créer le candidat dans Airtable
                        created_candidate = airtable.get_or_create_candidate(
                            profile_url, candidate_data, job_id
                        )
                        
                        if created_candidate:
                            processed_count += 1
                            logger.log_candidate_action("créé", created_candidate['id'], 
                                                       score=score_result['total_score'])
                    
                    except Exception as e:
                        logger.error(f"❌ Erreur traitement candidat: {e}")
                        continue
                
                # Logger les statistiques pour ce job
                airtable.log_system_event(
                    f"Recherche candidats terminée: {processed_count} nouveaux candidats",
                    job_id=job_id,
                    metadata={
                        'candidates_found': len(candidates),
                        'candidates_processed': processed_count
                    }
                )
                
                # Incrémenter les métriques
                airtable.increment_metric('Profiles Scraped', processed_count)
                total_candidates_found += processed_count
                
            except Exception as e:
                logger.error(f"❌ Erreur recherche candidats job {job_id}: {e}")
                airtable.log_error(
                    f"Erreur recherche candidats: {str(e)}",
                    job_id=job_id,
                    severity="Error"
                )
                continue
        
        logger.log_workflow_end("Candidate Search", True, 
                               total_candidates=total_candidates_found)
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur workflow Candidate Search: {e}")
        logger.log_workflow_end("Candidate Search", False, error=str(e))
        return False


def run_invitation_campaign():
    """Exécute le workflow d'invitation de candidats"""
    logger.log_workflow_start("Invitation Campaign")
    
    try:
        airtable = AirtableClient()
        skyvern = SkyvernClient()
        
        # Vérifier le quota quotidien
        today_invitations = airtable.count_invitations_today()
        remaining_quota = config.MAX_INVITATIONS_PER_DAY - today_invitations
        
        if remaining_quota <= 0:
            logger.warning("⚠️ Quota quotidien d'invitations atteint")
            return True
        
        logger.info(f"📧 Quota restant aujourd'hui: {remaining_quota}")
        
        # Récupérer les candidats qualifiés non invités
        qualified_candidates = airtable.get_qualified_candidates()
        
        if not qualified_candidates:
            logger.info("ℹ️ Aucun candidat qualifié à inviter")
            return True
        
        # Trier par score décroissant
        qualified_candidates.sort(
            key=lambda c: c['fields'].get('Algorithm Score', 0),
            reverse=True
        )
        
        # Limiter au quota disponible
        candidates_to_invite = qualified_candidates[:remaining_quota]
        
        logger.info(f"👤 {len(candidates_to_invite)} candidats à inviter")
        
        invited_count = 0
        for candidate in candidates_to_invite:
            candidate_data = candidate['fields']
            candidate_id = candidate['id']
            job_id = candidate_data.get('Job ID', [None])[0]  # Airtable links are arrays
            
            try:
                # Récupérer les détails du job
                job_record = airtable.jobs_table.get(job_id) if job_id else None
                if not job_record:
                    logger.warning(f"⚠️ Job non trouvé pour candidat {candidate_id}")
                    continue
                
                job_data = job_record['fields']
                
                # Préparer le message d'invitation
                message_template = (
                    "Hi {name},\n\n"
                    "I came across your profile and was impressed by your experience. "
                    "We're looking for a {job_title} for our project, and your skills in {skills} "
                    "seem like a great match.\n\n"
                    "Would you be interested in discussing this opportunity further?\n\n"
                    "Best regards"
                )
                
                # Envoyer l'invitation
                profile_url = candidate_data.get('Profile URL')
                success = skyvern.send_upwork_invitation(
                    profile_url,
                    job_data,
                    message_template
                )
                
                if success:
                    # Mettre à jour le statut dans Airtable
                    airtable.update_candidate(candidate_id, {
                        'Invitation Status': 'Sent',
                        'Invited Date': datetime.now().isoformat()
                    })
                    
                    # Logger l'événement
                    airtable.log_system_event(
                        f"Invitation envoyée: {profile_url}",
                        job_id=job_id,
                        candidate_id=candidate_id
                    )
                    
                    # Incrémenter les métriques
                    airtable.increment_metric('Invitations Sent')
                    
                    invited_count += 1
                    logger.log_invitation_sent(candidate_id, job_id, profile_url=profile_url)
                else:
                    logger.error(f"❌ Échec invitation candidat {candidate_id}")
                    airtable.log_error(
                        "Échec envoi invitation",
                        candidate_id=candidate_id,
                        job_id=job_id,
                        severity="Error"
                    )
                
            except Exception as e:
                logger.error(f"❌ Erreur invitation candidat {candidate_id}: {e}")
                airtable.log_error(
                    f"Erreur invitation: {str(e)}",
                    candidate_id=candidate_id,
                    job_id=job_id,
                    severity="Error"
                )
                continue
        
        logger.log_workflow_end("Invitation Campaign", True, invited_candidates=invited_count)
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur workflow Invitation Campaign: {e}")
        logger.log_workflow_end("Invitation Campaign", False, error=str(e))
        return False


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Upwork Recruitment Automation')
    parser.add_argument('command', choices=[
        'test', 'publish', 'search', 'invite', 'all'
    ], help='Commande à exécuter')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Mode verbeux')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.logger.setLevel('DEBUG')
    
    logger.info("🚀 Démarrage Upwork Recruitment Automation")
    
    if args.command == 'test':
        success = test_configuration()
        sys.exit(0 if success else 1)
    
    elif args.command == 'publish':
        success = run_job_publishing()
        sys.exit(0 if success else 1)
    
    elif args.command == 'search':
        success = run_candidate_search()
        sys.exit(0 if success else 1)
    
    elif args.command == 'invite':
        success = run_invitation_campaign()
        sys.exit(0 if success else 1)
    
    elif args.command == 'all':
        # Exécuter tous les workflows en séquence
        workflows = [
            ('Configuration', test_configuration),
            ('Job Publishing', run_job_publishing),
            ('Candidate Search', run_candidate_search),
            ('Invitation Campaign', run_invitation_campaign)
        ]
        
        all_success = True
        for name, func in workflows:
            logger.info(f"🔄 Exécution: {name}")
            try:
                success = func()
                if not success:
                    all_success = False
                    logger.error(f"❌ Échec du workflow: {name}")
                    break
            except Exception as e:
                logger.error(f"❌ Erreur inattendue dans {name}: {e}")
                all_success = False
                break
        
        if all_success:
            logger.info("✅ Tous les workflows exécutés avec succès")
        else:
            logger.error("❌ Échec d'un ou plusieurs workflows")
        
        sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
