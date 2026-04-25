from rest_framework import serializers
from .models import Job, FreelanceProject
from drf_spectacular.utils import extend_schema_field
from matching.models import MatchResult 

# 1. سيرياليزر الوظائف
class JobSerializer(serializers.ModelSerializer):
    match_score = serializers.SerializerMethodField()
    required_skills = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

    @extend_schema_field(serializers.FloatField)
    def get_match_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            match = MatchResult.objects.filter(user=request.user, job=obj).first()
            return match.match_score if match else 0.0
        return 0.0

# 2. سيرياليزر المشاريع (الفريلانس)
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

    # ركز هنا: الدالة دي لازم تكون "جوه" كلاس ProjectSerializer
    @extend_schema_field(serializers.FloatField)
    def get_match_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # بنبحث في جدول الماتش عن المشروع ده لليوزر ده
            match = MatchResult.objects.filter(user=request.user, project=obj).first()
            return match.match_score if match else 0.0
        return 0.0

# 3. سيرياليزر الرد (لو محتاجه)
class RefreshResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    imported_count = serializers.IntegerField()