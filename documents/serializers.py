from rest_framework import serializers
from .models import CV, Proposal, CVExperience, CVEducation
from accounts.models import Skill
from opportunities.serializers import JobSerializer, ProjectSerializer

# Custom field that creates Skill objects if they don't exist
class AutoCreateSkillSlugField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            # Create the skill if it does not exist
            skill, _ = Skill.objects.get_or_create(name=data)
            return skill

class CVExperienceSerializer(serializers.ModelSerializer):
    # استخدام التسميات اللي اليوزر طلبها في الـ request والـ response
    is_current = serializers.BooleanField(label="I currently work here")
    job_title = serializers.CharField(label="Job Title")
    company = serializers.CharField(label="Company")
    start_date = serializers.CharField(label="Start Date")
    end_date = serializers.CharField(required=False, allow_null=True, allow_blank=True, label="End Date")
    description = serializers.CharField(required=False, allow_blank=True, label="Description")

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

    def to_internal_value(self, data):
        # تحويل المفاتيح المخصصة للمفاتيح الأصلية في الموديل ومع دعم المفاتيح العادية كبديل
        mapped_data = {
            'is_current': data.get("I currently work here", data.get("is_current")),
            'job_title': data.get("Job Title", data.get("job_title")),
            'company': data.get("Company", data.get("company")),
            'start_date': data.get("Start Date", data.get("start_date")),
            'end_date': data.get("End Date", data.get("end_date")),
            'description': data.get("Description", data.get("description")),
        }
        return super().to_internal_value({k: v for k, v in mapped_data.items() if v is not None})

class CVEducationSerializer(serializers.ModelSerializer):
    school = serializers.CharField(label="School / University")
    degree = serializers.CharField(label="Degree / Qualification")
    graduation_year = serializers.CharField(label="Year of Graduation")
    description = serializers.CharField(required=False, allow_blank=True, label="Additional Details")

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

    def to_internal_value(self, data):
        mapped_data = {
            'school': data.get("School / University", data.get("school")),
            'degree': data.get("Degree / Qualification", data.get("degree")),
            'graduation_year': data.get("Year of Graduation", data.get("graduation_year")),
            'description': data.get("Additional Details", data.get("description")),
        }
        return super().to_internal_value({k: v for k, v in mapped_data.items() if v is not None})

class CVSerializer(serializers.ModelSerializer):
    # بنغير التسميات للي اليوزر طلبها وبنخليها قابلة للكتابة (Writable Nested)
    Experience = CVExperienceSerializer(many=True, source='experiences', required=False)
    Education = CVEducationSerializer(many=True, source='education_history', required=False)
    Skills = AutoCreateSkillSlugField(many=True, source='skills', slug_field='name', queryset=Skill.objects.all(), required=False)
    
    class Meta:
        model = CV
        fields = [
            'id', 'user', 'job', 'full_name', 'phone_number', 'professional_title', 
            'email_address', 'location', 'portfolio_url', 'professional_summary', 
            'content', 'ats_score', 'is_base', 'Experience', 'Education', 'Skills', 'created_at'
        ]
        read_only_fields = ['user', 'created_at', 'ats_score', 'job']

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "user": instance.user.id if instance.user else None,
            "job": instance.job.id if instance.job else None,
            "is_base": instance.is_base,
            "Personal Details": {
                "Full Name": instance.full_name,
                "Phone Number": instance.phone_number,
                "Professional Title": instance.professional_title,
                "Email Address": instance.email_address,
                "Location": instance.location,
                "Portfolio / LinkedIn URL": instance.portfolio_url,
                "Professional Summary": instance.professional_summary
            },
            "Experience": CVExperienceSerializer(instance.experiences.all(), many=True).data,
            "Education": CVEducationSerializer(instance.education_history.all(), many=True).data,
            "Skills": [s.name for s in instance.skills.all()],
            "ats_score": instance.ats_score,
            "created_at": instance.created_at
        }

    def to_internal_value(self, data):
        # Support case-insensitive keys for Personal Details
        personal = None
        for key in ["Personal Details", "personal_details", "personalDetails"]:
            if key in data:
                personal = data[key]
                break
        
        # We start by copying all keys from data except the personal details keys.
        new_data = {k: v for k, v in data.items() if k not in ["Personal Details", "personal_details", "personalDetails"]}

        field_map = {
            "Full Name": "full_name",
            "full_name": "full_name",
            "fullName": "full_name",
            
            "Phone Number": "phone_number",
            "phone_number": "phone_number",
            "phoneNumber": "phone_number",
            
            "Professional Title": "professional_title",
            "professional_title": "professional_title",
            "professionalTitle": "professional_title",
            
            "Email Address": "email_address",
            "email_address": "email_address",
            "emailAddress": "email_address",
            
            "Location": "location",
            "location": "location",
            
            "Portfolio / LinkedIn URL": "portfolio_url",
            "portfolio_url": "portfolio_url",
            "portfolioUrl": "portfolio_url",
            
            "Professional Summary": "professional_summary",
            "professional_summary": "professional_summary",
            "professionalSummary": "professional_summary",
        }

        if personal is not None:
            # If personal details was provided, copy its fields
            for display_key, model_key in field_map.items():
                if display_key in personal:
                    new_data[model_key] = personal[display_key]

        # Map nested lists in any of the common key formats to the serializer field names
        experience_keys = ["Experience", "experience", "experiences"]
        for k in experience_keys:
            if k in data:
                new_data['Experience'] = data[k]
                break

        education_keys = ["Education", "education", "education_history", "educationHistory"]
        for k in education_keys:
            if k in data:
                new_data['Education'] = data[k]
                break

        skills_keys = ["Skills", "skills"]
        for k in skills_keys:
            if k in data:
                new_data['Skills'] = data[k]
                break

        return super().to_internal_value(new_data)

    def create(self, validated_data):
        # التعامل مع الـ Nested Write يدوياً
        experiences_data = validated_data.pop('experiences', [])
        education_data = validated_data.pop('education_history', [])
        skills_data = validated_data.pop('skills', [])
        
        cv = CV.objects.create(**validated_data)
        
        # حفظ الخبرات
        for exp in experiences_data:
            CVExperience.objects.create(cv=cv, **exp)
            
        # حفظ التعليم
        for edu in education_data:
            CVEducation.objects.create(cv=cv, **edu)
            
        # حفظ المهارات
        if skills_data:
            cv.skills.set(skills_data)
            
        return cv

    def update(self, instance, validated_data):
        experiences_data = validated_data.pop('experiences', None)
        education_data = validated_data.pop('education_history', None)
        skills_data = validated_data.pop('skills', None)
        
        # Update CV flat fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Replace experiences if provided in the payload
        if experiences_data is not None:
            instance.experiences.all().delete()
            for exp in experiences_data:
                CVExperience.objects.create(cv=instance, **exp)
                
        # Replace education if provided in the payload
        if education_data is not None:
            instance.education_history.all().delete()
            for edu in education_data:
                CVEducation.objects.create(cv=instance, **edu)
                
        # Replace skills if provided in the payload
        if skills_data is not None:
            instance.skills.set(skills_data)
            
        return instance

class ProfileCVBuildSerializer(serializers.Serializer):
    user_data = serializers.CharField(
        help_text="Profile data text to send to the external CV profile API"
    )

    class Meta:
        fields = ['user_data']

class ProposalSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = Proposal
        fields = ['id', 'user', 'job', 'project', 'content', 'status', 'created_at', 'job_details', 'project_details']
        read_only_fields = ['user', 'created_at']
