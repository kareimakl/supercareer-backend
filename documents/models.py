from django.db import models
from accounts.models import User
from opportunities.models import Job, FreelanceProject


class CV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    # Personal Details
    full_name = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    professional_title = models.CharField(max_length=255, blank=True, default='')
    email_address = models.EmailField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    portfolio_url = models.URLField(max_length=500, blank=True, default='')
    professional_summary = models.TextField(blank=True, default='')

    # Legacy field
    content = models.TextField(blank=True, default='')
    ats_score = models.FloatField(default=0.0)
    
    is_base = models.BooleanField(default=False)

    skills = models.ManyToManyField('accounts.Skill', blank=True, related_name='cvs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CV - {self.full_name or self.user.username}"

class CVExperience(models.Model):
    cv = models.ForeignKey(CV, related_name='experiences', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=False)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class CVEducation(models.Model):
    cv = models.ForeignKey(CV, related_name='education_history', on_delete=models.CASCADE)
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    graduation_year = models.CharField(max_length=20)
    description = models.TextField(blank=True, default='') # maps to "Additional Details"

    def __str__(self):
        return f"{self.degree} from {self.school}"


class Proposal(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('archived', 'Archived'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(FreelanceProject, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Proposal"
        