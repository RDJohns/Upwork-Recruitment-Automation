import time
import random
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import re


def generate_unique_id(prefix: str = "ID") -> str:
    """Génère un ID unique avec préfixe"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = random.randint(1000, 9999)
    return f"{prefix}_{timestamp}_{random_suffix}"


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour le rendre safe"""
    # Remplacer les caractères invalides
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Limiter la longueur
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 255 - len(ext) - 1
        filename = name[:max_name_len] + ('.' + ext if ext else '')
    
    return filename


def extract_domain(url: str) -> Optional[str]:
    """Extrait le domaine d'une URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def calculate_hash(text: str) -> str:
    """Calcule le hash SHA256 d'un texte"""
    return hashlib.sha256(text.encode()).hexdigest()


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Charge du JSON en toute sécurité avec fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, indent: Optional[int] = None) -> str:
    """Sérialise en JSON en toute sécurité"""
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return "{}"


def format_currency(amount: float, currency: str = "USD") -> str:
    """Formate un montant en devise"""
    return f"{amount:.2f} {currency}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formate un pourcentage"""
    return f"{value:.{decimals}f}%"


def delay_with_jitter(base_delay: float, jitter_factor: float = 0.3) -> float:
    """Ajoute un délai avec jitter pour éviter la détection"""
    jitter = base_delay * jitter_factor * random.uniform(-1, 1)
    actual_delay = max(0, base_delay + jitter)
    time.sleep(actual_delay)
    return actual_delay


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calcule un délai exponentiel avec maximum"""
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay_with_jitter(delay)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Divise une liste en chunks de taille fixe"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Aplatit un dictionnaire imbriqué"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def is_valid_email(email: str) -> bool:
    """Valide un format d'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_url(url: str) -> bool:
    """Valide un format d'URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def parse_skills(skills_input: str) -> List[str]:
    """Parse une chaîne de compétences en liste nettoyée"""
    if not skills_input:
        return []
    
    # Split par virgules, points-virgules, ou pipes
    skills = re.split(r'[,;|]', skills_input)
    
    # Nettoyer chaque skill
    cleaned_skills = []
    for skill in skills:
        skill = skill.strip()
        if skill and len(skill) > 1:  # Ignorer les single chars
            cleaned_skills.append(skill)
    
    # Retourner unique et trié
    return sorted(list(set(cleaned_skills)))


def calculate_date_range(start_date: datetime, end_date: datetime) -> Dict[str, int]:
    """Calcule la différence entre deux dates"""
    delta = end_date - start_date
    return {
        'days': delta.days,
        'hours': delta.seconds // 3600,
        'minutes': (delta.seconds % 3600) // 60,
        'total_hours': delta.total_seconds() / 3600,
        'total_days': delta.total_seconds() / 86400
    }


def format_duration(seconds: float) -> str:
    """Formate une durée en secondes en format lisible"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """Décorateur pour réessayer une fonction en cas d'exception"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = exponential_backoff(attempt, delay)
                        print(f"⚠️ Erreur (tentative {attempt + 1}/{max_retries + 1}): {e}")
                        print(f"🔄 Nouvelle tentative dans {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Échec après {max_retries + 1} tentatives")
            
            raise last_exception
        return wrapper
    return decorator


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Valide la présence de champs requis"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    return missing_fields


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Fusionne plusieurs dictionnaires (deep merge)"""
    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result
