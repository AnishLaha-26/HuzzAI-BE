from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import User, PasswordResetToken
from .serializers import (
    UserSerializer, 
    RegisterSerializer, 
    LoginSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ForgotPasswordView(APIView):
    """View to handle forgot password requests"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("\n=== ForgotPasswordView Reached ===")
        print("Request data:", request.data)
        print("Request headers:", dict(request.headers))
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email, is_active=True)
                
                # Create password reset token
                reset_token = PasswordResetToken.objects.create(user=user)
                
                # Send email with reset link
                self.send_reset_email(user, reset_token)
                
                return Response({
                    'message': 'If your email exists in our system, you will receive a password reset link.'
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                # Don't reveal if user exists or not for security
                return Response({
                    'message': 'If your email exists in our system, you will receive a password reset link.'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_reset_email(self, user, reset_token):
        """Send password reset email to user"""
        try:
            # Create the reset URL - you'll need to adjust this URL based on your frontend
            reset_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token.token}"
            
            subject = 'Password Reset Request'
            
            # Create HTML email content
            html_message = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user.get_full_name() or user.email},</p>
                <p>You have requested to reset your password. Click the link below to reset your password:</p>
                <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Reset Password</a></p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p>{reset_url}</p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Your App Team</p>
            </body>
            </html>
            """
            
            # Create plain text version
            plain_message = f"""
            Password Reset Request
            
            Hello {user.get_full_name() or user.email},
            
            You have requested to reset your password. Click the link below to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            Your App Team
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourapp.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
        except Exception as e:
            # Log the error in production
            print(f"Failed to send password reset email: {str(e)}")


class ResetPasswordView(APIView):
    """View to handle password reset"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Password has been reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = None  # We'll define this in the method
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = request.data

        # Check old password
        if not self.object.check_password(data.get("old_password")):
            return Response({"old_password": ["Wrong password."]}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check new password and confirmation match
        if data.get("new_password") != data.get("new_password2"):
            return Response({"new_password": ["New passwords must match"]}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Set the new password
        self.object.set_password(data.get("new_password"))
        self.object.save()
        
        return Response({"message": "Password updated successfully"}, 
                       status=status.HTTP_200_OK)
