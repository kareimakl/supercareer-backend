from rest_framework import serializers
from .models import Job, FreelanceProject
from drf_spectacular.utils import extend_schema_field

class JobSerializer(serializers.ModelSerializer):
    match_score = serializers.SerializerMethodField()
    required_skills = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

    @extend_schema_field(serializers.IntegerField)
    def get_match_score(self, obj):
        # Placeholder for AI match score logic
        return 85

class ProjectSerializer(serializers.ModelSerializer):
    match_score = serializers.SerializerMethodField()
    required_skills = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = FreelanceProject
        fields = [
            'id', 'title', 'description', 'budget', 'deadline', 
            'duration', 'status', 'required_skills', 'platform_name', 
            'source_url', 'posted_date', 'scraped_at', 'match_score'
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_match_score(self, obj):
        # Placeholder for AI match score logic
        return 90

class RefreshResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    imported_count = serializers.IntegerField()
