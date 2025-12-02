# accounts/serializers.py
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

User = get_user_model()


# ---------- AUTH ----------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    # toggle this if you also want to return permissions codenames
    include_permissions = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # NOTE: Ensure AUTHENTICATION_BACKENDS supports email authentication.
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        # not used; the view builds the response
        return super().to_representation(instance)

    def get_groups(self, user: User) -> list[str]:
        return list(user.groups.values_list("name", flat=True))

    def get_permissions(self, user: User) -> list[str]:
        # user perms (direct + via groups)
        perms = Permission.objects.filter(user=user).values_list("codename", flat=True)
        group_perms = Permission.objects.filter(group__user=user).values_list(
            "codename", flat=True
        )
        return sorted(set(list(perms) + list(group_perms)))


# ---------- GROUPS ----------
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


# ---------- INVITE USER ----------
class InviteUserSerializer(serializers.Serializer):
    """
    Invites a single user and assigns them to one group.
    Accepts group by id (recommended) or by name.
    """

    email = serializers.EmailField()
    group = serializers.CharField()  # id or name
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(
        required=False, allow_blank=True
    )  # ignored (User has no phone)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def _resolve_group(self, value: str) -> Group:
        """
        Try to resolve group by ID first, then by name (case-insensitive).
        """
        # by id
        try:
            return Group.objects.get(id=value)
        except (Group.DoesNotExist, ValueError):
            pass
        # by name
        try:
            return Group.objects.get(name__iexact=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Invalid group")

    def validate(self, attrs):
        # resolve and stash the Group instance for use in create()
        
        attrs["_group_obj"] = self._resolve_group(attrs["group"])
        return attrs

    def create(self, validated_data):
        """
        We don't set password here; the view generates it and emails it.
        """
        group_obj: Group = validated_data.pop("_group_obj")
        validated_data.pop("group", None)

        # Optional fields that don't exist on the model should be removed
        phone = validated_data.pop("phone", None)  # ignored safely

        # Only fields that exist on User: email, full_name
        full_name = validated_data.get("full_name", "")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=None,
            full_name=full_name,
        )
        user.groups.set([group_obj])
        return user


# ---------- USERS LIST (for pagination endpoint) ----------
class UserListSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "is_active",
            "last_login",
            "date_joined",
            "groups",
        )

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))



class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)  

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "groups"]