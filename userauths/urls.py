from django.urls import path

# JWT Views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Local Views
from .views import (
    RegisterView,
    VerifyEmailOTPView,
    # VerifyMobileOTPView,
    SendEmailOTPView,
    # SendMobileOTPView,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    UserProfileView
)

urlpatterns = [
    # Registration and OTP
    path('register/', RegisterView.as_view(), name='register'),
    path('send-email-otp/', SendEmailOTPView.as_view(), name='send_email_otp'),
    path('verify-email/', VerifyEmailOTPView.as_view(), name='verify_email'),
    # path('send-mobile-otp/', SendMobileOTPView.as_view(), name='send_mobile_otp'),
    # path('verify-mobile/', VerifyMobileOTPView.as_view(), name='verify_mobile'),

    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Password Management
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # JWT Token Management
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
