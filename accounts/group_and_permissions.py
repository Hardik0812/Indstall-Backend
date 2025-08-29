from django.contrib.auth.models import Group
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .permissions import IsAdminUser
from utils.response import success_response
from .serializers import GroupSerializer

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