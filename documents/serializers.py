from rest_framework import serializers
from .models import CV, Proposal, CVExperience, CVEducation
from accounts.models import Skill
from opportunities.serializers import JobSerializer, ProjectSerializer

class CVExperienceSerializer(serializers.ModelSerializer):
    # استخدام التسميات اللي اليوزر طلبها في الـ request والـ response
    is_current = serializers.BooleanField(label="I currently work here")
    job_title = serializers.CharField(label="Job Title")
    company = serializers.CharField(label="Company")
    start_date = serializers.CharField(label="Start Date")
    end_date = serializers.CharField(required=False, allow_null=True, label="End Date")
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
    Skills = serializers.SlugRelatedField(many=True, source='skills', slug_field='name', queryset=Skill.objects.all(), required=False)
    
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
        # تحويل الـ Request المتداخل لـ Flat fields عشان الموديل يفهمها
        personal = data.get("Personal Details", data)
        
        # بننقل البيانات من الـ Nested Dictionary للـ Flat Map
        new_data = data.copy()
        new_data['full_name'] = personal.get("Full Name", personal.get("full_name", ""))
        new_data['phone_number'] = personal.get("Phone Number", personal.get("phone_number", ""))
        new_data['professional_title'] = personal.get("Professional Title", personal.get("professional_title", ""))
        new_data['email_address'] = personal.get("Email Address", personal.get("email_address", ""))
        new_data['location'] = personal.get("Location", personal.get("location", ""))
        new_data['portfolio_url'] = personal.get("Portfolio / LinkedIn URL", personal.get("portfolio_url", ""))
        new_data['professional_summary'] = personal.get("Professional Summary", personal.get("professional_summary", ""))
        
        # بنظبط الـ Experience و الـ Education لو موجودين
        if "Experience" in data:
            new_data['experiences'] = data.get("Experience")
        if "Education" in data:
            new_data['education_history'] = data.get("Education")
        if "Skills" in data:
            new_data['skills'] = data.get("Skills")
            
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
