import hashlib
import secrets
from aiosmtplib import SMTP

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.template_engine import env
from app.core.config import settings


class OTPService:

    @staticmethod
    def generate_otp(length: int = settings.OTP_LENGTH) -> str:
        '''Generate numeric OTP'''

        digits = "0123456789"
        return "".join(secrets.choice(digits) for _ in range(length))


    @staticmethod
    def hash_token(token : str) -> str:
        '''
        This function converts the input token into a hexadecimal hash string,
        allowing safe storage and later comparison without exposing the original token.

        Responses:
            str: A SHA-256 hexadecimal hash of the input token.
        '''

        hashed = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return hashed
    

    @staticmethod
    def verify_input_token(
            input_token: str,
            stored_hash: str,
            expected_length: int = settings.OTP_LENGTH
    ) -> bool:
        '''Validates the format of the input token and compares its hash with the stored hash'''
        
        if not input_token.isdigit():
            raise ValueError("Token must contain only digits")
            
        if len(input_token) != expected_length:
            raise ValueError(f"Token must be exactly {expected_length} digits long")
            
        hashed_input = OTPService.hash_token(input_token)
        return stored_hash == hashed_input 



class EmailService:
    '''
    Service class for sending verification emails using SMTP and Jinja2 templates.

    This class handles rendering email templates and sending them to users and verification input token.
    '''

    async def send_verification_email(
            self,
            to: str,
            otp: str
        ) -> None:
        
        # Render templates (HTML & text)
        html_template = env.get_template("email/verify_email.html")
        text_template = env.get_template("email/verify_email.txt")
        
        html_body = html_template.render(
            user_name=to.split("@")[0],
            otp=otp,
            expire_minutes=settings.OTP_EXPIRE_MINUTES
        )

        text_body = text_template.render(
            user_name=to.split("@")[0],
            otp=otp,
            expire_minutes=settings.OTP_EXPIRE_MINUTES
        )

        '''Create the email message'''
        subject = "Verify Your Email Address"
        message = MIMEMultipart("alternative")  # Use plain text if HTML not supported
        message["Subject"] = subject
        message["From"] = settings.FROM_EMAIL
        message["To"] = to

        message.attach(MIMEText(html_body, "html"))
        message.attach(MIMEText(text_body, "plain"))

        async with SMTP(
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            start_tls=True
            ) as smtp:

            await smtp.connect()  # Connect to server
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            await smtp.send_message(message)