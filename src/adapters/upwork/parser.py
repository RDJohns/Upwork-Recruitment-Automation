"""
Parser pour les données extraites de Upwork par Skyvern
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import re
from ...utils.logger import logger
from ...utils.helpers import parse_skills, safe_json_loads, format_currency


class UpworkDataParser:
    """Parser pour structurer les données brutes de Skyvern"""
    
    @staticmethod
    def parse_candidate_profile(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse les données brutes d'un profil candidat"""
        try:
            # Extraction basique avec fallbacks
            parsed = {
                'name': UpworkDataParser._extract_name(raw_data),
                'profile_url': UpworkDataParser._extract_profile_url(raw_data),
                'skills': UpworkDataParser._extract_skills(raw_data),
                'job_success_score': UpworkDataParser._extract_jss(raw_data),
                'hourly_rate': UpworkDataParser._extract_hourly_rate(raw_data),
                'total_earned': UpworkDataParser._extract_total_earned(raw_data),
                'total_jobs': UpworkDataParser._extract_total_jobs(raw_data),
                'location': UpworkDataParser._extract_location(raw_data),
                'profile_description': UpworkDataParser._extract_description(raw_data),
                'portfolio_text': UpworkDataParser._extract_portfolio(raw_data),
                'title': UpworkDataParser._extract_title(raw_data)
            }
            
            logger.debug(f"Profil parsé: {parsed['name']}", skills_count=len(parsed['skills']))
            return parsed
            
        except Exception as e:
            logger.error(f"Erreur parsing profil candidat: {e}")
            return UpworkDataParser._get_empty_profile()
    
    @staticmethod
    def parse_job_publication_result(raw_data: Dict[str, Any]) -> Optional[str]:
        """Extrait l'URL du job publié"""
        try:
            # Chercher l'URL dans différentes structures possibles
            url = None
            
            # Structure directe
            if 'job_url' in raw_data:
                url = raw_data['job_url']
            # Structure imbriquée
            elif 'extracted_data' in raw_data and 'job_url' in raw_data['extracted_data']:
                url = raw_data['extracted_data']['job_url']
            # Chercher dans les URLs trouvées
            elif 'urls' in raw_data:
                for found_url in raw_data['urls']:
                    if 'upwork.com' in found_url and '/jobs/' in found_url:
                        url = found_url
                        break
            
            if url and UpworkDataParser._is_valid_upwork_job_url(url):
                return url
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur parsing URL job: {e}")
            return None
    
    @staticmethod
    def parse_search_results(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse les résultats de recherche de candidats"""
        try:
            candidates = []
            
            # Différentes structures possibles
            if 'candidates' in raw_data:
                candidates_data = raw_data['candidates']
            elif 'extracted_data' in raw_data and 'candidates' in raw_data['extracted_data']:
                candidates_data = raw_data['extracted_data']['candidates']
            elif 'profiles' in raw_data:
                candidates_data = raw_data['profiles']
            else:
                candidates_data = []
            
            for candidate_raw in candidates_data:
                parsed_candidate = UpworkDataParser.parse_candidate_profile(candidate_raw)
                if parsed_candidate['name']:  # Ignorer les profils vides
                    candidates.append(parsed_candidate)
            
            logger.info(f"{len(candidates)} candidats parsés depuis {len(candidates_data)} résultats bruts")
            return candidates
            
        except Exception as e:
            logger.error(f"Erreur parsing résultats recherche: {e}")
            return []
    
    @staticmethod
    def parse_invitation_result(raw_data: Dict[str, Any]) -> bool:
        """Vérifie si une invitation a été envoyée avec succès"""
        try:
            # Indicateurs de succès
            success_indicators = [
                raw_data.get('invitation_sent', False),
                raw_data.get('success', False),
                raw_data.get('status') == 'completed'
            ]
            
            # Vérifier dans extracted_data
            extracted = raw_data.get('extracted_data', {})
            success_indicators.extend([
                extracted.get('invitation_sent', False),
                extracted.get('success', False)
            ])
            
            return any(success_indicators)
            
        except Exception as e:
            logger.error(f"Erreur parsing résultat invitation: {e}")
            return False
    
    @staticmethod
    def parse_responses(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse les réponses des candidats"""
        try:
            responses = []
            
            if 'responses' in raw_data:
                responses_data = raw_data['responses']
            elif 'extracted_data' in raw_data and 'responses' in raw_data['extracted_data']:
                responses_data = raw_data['extracted_data']['responses']
            elif 'messages' in raw_data:
                responses_data = raw_data['messages']
            else:
                responses_data = []
            
            for response_raw in responses_data:
                parsed_response = {
                    'candidate_name': response_raw.get('name', ''),
                    'candidate_url': response_raw.get('profile_url', ''),
                    'message': response_raw.get('message', ''),
                    'timestamp': response_raw.get('timestamp', ''),
                    'response_type': UpworkDataParser._classify_response(response_raw.get('message', '')),
                    'raw_data': response_raw
                }
                responses.append(parsed_response)
            
            logger.info(f"{len(responses)} réponses parsées")
            return responses
            
        except Exception as e:
            logger.error(f"Erreur parsing réponses: {e}")
            return []
    
    # Méthodes privées d'extraction
    
    @staticmethod
    def _extract_name(raw_data: Dict[str, Any]) -> str:
        """Extrait le nom du candidat"""
        possible_fields = ['name', 'full_name', 'candidate_name', 'profile_name']
        for field in possible_fields:
            if field in raw_data and raw_data[field]:
                return str(raw_data[field]).strip()
        return ""
    
    @staticmethod
    def _extract_profile_url(raw_data: Dict[str, Any]) -> str:
        """Extrait l'URL du profil"""
        possible_fields = ['profile_url', 'url', 'profile_link', 'candidate_url']
        for field in possible_fields:
            if field in raw_data and raw_data[field]:
                url = str(raw_data[field])
                if 'upwork.com' in url:
                    return url
        return ""
    
    @staticmethod
    def _extract_skills(raw_data: Dict[str, Any]) -> List[str]:
        """Extrait et nettoie les compétences"""
        skills = []
        
        # Différents formats possibles
        if 'skills' in raw_data:
            skills_raw = raw_data['skills']
            if isinstance(skills_raw, list):
                skills = skills_raw
            elif isinstance(skills_raw, str):
                skills = parse_skills(skills_raw)
        
        # Chercher dans d'autres champs
        for field in ['technologies', 'expertise', 'tools']:
            if field in raw_data and raw_data[field]:
                field_skills = raw_data[field]
                if isinstance(field_skills, list):
                    skills.extend(field_skills)
                elif isinstance(field_skills, str):
                    skills.extend(parse_skills(field_skills))
        
        # Nettoyer et dédupliquer
        cleaned_skills = []
        for skill in skills:
            if isinstance(skill, str) and skill.strip():
                cleaned_skills.append(skill.strip())
        
        return list(set(cleaned_skills))
    
    @staticmethod
    def _extract_jss(raw_data: Dict[str, Any]) -> float:
        """Extrait le Job Success Score"""
        possible_fields = ['job_success_score', 'jss', 'success_rate', 'success_score']
        for field in possible_fields:
            if field in raw_data and raw_data[field] is not None:
                try:
                    # Nettoyer et convertir
                    value = str(raw_data[field]).replace('%', '').strip()
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return 0.0
    
    @staticmethod
    def _extract_hourly_rate(raw_data: Dict[str, Any]) -> float:
        """Extrait le taux horaire"""
        possible_fields = ['hourly_rate', 'rate', 'price', 'hourly_price']
        for field in possible_fields:
            if field in raw_data and raw_data[field] is not None:
                try:
                    # Nettoyer et convertir
                    value = str(raw_data[field]).replace('$', '').replace('/hr', '').strip()
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return 0.0
    
    @staticmethod
    def _extract_total_earned(raw_data: Dict[str, Any]) -> float:
        """Extrait le total des revenus"""
        possible_fields = ['total_earned', 'earnings', 'total_revenue', 'lifetime_earnings']
        for field in possible_fields:
            if field in raw_data and raw_data[field] is not None:
                try:
                    # Nettoyer et convertir
                    value = str(raw_data[field]).replace('$', '').replace(',', '').strip()
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return 0.0
    
    @staticmethod
    def _extract_total_jobs(raw_data: Dict[str, Any]) -> int:
        """Extrait le nombre total de jobs"""
        possible_fields = ['total_jobs', 'jobs_count', 'completed_jobs', 'project_count']
        for field in possible_fields:
            if field in raw_data and raw_data[field] is not None:
                try:
                    return int(raw_data[field])
                except (ValueError, TypeError):
                    continue
        return 0
    
    @staticmethod
    def _extract_location(raw_data: Dict[str, Any]) -> str:
        """Extrait la localisation"""
        possible_fields = ['location', 'country', 'city', 'address']
        for field in possible_fields:
            if field in raw_data and raw_data[field]:
                return str(raw_data[field]).strip()
        return ""
    
    @staticmethod
    def _extract_description(raw_data: Dict[str, Any]) -> str:
        """Extrait la description du profil"""
        possible_fields = ['description', 'profile_description', 'bio', 'about', 'summary']
        for field in possible_fields:
            if field in raw_data and raw_data[field]:
                return str(raw_data[field]).strip()
        return ""
    
    @staticmethod
    def _extract_portfolio(raw_data: Dict[str, Any]) -> str:
        """Extrait le texte du portfolio"""
        possible_fields = ['portfolio', 'portfolio_text', 'work_history', 'projects']
        for field in possible_fields:
            if field in raw_data:
                if isinstance(raw_data[field], str):
                    return raw_data[field].strip()
                elif isinstance(raw_data[field], list):
                    return " ".join(str(item) for item in raw_data[field])
        return ""
    
    @staticmethod
    def _extract_title(raw_data: Dict[str, Any]) -> str:
        """Extrait le titre/profession"""
        possible_fields = ['title', 'profession', 'role', 'job_title']
        for field in possible_fields:
            if field in raw_data and raw_data[field]:
                return str(raw_data[field]).strip()
        return ""
    
    @staticmethod
    def _classify_response(message: str) -> str:
        """Classifie une réponse de candidat"""
        if not message:
            return "Unknown"
        
        message_lower = message.lower()
        
        # Mots-clés positifs
        positive_keywords = ['interested', 'available', 'yes', 'sure', 'glad', 'excited', 'ready']
        # Mots-clés négatifs
        negative_keywords = ['not interested', 'busy', 'no thanks', 'decline', 'pass', 'unavailable']
        # Mots-clés de questions
        question_keywords = ['when', 'what', 'how much', 'budget', 'details', '?']
        
        if any(kw in message_lower for kw in negative_keywords):
            return "Declined"
        elif any(kw in message_lower for kw in positive_keywords):
            return "Accepted"
        elif any(kw in message_lower for kw in question_keywords):
            return "Question"
        else:
            return "Neutral"
    
    @staticmethod
    def _is_valid_upwork_job_url(url: str) -> bool:
        """Valide une URL de job Upwork"""
        return url and ("upwork.com" in url and ("/jobs/" in url or "/proposals/" in url))
    
    @staticmethod
    def _get_empty_profile() -> Dict[str, Any]:
        """Retourne un profil vide avec les bonnes clés"""
        return {
            'name': '',
            'profile_url': '',
            'skills': [],
            'job_success_score': 0.0,
            'hourly_rate': 0.0,
            'total_earned': 0.0,
            'total_jobs': 0,
            'location': '',
            'profile_description': '',
            'portfolio_text': '',
            'title': ''
        }
