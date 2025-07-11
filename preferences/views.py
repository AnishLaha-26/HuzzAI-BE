from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Preferences
from .serializers import PreferenceSerializer

# Create your views here.

class PreferenceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retrieve the current user's preferences
        """
        try:
            preferences = Preferences.objects.get(user=request.user)
            serializer = PreferenceSerializer(preferences)
            return Response(serializer.data)
        except Preferences.DoesNotExist:
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
            
        # Map frontend field names to backend field names
        data = request.data.copy()
        if 'gender' in data:
            data['sex'] = data.pop('gender')
        if 'age' in data:
            data['age_group'] = data.pop('age')
        if 'goals' in data:
            data['dating_goal'] = data.pop('goals')
        if 'preferred_platform' in data:
            data['chat_platform'] = data.pop('preferred_platform')
            
        serializer = PreferenceSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """
        Update existing preferences for the current user
        """
        try:
            preferences = Preferences.objects.get(user=request.user)
            
            # Map frontend field names to backend field names
            data = request.data.copy()
            if 'gender' in data:
                data['sex'] = data.pop('gender')
            if 'age' in data:
                data['age_group'] = data.pop('age')
            if 'goals' in data:
                data['dating_goal'] = data.pop('goals')
            if 'preferred_platform' in data:
                data['chat_platform'] = data.pop('preferred_platform')
                
            serializer = PreferenceSerializer(preferences, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Preferences.DoesNotExist:
            return Response(
                {"detail": "Preferences not found. Use POST to create new preferences."},
                status=status.HTTP_404_NOT_FOUND
            )
