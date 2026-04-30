from django.db import models
from accounts.models import User
from opportunities.models import Job, FreelanceProject

class MatchResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches")
    job = models.ForeignKey(Job, null=True, blank=True, on_delete=models.CASCADE)
    project = models.ForeignKey(FreelanceProject, null=True, blank=True, on_delete=models.CASCADE)
    
    match_score = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    ai_tips = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # التعديل هنا: الترتيب بالأعلى سكور أولاً، وإذا تساوى السكور، الأحدث (created_at) يظهر أولاً
        ordering = ['-match_score', '-created_at']

    def __str__(self):
        # تأكدنا من التعامل مع الـ null في العنوان عشان ميرميش Error
        target = "Unknown"
        if self.job:
            target = self.job.title
        elif self.project:
            target = self.project.title
            
        return f"{self.user.email} - {target} ({self.match_score}%)"