from datetime import timedelta

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model.
    Handles user and superuser creation with required fields.
    """

    def create_user(self, email, first_name, last_name, region, phone_no, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is a required field.')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name, 
            last_name = last_name, 
            region=region, 
            phone_no=phone_no, 
            **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, region, phone_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, first_name, last_name, region, phone_no, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model extending AbstractBaseUser.
    """
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    region = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20, unique=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    # is_mobile_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name', 'region', 'phone_no']
    
    def __str__(self):
        return self.email
    

class OTP(models.Model):
    """
    Stores OTPs for email or phone number verification.
    """
    email = models.EmailField(null=True, blank=True)
    # phone_no = models.CharField(max_length=20, null=True, blank=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    PURPOSE_CHOICES = [
        ('register', 'Register'),
        ('reset', 'Password Reset'),
    ]

    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default='register')

    def is_expired(self):
        """
        Check if OTP is expired (valid for 5 minutes).
        """
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.email or self.phone_no}"

class TemporaryUserData(models.Model):
    """
    Temporarily stores user data during the registration process until OTPs are verified.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    phone_no = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    region = models.CharField(max_length=100)
    
    is_email_verified = models.BooleanField(default=False)
    # is_mobile_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email