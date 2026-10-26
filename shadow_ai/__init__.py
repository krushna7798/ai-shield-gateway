"""
shadow_ai Django project package.
"""

# Monkeypatch to permit MySQL 8.0.x versions on Django
from django.db.backends.base.base import BaseDatabaseWrapper
BaseDatabaseWrapper.check_database_version_supported = lambda self: None
