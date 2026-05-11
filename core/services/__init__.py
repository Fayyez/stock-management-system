from .dashboard import build_dashboard_context
from .person import PersonService

person_service = PersonService()

__all__ = ['build_dashboard_context', 'PersonService', 'person_service']
