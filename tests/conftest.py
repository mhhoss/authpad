import sys
from pathlib import Path
from httpx import patch
import pytest
from jinja2 import Environment, FileSystemLoader
from unittest.mock import AsyncMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Load templates for tests
@pytest.fixture(scope="module")
def jinja_env():
    BASE_DIR = Path(__file__).resolve().parent.parent
    template_path = BASE_DIR / "app" / "templates"
    env = Environment(loader=FileSystemLoader(template_path))
    return env


@pytest.fixture
def mock_smtp():
    '''Mock for SMTP async'''

    with patch('app.auth.services.otp') as mock_smtp_class:
        mock_smtp_instance = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
        yield mock_smtp_instance