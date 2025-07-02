from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Preference
from .serializers import PreferenceSerializer

# Create your views here.

class PreferenceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retrieve the current user's preferences
        """
        try:
            preference = Preference.objects.get(user=request.user)
            serializer = PreferenceSerializer(preference)
            return Response(serializer.data)
        except Preference.DoesNotExist:
            return Response(
                {"detail": "Preferences not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request):
        """
        Create new preferences for the current user
        """
        # Check if user already has preferences
        if hasattr(request.user, 'preferences'):
            return Response(
                {"detail": "Preferences already exist. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = PreferenceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """
        Update existing preferences for the current user
        """
        try:
            preference = Preference.objects.get(user=request.user)
            serializer = PreferenceSerializer(preference, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Preference.DoesNotExist:
            return Response(
                {"detail": "Preferences not found. Use POST to create new preferences."},
                status=status.HTTP_404_NOT_FOUND
            )
