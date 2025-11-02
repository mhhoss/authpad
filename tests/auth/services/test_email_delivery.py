import pytest
from unittest.mock import patch, AsyncMock
from app.auth.services.otp import EmailService

@pytest.mark.asyncio
async def test_send_verification_email_success():
    with patch('app.auth.services.otp.SMTP') as mock_smtp_class:
        
        # Setup mock
        mock_smtp_instance = AsyncMock()
        mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
        
        # Test
        email_service = EmailService()
        email = "user@example.com"
        otp = "123456"
        
        await email_service.send_verification_email(to=email, otp=otp)
        
        # verify mock calls
        mock_smtp_instance.connect.assert_called_once()
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()