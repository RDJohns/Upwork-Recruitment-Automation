from typing import Dict, Any, List, Tuple
from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import parse_skills, format_percentage


class CandidateScoringEngine:
    """Algorithme de scoring multi-critères pour les candidats"""
    
    # Poids par défaut (configurable via variables d'environnement si besoin)
    WEIGHTS = {
        'skills_match': 0.35,      # 35% - Correspondance des compétences
        'jss': 0.20,               # 20% - Job Success Score
        'experience': 0.20,        # 20% - Expérience (revenus + projets)
        'portfolio': 0.15,         # 15% - Qualité du portfolio/description
        'rate_compatibility': 0.10 # 10% - Compatibilité tarifaire
    }
    
    def __init__(self):
        logger.info("Moteur de scoring initialisé", weights=self.WEIGHTS)
    
    def calculate_score(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score total pondéré (0-100) pour un candidat
        
        Args:
            candidate_data: Données du candidat (skills, JSS, rate, etc.)
            job_requirements: Exigences du job (skills requises, budget, etc.)
            
        Returns:
            Dict avec score total et décomposition par critère
        """
        try:
            scores = {}
            
            # 1. Skills Match Score
            scores['skills_match'] = self._calculate_skills_match(
                candidate_data.get('skills', []),
                job_requirements.get('skills', [])
            )
            
            # 2. Job Success Score (JSS)
            scores['jss'] = self._calculate_jss_score(
                candidate_data.get('job_success_score', 0)
            )
            
            # 3. Experience Score
            scores['experience'] = self._calculate_experience_score(
                candidate_data.get('total_earned', 0),
                candidate_data.get('total_jobs', 0)
            )
            
            # 4. Portfolio Score
            scores['portfolio'] = self._calculate_portfolio_score(
                candidate_data.get('profile_description', ''),
                candidate_data.get('portfolio_text', ''),
                job_requirements.get('keywords', [])
            )
            
            # 5. Rate Compatibility
            scores['rate_compatibility'] = self._calculate_rate_compatibility(
                candidate_data.get('hourly_rate', 0),
                job_requirements.get('max_rate', 999),
                job_requirements.get('min_rate', 0)
            )
            
            # Calcul final pondéré
            final_score = sum(scores[key] * self.WEIGHTS[key] for key in scores)
            
            result = {
                'total_score': round(final_score, 2),
                'breakdown': scores,
                'qualification_status': self.get_qualification_status(final_score)
            }
            
            logger.debug(f"Score calculé: {final_score:.2f}", breakdown=scores)
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul score: {e}")
            return {
                'total_score': 0,
                'breakdown': {},
                'qualification_status': 'Unqualified'
            }
    
    def _calculate_skills_match(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Calcule le score de correspondance des compétences (0-100)"""
        if not required_skills:
            return 50  # Score neutre si pas de compétences requises
        
        if not candidate_skills:
            return 0  # Pas de correspondance si pas de compétences
        
        # Normaliser les compétences (lowercase, strip)
        candidate_skills_norm = {skill.lower().strip() for skill in candidate_skills if skill}
        required_skills_norm = {skill.lower().strip() for skill in required_skills if skill}
        
        # Calculer le ratio de correspondance
        matches = len(candidate_skills_norm & required_skills_norm)
        total_required = len(required_skills_norm)
        
        if total_required == 0:
            return 50
        
        match_ratio = matches / total_required
        
        # Bonus si toutes les compétences requises sont présentes
        if match_ratio == 1.0:
            return 100
        elif match_ratio >= 0.8:
            return 90
        elif match_ratio >= 0.6:
            return 75
        elif match_ratio >= 0.4:
            return 50
        elif match_ratio >= 0.2:
            return 25
        else:
            return 10
    
    def _calculate_jss_score(self, jss: float) -> float:
        """Calcule le score basé sur le Job Success Score (0-100)"""
        if jss >= 95:
            return 100
        elif jss >= 90:
            return 85
        elif jss >= 85:
            return 70
        elif jss >= 80:
            return 55
        elif jss >= 75:
            return 40
        elif jss >= 70:
            return 25
        else:
            return 10
    
    def _calculate_experience_score(self, total_earned: float, total_jobs: int) -> float:
        """Calcule le score d'expérience basé sur les revenus et nombre de projets"""
        # Score basé sur les revenus
        if total_earned > 100000:
            earned_score = 100
        elif total_earned > 50000:
            earned_score = 85
        elif total_earned > 20000:
            earned_score = 70
        elif total_earned > 10000:
            earned_score = 55
        elif total_earned > 5000:
            earned_score = 40
        elif total_earned > 1000:
            earned_score = 25
        else:
            earned_score = 10
        
        # Score basé sur le nombre de projets
        if total_jobs > 100:
            jobs_score = 100
        elif total_jobs > 50:
            jobs_score = 85
        elif total_jobs > 25:
            jobs_score = 70
        elif total_jobs > 15:
            jobs_score = 55
        elif total_jobs > 10:
            jobs_score = 40
        elif total_jobs > 5:
            jobs_score = 25
        else:
            jobs_score = 10
        
        # Moyenne pondérée (70% revenus, 30% projets)
        return (earned_score * 0.7) + (jobs_score * 0.3)
    
    def _calculate_portfolio_score(self, profile_description: str, portfolio_text: str, 
                                 job_keywords: List[str]) -> float:
        """Calcule le score basé sur la qualité du portfolio et description"""
        if not profile_description and not portfolio_text:
            return 30  # Pénalité si pas de description
        
        # Combiner tout le texte
        combined_text = f"{profile_description} {portfolio_text}".lower()
        
        # Score de base basé sur la longueur (indique le niveau de détail)
        text_length = len(combined_text)
        if text_length > 2000:
            length_score = 90
        elif text_length > 1000:
            length_score = 75
        elif text_length > 500:
            length_score = 60
        elif text_length > 200:
            length_score = 45
        else:
            length_score = 30
        
        # Score basé sur les mots-clés du job
        if job_keywords:
            keyword_matches = sum(1 for kw in job_keywords if kw.lower() in combined_text)
            keyword_ratio = keyword_matches / len(job_keywords)
            keyword_score = keyword_ratio * 100
        else:
            keyword_score = 50  # Neutre si pas de mots-clés
        
        # Indicateurs de qualité (mots positifs, etc.)
        quality_indicators = [
            'experience', 'expert', 'specialist', 'professional', 'skilled',
            'certified', 'senior', 'lead', 'managed', 'developed', 'created'
        ]
        quality_matches = sum(1 for indicator in quality_indicators if indicator in combined_text)
        quality_score = min(quality_matches * 10, 50)  # Max 50 points
        
        # Moyenne pondérée
        return (length_score * 0.4) + (keyword_score * 0.4) + (quality_score * 0.2)
    
    def _calculate_rate_compatibility(self, candidate_rate: float, max_rate: float, 
                                     min_rate: float = 0) -> float:
        """Calcule le score de compatibilité tarifaire (0-100)"""
        if candidate_rate == 0:
            return 50  # Neutre si pas de tarif spécifié
        
        if candidate_rate <= max_rate and candidate_rate >= min_rate:
            # Parfaitement dans la fourchette
            return 100
        elif candidate_rate <= max_rate * 1.1:
            # Légèrement au-dessus mais acceptable
            return 85
        elif candidate_rate <= max_rate * 1.2:
            # Un peu au-dessus
            return 70
        elif candidate_rate <= max_rate * 1.5:
            # Significativement au-dessus
            return 40
        else:
            # Trop cher
            return 10
    
    def get_qualification_status(self, score: float) -> str:
        """Détermine le statut de qualification basé sur le score"""
        if score >= config.MIN_QUALIFICATION_SCORE:
            return 'Qualified'
        elif score >= config.REVIEW_SCORE_THRESHOLD:
            return 'To Review'
        else:
            return 'Unqualified'
    
    def rank_candidates(self, candidates: List[Dict[str, Any]], 
                        job_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Classe une liste de candidats par score décroissant
        
        Args:
            candidates: Liste des candidats avec leurs données
            job_requirements: Exigences du job
            
        Returns:
            Liste des candidats avec scores ajoutés, classée par score décroissant
        """
        scored_candidates = []
        
        for candidate in candidates:
            candidate_data = candidate.get('fields', {})
            
            # Calculer le score
            score_result = self.calculate_score(candidate_data, job_requirements)
            
            # Ajouter les informations de scoring
            candidate_with_score = candidate.copy()
            candidate_with_score['scoring'] = score_result
            
            scored_candidates.append(candidate_with_score)
        
        # Trier par score décroissant
        scored_candidates.sort(
            key=lambda c: c['scoring']['total_score'], 
            reverse=True
        )
        
        logger.info(f"Candidats classés: {len(scored_candidates)} évalués")
        
        return scored_candidates
    
    def get_score_distribution(self, scored_candidates: List[Dict[str, Any]]) -> Dict[str, int]:
        """Retourne la distribution des scores par catégorie"""
        distribution = {
            'Qualified': 0,
            'To Review': 0,
            'Unqualified': 0
        }
        
        for candidate in scored_candidates:
            status = candidate['scoring']['qualification_status']
            distribution[status] += 1
        
        return distribution
    
    def explain_score(self, candidate_data: Dict[str, Any], 
                     job_requirements: Dict[str, Any]) -> str:
        """Génère une explication textuelle du score"""
        score_result = self.calculate_score(candidate_data, job_requirements)
        breakdown = score_result['breakdown']
        
        explanation = f"Score total: {score_result['total_score']:.1f}/100\n"
        explanation += f"Statut: {score_result['qualification_status']}\n\n"
        explanation += "Détail par critère:\n"
        
        criterion_names = {
            'skills_match': 'Correspondance compétences',
            'jss': 'Job Success Score',
            'experience': 'Expérience',
            'portfolio': 'Portfolio/Description',
            'rate_compatibility': 'Compatibilité tarifaire'
        }
        
        for criterion, score in breakdown.items():
            weight = self.WEIGHTS[criterion]
            weighted_score = score * weight
            name = criterion_names.get(criterion, criterion)
            explanation += f"- {name}: {score:.1f}/100 (poids {weight*100:.0f}%) → {weighted_score:.1f} points\n"
        
        return explanation
