from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .serializers import (
    RegisterSerializer, ProfileSerializer, CustomTokenObtainPairSerializer, 
    UserSerializer, DashboardStatsSerializer, GoogleAuthSerializer, 
    ChangePasswordSerializer, LogoutSerializer
)
from drf_spectacular.utils import extend_schema
from .models import User, UserProfile
from opportunities.models import Job, FreelanceProject
from documents.models import Proposal
from matching.models import MatchResult
from django.db.models import Avg
from django.utils import timezone


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Return the created data including profile info and tokens
            response_data = {
                "message": "User and Profile created successfully",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": UserSerializer(user).data,
                "profile": ProfileSerializer(user.profile).data
            }
            return Response(response_data, status=201)

        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            # Handle either 'refresh' or 'token' key for flexibility
            refresh_token = request.data.get("refresh") or request.data.get("token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except (TokenError, KeyError):
            return Response({"error": "Invalid token or token missing"}, status=400)


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer
    """Authenticate and log in users using a Google OAuth2 ID token."""

    def post(self, request):
        id_token_str = request.data.get('id_token') or request.data.get('token')
        if not id_token_str:
            return Response({'error': 'id_token is required'}, status=400)

        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {'error': 'GOOGLE_CLIENT_ID is not configured on the server environment.'},
                status=500,
            )

        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=400)

        email = id_info.get('email')
        if not email:
            return Response({'error': 'Google token did not contain an email'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found. Please register first.'}, status=404)

        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user)

        # Issue tokens
        refresh = RefreshToken.for_user(user)
        response_data = {
            'message': 'Logged in with Google successfully',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(user.profile).data,
        }
        return Response(response_data, status=200)


class GoogleRegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer
    """Register users using a Google OAuth2 ID token."""

    def post(self, request):
        id_token_str = request.data.get('id_token') or request.data.get('token')
        if not id_token_str:
            return Response({'error': 'id_token is required'}, status=400)

        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {'error': 'GOOGLE_CLIENT_ID is not configured on the server environment.'},
                status=500,
            )

        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=400)

        email = id_info.get('email')
        if not email:
            return Response({'error': 'Google token did not contain an email'}, status=400)

        user = User.objects.filter(email=email).first()
        if user:
            return Response({'error': 'User with this email already exists. Please log in.'}, status=400)

        role = request.data.get('role')
        if not role:
            return Response({'error': 'role is required for registration'}, status=400)

        first_name = id_info.get('given_name') or ''
        last_name = id_info.get('family_name') or ''
        full_name = id_info.get('name', '')
        if not (first_name or last_name) and full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        username_base = email.split('@')[0]
        username = f"{username_base}_{get_random_string(6)}"
        
        user = User.objects.create_user(
            email=email,
            username=username,
            role=role,
            first_name=first_name,
            last_name=last_name,
            password=None,
        )
        user.set_unusable_password()
        user.save()

        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user)

        # Issue tokens
        refresh = RefreshToken.for_user(user)
        response_data = {
            'message': 'Registered with Google successfully',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(user.profile).data,
        }
        return Response(response_data, status=201)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request):
        profile = UserProfile.objects.select_related('user')\
            .prefetch_related('skills', 'experiences', 'education_history')\
            .get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = UserProfile.objects.select_related('user').get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardStatsSerializer

    @extend_schema(responses={200: DashboardStatsSerializer})

    def get(self, request):
        user = request.user
        profile = user.profile
        
        # Stats calculation
        today = timezone.now().date()
        matches_today = MatchResult.objects.filter(user=user, created_at__date=today).count()
        active_proposals = Proposal.objects.filter(user=user, status='sent').count()
        
        avg_match_score = MatchResult.objects.filter(user=user).aggregate(Avg('match_score'))['match_score__avg'] or 0
        
        data = {
            "matches_today": matches_today,
            "active_proposals": active_proposals,
            "avg_match_score": round(avg_match_score * 100, 1) if avg_match_score <= 1 else round(avg_match_score, 1),
            "profile_views": profile.profile_views,
            "user_name": user.first_name or user.username
        }
        return Response(data)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not all([old_password, new_password, confirm_password]):
            return Response({"error": "All fields are required."}, status=400)

        if new_password != confirm_password:
            return Response({"error": "New passwords do not match."}, status=400)

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password."}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."})
