import subprocess
import os
import csv
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Job, FreelanceProject
from accounts.models import Skill
from .serializers import JobSerializer, ProjectSerializer, RefreshResponseSerializer
from drf_spectacular.utils import extend_schema
from documents.models import Proposal
from documents.serializers import ProposalSerializer
# from ai_llm.ai_llm.proposal import generate_proposal
from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Skill

class JobListView(generics.ListAPIView):
    queryset = Job.objects.prefetch_related('required_skills').all()
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

class ProjectListView(generics.ListAPIView):
    queryset = FreelanceProject.objects.prefetch_related('required_skills').all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]



class RefreshProjectsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RefreshResponseSerializer

    @extend_schema(responses={200: RefreshResponseSerializer})

    def post(self, request):
        try:
            print("--- RefreshProjectsView Start ---")
            scraper_path = os.path.normpath(os.path.join(settings.BASE_DIR, '..', 'web-scraping', 'scraper', 'mostaql_sqraper.py'))
            print(f"Scraper Path: {scraper_path}")
            
            if not os.path.exists(scraper_path):
                return Response({"error": "Scraper script not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Run scraper via subprocess using binary mode to avoid encoding crashes
            import sys
            print(f"Python Executable: {sys.executable}")
            # We capture output as bytes and decode with errors='replace' to avoid UnicodeDecodeError
            process = subprocess.run([sys.executable, scraper_path], capture_output=True)
            
            stdout = process.stdout.decode('utf-8', errors='replace') if process.stdout else ""
            stderr = process.stderr.decode('utf-8', errors='replace') if process.stderr else ""
            
            if stdout:
                print(f"Scraper STDOUT: {stdout[:500]}...")
            if stderr:
                print(f"Scraper STDERR: {stderr}")

            if process.returncode != 0:
                return Response({"error": f"Scraper failed: {stderr}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 2. Import Data from CSV
            csv_path = os.path.normpath(os.path.join(settings.BASE_DIR, '..', 'web-scraping', 'data', 'mostaql_projects.csv'))
            if not os.path.exists(csv_path):
                return Response({"error": "CSV data not found after scraping"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            imported_count = self.import_data(csv_path)
            print(f"Successfully imported: {imported_count}")
            
            return Response({
                "message": "Projects refreshed successfully",
                "imported_count": imported_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Exception in RefreshProjectsView: {str(e)}")
            return Response({"error": str(e), "trace": error_trace}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def import_data(self, csv_path):
        count = 0
        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                headers = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
                reader.fieldnames = headers

                for row in reader:
                    link = row.get('link')
                    if not link or FreelanceProject.objects.filter(source_url=link).exists():
                        continue
                    
                    project = FreelanceProject.objects.create(
                        title=row.get('project_name', ''),
                        description=row.get('project_details', ''),
                        budget=row.get('budget', '').strip() if row.get('budget') else None,
                        duration=row.get('duration', '').strip() if row.get('duration') else None,
                        status=row.get('project_status', 'مفتوح'),
                        platform_name='Mostaql',
                        source_url=link,
                        posted_date=self.parse_date(row.get('publish_date'))
                    )
                    
                    # Skills
                    skills_str = row.get('skills')
                    if skills_str:
                        skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
                        for skill_name in skills_list:
                            skill, _ = Skill.objects.get_or_create(name=skill_name)
                            project.required_skills.add(skill)
                    
                    count += 1
        except Exception as e:
            print(f"Error during import_data: {e}")
            raise e
        return count

    def parse_date(self, date_str):
        if not date_str:
            return None
        try:
            from django.utils import timezone
            # Mostaql usually provides ISO like 2024-03-17T20:25:00Z
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            # Make timezone aware if needed
            if timezone.is_naive(dt):
                return timezone.make_aware(dt)
            return dt
        except (ValueError, TypeError):
            return None

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
