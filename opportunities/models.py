from django.db import models


class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    source_platform = models.CharField(max_length=255)
    source_url = models.URLField()

    posted_date = models.DateField()
    required_skills = models.ManyToManyField('accounts.Skill', blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FreelanceProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    budget = models.CharField(max_length=255, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    
    required_skills = models.ManyToManyField('accounts.Skill', blank=True)

    platform_name = models.CharField(max_length=255)
    source_url = models.URLField(max_length=2000)

    posted_date = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title