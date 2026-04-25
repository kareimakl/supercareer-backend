# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated # رجعنا الحماية
# from .models import MatchResult
# from .serializers import MatchResultSerializer
# from .match import get_ai_match
# from opportunities.models import Job

# class UserMatchView(APIView):
#     # الحماية: لازم اليوزر يكون عامل Login عشان يشوف الـ Matches بتاعته بس
#     permission_classes = [IsAuthenticated] 

#     def get(self, request):
#         user = request.user # بنعتمد على اليوزر اللي باعت الـ Request فعلياً
        
#         if not hasattr(user, 'profile'):
#             return Response({"error": "No user profile found."}, status=400)
        
#         profile = user.profile
#         skills_list = [skill.name for skill in profile.skills.all()]
#         profile_str = f"Skills: {', '.join(skills_list)}. Bio: {profile.bio}"

#         # ملاحظة: ممكن تزود عدد الوظائف هنا لـ 10 أو 20 زي ما تحب
#         jobs = Job.objects.all()[:10]
        
#         for job in jobs:
#             job_str = f"Job: {job.title}. Description: {job.description}"
#             score, matched, tips = get_ai_match(profile_str, job_str)
            
#             MatchResult.objects.update_or_create(
#                 user=user, job=job,
#                 defaults={
#                     "match_score": score,
#                     "matched_skills": matched,
#                     "ai_tips": tips
#                 }
#             )

#         matches = MatchResult.objects.filter(user=user).order_by('-match_score')
#         serializer = MatchResultSerializer(matches, many=True, context={'request': request})
#         return Response(serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MatchResult
from .serializers import MatchResultSerializer
from .match import get_ai_match
from opportunities.models import Job, FreelanceProject

# 1. API خاص بمطابقة الوظائف فقط
class JobMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile'):
            return Response({"error": "No profile found"}, status=400)
        
        profile_str = f"Skills: {[s.name for s in user.profile.skills.all()]}. Bio: {user.profile.bio}"
        
        # التعديل هنا: بنجيب أحدث 10 وظائف بناءً على تاريخ النشر
        jobs = Job.objects.all().order_by('-posted_date')[:10] 
        for job in jobs:
            score, matched, tips = get_ai_match(profile_str, f"{job.title} {job.description}")
            MatchResult.objects.update_or_create(
                user=user, job=job,
                defaults={"match_score": score, "matched_skills": matched, "ai_tips": tips}
            )
        
        # بنعرض لليوزر الأعلى سكور الأول، ولو السكور متساوي بنجيب الأحدث
        matches = MatchResult.objects.filter(user=user, job__isnull=False).order_by('-match_score', '-job__posted_date')
        return Response(MatchResultSerializer(matches, many=True, context={'request': request}).data)

# 2. API خاص بمطابقة المشاريع (Freelance) فقط
class ProjectMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile'):
            return Response({"error": "No profile found"}, status=400)

        profile_str = f"Skills: {[s.name for s in user.profile.skills.all()]}. Bio: {user.profile.bio}"
        
        # التعديل هنا: بنجيب أحدث 10 مشاريع فريلانس
        projects = FreelanceProject.objects.all().order_by('-posted_date')[:10]
        for proj in projects:
            score, matched, tips = get_ai_match(profile_str, f"{proj.title} {proj.description}")
            MatchResult.objects.update_or_create(
                user=user, 
                project=proj, 
                defaults={"match_score": score, "matched_skills": matched, "ai_tips": tips}
            )
        
        # عرض المشاريع: الأعلى سكور الأول، ثم الأحدث تاريخياً
        matches = MatchResult.objects.filter(user=user, project__isnull=False).order_by('-match_score', '-project__posted_date')
        return Response(MatchResultSerializer(matches, many=True, context={'request': request}).data)