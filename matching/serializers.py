from rest_framework import serializers
from .models import MatchResult
# غيرنا FreelanceProjectSerializer لـ ProjectSerializer عشان يطابق الملف التاني
from opportunities.serializers import JobSerializer, ProjectSerializer 

class MatchResultSerializer(serializers.ModelSerializer):
    # بنستخدم الاسم الجديد هنا كمان
    job_details = JobSerializer(source='job', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)
    
    class Meta:
        model = MatchResult
        fields = [
            'id', 'user', 'job', 'project', 'match_score', 
            'matched_skills', 'missing_skills', 'ai_tips',
            'job_details', 'project_details', 'created_at'
        ]
        read_only_fields = ['match_score', 'matched_skills', 'missing_skills', 'ai_tips', 'created_at']
