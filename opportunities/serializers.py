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
        if hasattr(obj, 'user_matches'):
            matches = obj.user_matches
            if matches:
                return int(matches[0].match_score)
            return 0
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            from matching.models import MatchResult
            match = MatchResult.objects.filter(user=request.user, job=obj).first()
            if match:
                return int(match.match_score)
        return 0


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
        if hasattr(obj, 'user_matches'):
            matches = obj.user_matches
            if matches:
                return int(matches[0].match_score)
            return 0
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            from matching.models import MatchResult
            match = MatchResult.objects.filter(user=request.user, project=obj).first()
            if match:
                return int(match.match_score)
        return 0


class RefreshResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    imported_count = serializers.IntegerField()
