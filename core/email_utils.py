import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_detection_report_email(user, crop, disease_name, health_status, message, image_url):
    """
    Send a plant disease detection report to the user's email using Brevo.
    """
    context = {
        'user': user,
        'datetime': now(),
        'crop': crop,
        'disease': disease_name if disease_name else "Not Identified",
        'health_status': health_status,
        'message': message,
        'image_url': image_url,
    }

    subject = "Plant Disease Detection Report"
    html_content = render_to_string("email/Analysis_Report.html", context)
    plain_text_content = strip_tags(html_content)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    sender = {
        "name": settings.EMAIL_OTP_SENDER_NAME,
        "email": settings.EMAIL_OTP_SENDER_EMAIL
    }

    to = [{"email": user.email, "name": user.first_name}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        subject=subject,
        sender=sender,
        text_content=plain_text_content
    )

    try:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Disease report email sent to {user.email}")
    except ApiException as e:
        logger.error(f"Error sending detection report via Brevo to {user.email}: {e}")
