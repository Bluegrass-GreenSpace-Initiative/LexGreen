# services/__init__.py
from .database import Database
from .uk_tree_service import UKTreeService
from .custom_tree_service import CustomTreeService
from .adoption_service import AdoptionService
from .damage_report_service import DamageReportService

# Make classes available for import directly from services package
__all__ = [
    'Database',
    'UKTreeService',
    'CustomTreeService',
    'AdoptionService',
    'DamageReportService'
]
