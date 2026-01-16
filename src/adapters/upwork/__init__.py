"""
Adapter Upwork pour l'automation de recrutement
"""

from .tasks import UpworkTasks
from .parser import UpworkDataParser
from .auth import UpworkAuthHandler

__all__ = [
    'UpworkTasks',
    'UpworkDataParser', 
    'UpworkAuthHandler'
]