import random
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.hashers import make_password

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from .models import OTP, TemporaryUserData

logger = logging.getLogger('core')  # Use the custom 'core' logger

def generate_otp():
    """Generate a 6-digit numeric OTP."""
    return str(random.randint(100000, 999999))


def cleanup_temp_user(email, phone_no):
    """
    Remove expired or conflicting temporary user entries.
    This prevents issues with duplicate email or phone registration.
    """
    expiry_time = timezone.now() - timedelta(minutes=10)

    expired_count = TemporaryUserData.objects.filter(
        Q(email=email) | Q(phone_no=phone_no),
        created_at__lt=expiry_time
    ).delete()

    conflict_count = TemporaryUserData.objects.filter(
        Q(email=email) | Q(phone_no=phone_no)
    ).delete()

    logger.info(f"Cleaned up temp users: expired={expired_count}, conflicts={conflict_count}")


def create_temp_user(validated_data):
    """
    Save user data temporarily before full registration (until OTPs are verified).
    """
    temp_user = TemporaryUserData.objects.create(
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        email=validated_data['email'],
        phone_no=validated_data['phone_no'],
        password=make_password(validated_data['password']),
        region=validated_data['region']
    )
    logger.debug(f"Temporary user created for email: {temp_user.email}")
    return temp_user


def send_email_otp(email, purpose='register'):
    """
    Send an OTP to the user's email using Brevo (Sendinblue).
    """
    otp_code = generate_otp()

    OTP.objects.filter(email=email, purpose=purpose).delete()
    OTP.objects.create(email=email, otp_code=otp_code, purpose=purpose)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    sender = {
        "name": settings.EMAIL_OTP_SENDER_NAME,
        "email": settings.EMAIL_OTP_SENDER_EMAIL
    }

    subject = "Your OTP Code"
    html_content = f"<html><body><h3>Your OTP is: <strong>{otp_code}</strong></h3></body></html>"

    to = [{"email": email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        subject=subject,
        sender=sender
    )

    try:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email OTP sent to {email}")
        return otp_code

    except ApiException as e:
        logger.error(f"Error sending email OTP via Brevo for {email}: {e}")
        return False


# def send_mobile_otp(phone_no, purpose='register'):
#     """
#     Send an OTP to the user's mobile number using Fast2SMS.
#     """
#     otp_code = generate_otp()

#     OTP.objects.filter(phone_no=phone_no, purpose=purpose).delete()
#     OTP.objects.create(phone_no=phone_no, otp_code=otp_code, purpose=purpose)

#     print(f"[DEBUG] Sending OTP to {phone_no}: {otp_code}")
#     logger.info(f"Sending otp to {phone_no}: {otp_code}")
#     url = "https://www.fast2sms.com/dev/bulkV2"

#     payload = {
#         # 'sender_id': 'FSTSMS',
#         # 'message': f'Your OTP is {otp_code}. Do not share it with anyone.',
#         # 'language': 'english',
#         # 'route': 'p',
#         # 'numbers': phone_no
#         "variables_values": otp_code,
#         "route": "otp",
#         "numbers": phone_no
#     }

#     headers = {
#         'authorization': settings.FAST2SMS_API_KEY,
#         'Content-Type': "application/x-www-form-urlencoded",
#         'Cache-Control': "no-cache",
#     }

#     try:
#         # response = requests.post(url, data=payload, headers=headers)
#         response = requests.request("POST", url, data=payload, headers=headers)
#         if response.status_code == 200:
#             logger.info(f"Mobile OTP sent successfully to {phone_no}")
#             return otp_code
#         else:
#             logger.warning(f"Failed to send mobile OTP to {phone_no}. Response: {response.text}")
#             return False
#     except Exception as e:
#         logger.exception(f"Exception while sending mobile OTP to {phone_no}: {e}")
#         return False


# payload = "sender_id=DLT_SENDER_ID&message=YOUR_MESSAGE_ID&variables_values=12345|asdaswdx&route=dlt&numbers=9999999999,8888888888,7777777777"


def verify_otp(identifier, otp_code, is_email=True):
    """
    Verify an OTP against email or phone, checking for expiry and duplication.
    Returns:
        - otp instance if valid
        - error message string if invalid
    """
    try:
        lookup_field = {'email': identifier} if is_email else {'phone_no': identifier}
        otp = OTP.objects.filter(**lookup_field, otp_code=otp_code).latest('created_at')
    except OTP.DoesNotExist:
        logger.warning(f"OTP verification failed for {identifier} - OTP not found")
        return None, "Invalid or expired OTP"

    if otp.is_verified:
        logger.info(f"OTP for {identifier} already verified")
        return None, "OTP already verified"

    if otp.is_expired():
        logger.info(f"OTP for {identifier} has expired")
        return None, "OTP has expired"

    otp.is_verified = True
    otp.save()
    logger.info(f"OTP successfully verified for {identifier}")
    return otp, None
