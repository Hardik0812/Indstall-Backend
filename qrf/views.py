from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from utils.permissions import IsSalesUser
from utils.response import error_response, success_response

from .serializers import QRFCreateSerializer, QRFDetailSerializer


class QRFCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSalesUser]

    def post(self, request):
        serializer = QRFCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            qrf = serializer.save()
            return success_response(
                message="QRF created successfully.",
                data=QRFDetailSerializer(qrf).data,
                status_code=status.HTTP_201_CREATED,
            )
        return error_response(
            message="Invalid data.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
