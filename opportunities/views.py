from django.db.models import Prefetch
from matching.models import MatchResult
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Job, FreelanceProject
from .serializers import JobSerializer, ProjectSerializer, RefreshResponseSerializer
from drf_spectacular.utils import extend_schema
from documents.models import Proposal
from documents.serializers import ProposalSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Skill

class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            return Job.objects.prefetch_related(
                'required_skills',
                Prefetch(
                    'matchresult_set',
                    queryset=MatchResult.objects.filter(user=user),
                    to_attr='user_matches'
                )
            ).all().order_by('-id')
        return Job.objects.prefetch_related('required_skills').all().order_by('-id')

class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            return FreelanceProject.objects.prefetch_related(
                'required_skills',
                Prefetch(
                    'matchresult_set',
                    queryset=MatchResult.objects.filter(user=user),
                    to_attr='user_matches'
                )
            ).all().order_by('-id')
        return FreelanceProject.objects.prefetch_related('required_skills').all().order_by('-id')




class RefreshProjectsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RefreshResponseSerializer

    @extend_schema(responses={200: RefreshResponseSerializer})
    def post(self, request):
        # Scraping is handled by an external service that writes directly to the database.
        # This endpoint simply reports the current count of projects in the DB.
        total_count = FreelanceProject.objects.count()
        return Response({
            "message": "Projects loaded from database successfully",
            "imported_count": total_count
        }, status=status.HTTP_200_OK)

class ProposalCreateView(generics.CreateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')
        job = serializer.validated_data.get('job')
        content = serializer.validated_data.get('content')
        
        # If content is "AI_GEN", generate it using Gemini
        if content == "AI_GEN":
            target = project if project else job
            if target:
                profile_str = f"Name: {user.get_full_name()}, Bio: {user.profile.bio}, Skills: {', '.join([s.name for s in user.profile.skills.all()])}"
                target_str = f"Title: {target.title}, Description: {target.description}"
                # content = generate_proposal(profile_str, target_str)
                content = "AI Proposal Generation is currently disabled."
        
        serializer.save(user=user, content=content)
