# accounts/views_refresh.py
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.models import User
from utils.response import success_response


class TokenRefreshWithUserView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # Let SimpleJWT handle refresh first
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data  # contains 'access' and maybe 'refresh'

        # Decode new access to fetch user
        authenticator = JWTAuthentication()
        validated_token = authenticator.get_validated_token(tokens["access"])
        user = authenticator.get_user(validated_token)

        response_payload = {
            # access (and refresh if ROTATE_REFRESH_TOKENS=True)
            "tokens": tokens,
            "user": {
                "id": user.id,
                "email": getattr(user, "email", ""),
                "full_name": getattr(user, "full_name", ""),
                "groups": list(user.groups.values_list("name", flat=True)),
            },
        }

        return success_response(
            message="Token refreshed successfully",
            data=response_payload,
            status_code=status.HTTP_200_OK,
        )
