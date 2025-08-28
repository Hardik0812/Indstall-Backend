from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Permission
from rest_framework import serializers
from django.contrib.auth.models import Group
from accounts.models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # toggle this if you also want to return permissions codenames
    include_permissions = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        # not used
        return super().to_representation(instance)

    def get_groups(self, user: User) -> list[str]:
        return list(user.groups.values_list("name", flat=True))

    def get_permissions(self, user: User) -> list[str]:
        # user perms (direct + via groups)
        perms = Permission.objects.filter(user=user).values_list("codename", flat=True)
        group_perms = Permission.objects.filter(group__user=user).values_list("codename", flat=True)
        return sorted(set(list(perms) + list(group_perms)))


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    group = serializers.CharField()  # single select from your frontend
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_group(self, value):
        try:
            Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Invalid group")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """
        We don't set password here; the view will generate one and set it,
        so it can also email it.
        """
        group_id = validated_data.pop("group")
        user = User.objects.create_user(**validated_data, password=None)
        group = Group.objects.get(id=group_id)
        user.groups.set([group])
        return user