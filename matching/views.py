from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import MatchResult
from .serializers import MatchResultSerializer

from .match import match
from opportunities.models import Job, FreelanceProject

class MatchListView(generics.ListAPIView):
    serializer_class = MatchResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            queryset = MatchResult.objects.filter(user=user)
            
            # Trigger a refresh of scores for the first few items for demo purposes
            # Check if user.profile exists
            if not hasattr(user, 'profile'):
                return MatchResult.objects.none()

            profile_str = f"Bio: {user.profile.bio or ''}, Skills: {', '.join([s.name for s in user.profile.skills.all()])}"
            # Match against jobs
            for job in Job.objects.all()[:50]:
                try:
                    project_str = f"Title: {job.title}, Description: {job.description}"
                    score = match(profile_str, project_str)
                    MatchResult.objects.update_or_create(
                        user=user,
                        job=job,
                        defaults={
                            "match_score": score,
                            "matched_skills": [],
                            "missing_skills": [],
                            "ai_tips": ""
                        }
                    )
                except Exception as e:
                    print(f"Error matching job {job.id}: {e}")
                    continue
            
            # Match against projects
            for project in FreelanceProject.objects.all()[:50]:
                try:
                    project_str = f"Title: {project.title}, Description: {project.description}"
                    score = match(profile_str, project_str)
                    MatchResult.objects.update_or_create(
                        user=user,
                        project=project,
                        defaults={
                            "match_score": score,
                            "matched_skills": [],
                            "missing_skills": [],
                            "ai_tips": ""
                        }
                    )
                except Exception as e:
                    print(f"Error matching project {project.id}: {e}")
                    continue
            queryset = MatchResult.objects.filter(user=user)
            return queryset.order_by('-match_score')
        except Exception as e:
            import traceback
            print(f"MatchListView Error: {str(e)}")
            print(traceback.format_exc())
            # For debugging, we can raise it or return empty
            raise e
