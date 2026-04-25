from django.contrib import admin
# استورد الجداول الخاصة بالـ opportunities من الملف الحالي
from .models import Job, FreelanceProject 

# استورد الجداول الخاصة بالـ accounts من مكانها الصح
from accounts.models import User, UserProfile, Skill 

# تسجيل الجداول في الأدمن
admin.site.register(Job)
admin.site.register(FreelanceProject)