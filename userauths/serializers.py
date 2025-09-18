import re
import logging

from rest_framework import serializers
from .models import CustomUser

logger = logging.getLogger(__name__)

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    Validates password strength and matching confirmation.
    """
    password = serializers.CharField(write_only=True) 
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'password', 
            'confirm_password', 
            'phone_no', 
            'region'
        ]

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            logger.warning(f"Password mismatch for email: {data.get('email')}")
            raise serializers.ValidationError("Passwords do not match.")
        
        # Password policy enforcement
        if len(password) < 8:
            logger.warning(f"Weak password (too short) for email: {data.get('email')}")
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            logger.warning(f"Weak password (missing uppercase) for email: {data.get('email')}")
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            logger.warning(f"Weak password (missing lowercase) for email: {data.get('email')}")
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            logger.warning(f"Weak password (missing digit) for email: {data.get('email')}")
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            logger.warning(f"Weak password (missing special char) for email: {data.get('email')}")
            raise serializers.ValidationError("Password must contain at least one special character.")
        if re.search(r"\s", password):
            logger.warning(f"Password contains space for email: {data.get('email')}")
            raise serializers.ValidationError("Password must not contain spaces.")
        logger.info(f"Password validated for registration: {data.get('email')}")
        return data

class SendEmailOTPSerializer(serializers.Serializer):
    """
    Serializer for sending OTP to email during registration or password reset.
    """
    email = serializers.EmailField()
    # purpose = serializers.ChoiceField(choices=['register', 'login', 'forgot_password'])
    def validate_email(self, email):
        logger.info(f"SendEmailOTPSerializer validating email: {email}")
        return email

# class SendMobileOTPSerializer(serializers.Serializer):
#     """
#     Serializer for sending OTP to a mobile number.
#     """
#     phone_no = serializers.CharField(max_length=20)
#     def validate_phone_no(self, phone_no):
#         logger.info(f"SendMobileOTPSerializer validating phone_no: {phone_no}")
#         return phone_no

class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying email or mobile OTP.
    """
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    def validate(self, data):
        logger.info(f"Verifying OTP for email: {data.get('email')}")
        return data

class LoginSerializer(serializers.Serializer):
    """
    Serializer for logging in a user with email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    def validate(self, data):
        logger.info(f"Login attempt for email: {data.get('email')}")
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for initiating the forgot password process via email.
    """
    email = serializers.EmailField()
    def validate_email(self, email):
        logger.info(f"Forgot password requested for email: {email}")
        return email

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting the password using a verified OTP.
    """
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField()

    def validate_new_password(self, password):
        """
        Validate the strength of the new password.
        """
        if len(password) < 8:
            logger.warning("New password too short")
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            logger.warning("New password missing uppercase")
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            logger.warning("New password missing lowercase")
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            logger.warning("New password missing digit")
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            logger.warning("New password missing special character")
            raise serializers.ValidationError("Password must contain at least one special character.")
        if re.search(r"\s", password):
            logger.warning("New password contains spaces")
            raise serializers.ValidationError("Password must not contain spaces.")
        logger.info("New password validated successfully")
        return password
    

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details.
    """
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_no', 
            'region'
        ]

        # read_only_fields = ['email']  # Don't allow changing email
    # def update(self, instance, validated_data):
    #     """
    #     Update the user profile with validated data.
    #     """
    #     instance.first_name = validated_data.get('first_name', instance.first_name)
    #     instance.last_name = validated_data.get('last_name', instance.last_name)
    #     instance.phone_no = validated_data.get('phone_no', instance.phone_no)
    #     instance.region = validated_data.get('region', instance.region)
    #     instance.save()
    #     logger.info(f"User profile updated for email: {instance.email}")
    #     return instance