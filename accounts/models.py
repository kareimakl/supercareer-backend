from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('freelancer', 'Freelancer'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_blocked = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    professional_title = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    portfolio_url = models.URLField(max_length=500, blank=True, default='')
    
    skills = models.ManyToManyField(Skill, blank=True, related_name="user_profiles")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    specialization = models.TextField(blank=True, default='')
    experience = models.TextField(blank=True, default='') # Legacy field
    bio = models.TextField(blank=True, default='')
    education = models.TextField(blank=True, default='') # Legacy field
    preferences = models.TextField(blank=True, default='')
    profile_views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} Profile"

class WorkExperience(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='experiences', on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Education(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='education_history', on_delete=models.CASCADE)
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    graduation_year = models.CharField(max_length=20)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.degree} from {self.school}"







