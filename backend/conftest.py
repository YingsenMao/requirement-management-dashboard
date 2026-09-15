import pytest
from django.conf import settings


@pytest.fixture(autouse=True)
def use_simple_staticfiles():
    """Override staticfiles storage for tests to avoid manifest issues."""
    original_storage = settings.STATICFILES_STORAGE
    settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    yield
    settings.STATICFILES_STORAGE = original_storage
