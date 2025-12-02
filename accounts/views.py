from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from utils.password import generate_strong_password
from utils.permissions import IsAdminUser
from utils.response import error_response, success_response
from utils.pagination import (
    parse_pagination,
    validate_ordering,
    paginate_queryset,
)
from django.db.models import Q
from .serializers import (
    GroupSerializer,
    InviteUserSerializer,
    LoginSerializer,
    User,
    UserListSerializer,
    UserSerializer,
)
from rest_framework import generics, permissions

class GroupListView(APIView):
    """
    List all available groups (roles).
    Only superusers/admins can see this list.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return success_response(
            message="Groups fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        include_permissions = serializer.validated_data.get(
            "include_permissions", False
        )

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


class UsersListView(APIView):
    """
    GET /api/v1/accounts/users/
      ?page=1
      &page_size=20
      &search=jane
      &is_active=true|false
      &group=Staff          # exact name (you can switch to id if you prefer)
      &ordering=-date_joined  # one of: email, full_name, date_joined, last_login, is_active
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    # allowed fields for ?ordering=
    ORDERING_FIELDS = {"email", "full_name", "date_joined", "last_login", "is_active"}

    def get(self, request):
        # 1) Base queryset
        qs = (
            User.objects.all()
            .select_related()
            .prefetch_related("groups")
            .order_by()  # clear default ordering
        )

        # 2) Filters
        search = (request.query_params.get("search") or "").strip()
        if search:
            qs = qs.filter(Q(email__icontains=search) | Q(full_name__icontains=search))

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            v = is_active.lower()
            if v in ("true", "1", "yes"):
                qs = qs.filter(is_active=True)
            elif v in ("false", "0", "no"):
                qs = qs.filter(is_active=False)

        group = request.query_params.get("group")
        if group:
            qs = qs.filter(groups__name=group)

        # 3) Ordering (validated)
        ordering = validate_ordering(
            request,
            allowed_fields=self.ORDERING_FIELDS,
            default="-date_joined",
        )
        qs = qs.order_by(ordering)

        # 4) Pagination (your helpers)
        page, page_size = parse_pagination(
            request, default_page=1, default_page_size=20, max_page_size=100
        )
        page_obj, meta = paginate_queryset(qs, page, page_size)

        # 5) Serialize current page
        serializer = UserListSerializer(page_obj.object_list, many=True)

        # 6) Wrap in your success_response
        # meta already has: page, page_size, total_pages, total_items, has_next, has_prev, next_page, prev_page
        payload = {**meta, "results": serializer.data}

        return success_response(
            message="Users fetched successfully.",
            data=payload,
            status_code=status.HTTP_200_OK,
        )

class SalesEngineerListView(generics.ListAPIView):
    """
    List all users belonging to the 'Sales' group.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only users in the 'Sales' group.
        """
        try:
            sales_group = Group.objects.get(name="Sales")
            return User.objects.filter(groups=sales_group)
        except Group.DoesNotExist:
            return User.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Override to send a custom response format.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
           data=serializer.data,
           message="Sales engineers fetched successfully.",
           status_code=status.HTTP_200_OK,
        )