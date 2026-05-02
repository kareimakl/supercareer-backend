import re
import sys
from django.core.management.base import BaseCommand
from opportunities.models import Job, FreelanceProject
from accounts.models import Skill
from django.db import transaction

class Command(BaseCommand):
    help = 'Cleanup duplicate jobs/projects and extract skills from descriptions'

    def handle(self, *args, **kwargs):
        self.extract_skills(Job)
        self.extract_skills(FreelanceProject)

    def extract_skills(self, model):
        # Process ALL records to ensure we catch everything
        objs = model.objects.all()
        total = objs.count()
        self.stdout.write(f'--- Extracting skills for {model.__name__} ({total} to process) ---')
        
        # Pre-fetch existing skills for faster matching
        all_skills = {s.name.lower(): s for s in Skill.objects.all()}
        
        updated_count = 0
        for i, obj in enumerate(objs):
            if i % 100 == 0:
                self.stdout.write(f"  {model.__name__} Progress: {i}/{total}...")
                sys.stdout.flush()
                
            description = obj.description
            if not description:
                continue
                
            found_skills = []
            
            # Step 1: Match against existing skills (Keyword matching)
            for skill_name, skill_obj in all_skills.items():
                # Avoid very short skills like 'AI' matching inside words
                if len(skill_name) <= 3:
                    pattern = rf'\b{re.escape(skill_name)}\b'
                else:
                    pattern = re.escape(skill_name)
                    
                if re.search(pattern, description, re.IGNORECASE):
                    found_skills.append(skill_obj)
            
            # Step 2: Discover skills from separators (dot, pipe, dash, bullets)
            # We look for the common Wuzzuf/LinkedIn separators
            # \xb7 = mid-dot, \u2022 = bullet, \u25cf = black circle
            parts = re.split(r'\s*[·|\-\u00b7\u2022\u25cf]\s*', description)
            
            if len(parts) > 2:
                for part in parts:
                    skill_name = part.strip()
                    # Filters: length between 3 and 40, no common job metadata
                    if not skill_name or len(skill_name) < 3 or len(skill_name) > 40:
                        continue
                    
                    # Skip common job metadata found in Wuzzuf descriptions
                    lower_name = skill_name.lower()
                    skip_keywords = [
                        'level', 'exp', 'time', 'yrs', 'job', 'egypt', 'cairo',
                        'dubai', 'remote', 'hybrid', 'on-site', 'ago', 'hour',
                        'day', 'week', 'month', 'salary', 'negotiable', 'male', 'female'
                    ]
                    if any(kw in lower_name for kw in skip_keywords):
                        continue
                    
                    # If it looks like a skill, use it
                    if lower_name in all_skills:
                        found_skills.append(all_skills[lower_name])
                    else:
                        # Create new skill
                        new_skill, _ = Skill.objects.get_or_create(name=skill_name[:100])
                        all_skills[lower_name] = new_skill
                        found_skills.append(new_skill)
            
            if found_skills:
                # Deduplicate and add
                with transaction.atomic():
                    obj.required_skills.add(*list(set(found_skills)))
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Updated skills for {updated_count} {model.__name__} records.'))
