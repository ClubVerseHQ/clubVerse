# App Imports
from apps.users.models import OTP
from core.services.mail_service import EmailService
# Django Imports
import pyotp
from django.utils.timezone import now, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

User = get_user_model()

class OTPService:
    def __init__(self, user, purpose):
        if not isinstance(user, User):
            raise ValueError("The 'user' parameter must be an instance of the User model.")
        self.user = user
        self.purpose = purpose
        self.email = user.email
        self.email_service = EmailService()
        self.otp_obj = None

    def generate_otp(self):
        """
        Generate a new OTP or update the existing one for the user and purpose.
        """
        try:
            otp_record, created = OTP.objects.update_or_create(
                purpose=self.purpose,
                user=self.user,
                email=self.email,
                defaults={
                    "otp_secret": pyotp.random_base32(),
                    "created_at": now(),
                    "attempt_count": 0
                }
            )
            self.otp_obj = otp_record

            # Generate OTP using pyotp
            totp = pyotp.TOTP(otp_record.otp_secret, interval=300)
            return totp.now()
        except Exception as e:
            raise Exception(f"Error while generating OTP: {str(e)}")

    def send_otp(self):
        """
        Generate the OTP and send it via email using Celery.
        """
        try:
            otp = self.generate_otp()
            # Send email asynchronously using Celery
            self.email_service.send_otp_email(otp, self.email)
        except Exception as e:
            raise Exception(f"Error while sending OTP: {str(e)}")
        
    def verify(self, otp):
        """
        Verify the provided OTP.
        Args:
            otp (str): The OTP code to verify.
        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        try:
            # Fetch OTP record based on email and purpose
            otp_record = OTP.objects.get(email=self.email, purpose=self.purpose)
            self.otp_obj = otp_record
        except ObjectDoesNotExist:
            return False, "No pending verification found."

        # Check if the OTP has expired (older than 5 minutes)
        if otp_record.created_at < now() - timedelta(minutes=5):
            return False, "OTP has expired."

        # Check if maximum attempts have been reached
        if otp_record.attempt_count >= 5:
            return False, "Maximum OTP attempts reached. Please request a new OTP."

        # Verify the OTP code using TOTP
        totp = pyotp.TOTP(otp_record.otp_secret, interval=300)
        if not totp.verify(otp):
            otp_record.attempt_count += 1  # Increment attempt count
            otp_record.save()
            return False, "Invalid OTP."
        return True, "OTP is valid."