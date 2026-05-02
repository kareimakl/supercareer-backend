from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MatchResult
from .serializers import MatchResultSerializer
from .match import get_ai_match, generate_ai_proposal
from opportunities.models import Job, FreelanceProject
from concurrent.futures import ThreadPoolExecutor
from django.db import connection

# 1. API خاص بمطابقة الوظائف فقط
class JobMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if not hasattr(user, 'profile'):
                return Response({"error": "No profile found"}, status=400)
            
            profile_str = f"Skills: {[s.name for s in user.profile.skills.all()]}. Bio: {user.profile.bio}"
            
            # بنجيب أحدث 50 وظيفة
            jobs = Job.objects.all().order_by('-posted_date')[:50] 
            
            def process_job(job):
                try:
                    score, matched, tips = get_ai_match(profile_str, f"{job.title} {job.description}")
                    MatchResult.objects.update_or_create(
                        user=user, job=job,
                        defaults={"match_score": score, "matched_skills": matched, "ai_tips": tips}
                    )
                except Exception:
                    pass
                finally:
                    # مهم جداً في Django عند استخدام الـ Threads
                    # نقفل الكونكشن الخاص بكل thread عشان ميحصلش تعليق في قاعدة البيانات
                    connection.close()

            # تنفيذ الطلبات بالتوازي (10 في المرة الواحدة)
            with ThreadPoolExecutor(max_workers=10) as executor:
                # بنستخدم list() عشان نجبر الكود ينتظر تنفيذ كل الـ threads قبل ما يكمل
                list(executor.map(process_job, jobs))
            
            # بنعرض لليوزر الأعلى سكور الأول، ولو السكور متساوي بنجيب الأحدث
            matches = MatchResult.objects.filter(user=user, job__isnull=False).order_by('-match_score', '-job__posted_date')
            return Response(MatchResultSerializer(matches, many=True, context={'request': request}).data)
        except Exception as e:
            import traceback
            return Response({
                "error": "Internal Server Error",
                "details": str(e),
                "traceback": traceback.format_exc()
            }, status=500)

# 2. API خاص بمطابقة المشاريع (Freelance) فقط
class ProjectMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if not hasattr(user, 'profile'):
                return Response({"error": "No profile found"}, status=400)
            
            profile_str = f"Skills: {[s.name for s in user.profile.skills.all()]}. Bio: {user.profile.bio}"
            
            # بنجيب أحدث 50 مشروع
            projects = FreelanceProject.objects.all().order_by('-posted_date')[:50]
            
            def process_project(project):
                try:
                    score, matched, tips = get_ai_match(profile_str, f"{project.title} {project.description}")
                    MatchResult.objects.update_or_create(
                        user=user, project=project,
                        defaults={"match_score": score, "matched_skills": matched, "ai_tips": tips}
                    )
                except Exception:
                    pass
                finally:
                    connection.close()

            with ThreadPoolExecutor(max_workers=10) as executor:
                list(executor.map(process_project, projects))
            
            matches = MatchResult.objects.filter(user=user, project__isnull=False).order_by('-match_score', '-project__posted_date')
            return Response(MatchResultSerializer(matches, many=True, context={'request': request}).data)
        except Exception as e:
            import traceback
            return Response({
                "error": "Internal Server Error",
                "details": str(e),
                "traceback": traceback.format_exc()
            }, status=500)

# 3. API لتوليد مقترح (Proposal)
class ProposalGeneratorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response({"error": "project_id is required"}, status=400)
            
        try:
            project = FreelanceProject.objects.get(id=project_id)
        except FreelanceProject.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)
            
        if not hasattr(user, 'profile'):
            return Response({"error": "No profile found"}, status=400)
            
        profile_data = {
            "skills": [s.name for s in user.profile.skills.all()],
            "bio": user.profile.bio,
            "full_name": user.profile.full_name
        }
        
        proposal_text = generate_ai_proposal(profile_data, project.description)
        return Response({"proposal": proposal_text})
