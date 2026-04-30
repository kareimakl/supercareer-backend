from rest_framework import serializers
from .models import CV, Proposal, CVExperience, CVEducation
from opportunities.serializers import JobSerializer, ProjectSerializer

class CVExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVExperience
        fields = ['is_current', 'job_title', 'company', 'start_date', 'end_date', 'description']

    def to_representation(self, instance):
        return {
            "I currently work here": instance.is_current,
            "Job Title": instance.job_title,
            "Company": instance.company,
            "Start Date": instance.start_date,
            "End Date": instance.end_date,
            "Description": instance.description
        }

class CVEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVEducation
        fields = ['school', 'degree', 'graduation_year', 'description']

    def to_representation(self, instance):
        return {
            "School / University": instance.school,
            "Degree / Qualification": instance.degree,
            "Year of Graduation": instance.graduation_year,
            "Additional Details": instance.description
        }

class CVSerializer(serializers.ModelSerializer):
    experiences = CVExperienceSerializer(many=True, read_only=True)
    education_history = CVEducationSerializer(many=True, read_only=True)
    skills = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    

    class Meta:
        model = CV
        fields = [
            'id', 'user', 'job', 'full_name', 'phone_number', 'professional_title', 
            'email_address', 'location', 'portfolio_url', 'professional_summary', 
            'content', 'ats_score', 'skills', 'experiences', 'education_history', 'created_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data.get("id"),
            "user": data.get("user"),
            "job": data.get("job"),
            "Personal Details": {
                "Full Name": data.get("full_name"),
                "Phone Number": data.get("phone_number"),
                "Professional Title": data.get("professional_title"),
                "Email Address": data.get("email_address"),
                "Location": data.get("location"),
                "Portfolio / LinkedIn URL": data.get("portfolio_url"),
                "Professional Summary": data.get("professional_summary")
            },
            "Experience": data.get("experiences"),
            "Education": data.get("education_history"),
            "Skills": data.get("skills"),
            "ats_score": data.get("ats_score"),
            "created_at": data.get("created_at")
        }

class ProposalSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = Proposal
        fields = ['id', 'user', 'job', 'project', 'content', 'status', 'created_at', 'job_details', 'project_details']
        read_only_fields = ['user', 'created_at']
