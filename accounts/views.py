from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from utils.response import error_response, success_response  # <-- use the helper
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import LoginSerializer
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from utils.response import success_response, error_response
from utils.password import generate_strong_password
from .serializers import InviteUserSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        include_permissions = serializer.validated_data.get("include_permissions", False)

        # issue tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        payload = {

                "access_token": access,
                "refresh_token": str(refresh),
                "id": user.id,
                "email": user.email,
                "full_name": getattr(user, "full_name", ""),
                "phone": getattr(user, "phone", ""),
                "groups": serializer.get_groups(user),
                "permissions": serializer.get_permissions(user),

        }

        return success_response(
            message="Logged in successfully",
            data=payload,
            status_code=status.HTTP_200_OK,
        )

class LogoutView(APIView):
    """
    Blacklist the provided refresh token so it can’t be used again.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return error_response("Refresh token is required.", status_code=400)

        try:
            serializer = TokenBlacklistSerializer(data={"refresh": refresh})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as exc:
            # If token already blacklisted/invalid, treat as success (idempotent logout)
            return success_response(message="Logged out.", data=[], status_code=200)

        return success_response(message="Logged out.", data=[], status_code=200)
    

class InviteUserView(APIView):
    """
    Superadmin/Admin invites a user by email and assigns a group.
    Generates a password and emails it to the user.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @transaction.atomic
    def post(self, request):
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1) Generate strong password
        plain_password = generate_strong_password(12)

        # 2) Create user + assign group
        user = serializer.save()
        user.set_password(plain_password)
        user.save(update_fields=["password"])

        # 3) Email the password (adjust template as needed)
        subject = "Your account has been created"
        app_url = getattr(settings, "FRONTEND_LOGIN_URL", "")
        message_lines = [
            f"Hello {getattr(user, 'full_name', '') or user.email},",
            "",
            "Your account has been created. Use the credentials below to sign in:",
            f"Email: {user.email}",
            f"Password: {plain_password}",
            "",
            f"Login here: {app_url}" if app_url else "",
            "",
            "For security, please change your password after logging in.",
        ]
        message = "\n".join([line for line in message_lines if line is not None])

        email_status = "sent"
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            # We don’t rollback user creation, but we report email failure
            email_status = "failed"

        data = {
            "id": str(user.id),
            "email": user.email,
            "full_name": getattr(user, "full_name", ""),
            "groups": list(user.groups.values_list("name", flat=True)),
            "email_delivery": email_status,
        }

        # IMPORTANT: do NOT return the plain password in the API response
        return success_response(
            message="User invited successfully.",
            data=data,
            status_code=status.HTTP_201_CREATED,
        )