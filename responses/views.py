# responses/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response as DRF_Response
from rest_framework.permissions import IsAuthenticated
from .models import Response
from .serializers import ResponseSerializer

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return DRF_Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )