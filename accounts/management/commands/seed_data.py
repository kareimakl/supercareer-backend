import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, UserProfile, Skill
from opportunities.models import Job, FreelanceProject
from documents.models import CV, Proposal
from matching.models import MatchResult

class Command(BaseCommand):
    help = 'Seed the database with initial demonstration data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning up old data...')
        MatchResult.objects.all().delete()
        CV.objects.all().delete()
        
        self.stdout.write('Seeding data...')

        # 1. Create Skills
        skill_names = [
            'Python', 'Django', 'React', 'Vue.js', 'TypeScript', 'Node.js', 
            'AI', 'Machine Learning', 'Natural Language Processing', 
            'Figma', 'UI/UX Design', 'Tailwind CSS', 'PostgreSQL', 'Docker',
            'AWS', 'DevOps', 'Mobile Development', 'Flutter', 'Swift'
        ]
        skills = []
        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills.append(skill)
        self.stdout.write(f'Created {len(skills)} skills.')

        # 2. Create Users
        users_data = [
            {
                'email': 'omar@example.com',
                'username': 'omar_dev',
                'first_name': 'Omar',
                'last_name': 'Elders',
                'role': 'job_seeker',
                'bio': 'Senior Full Stack Developer specializing in AI and React.',
                'specialization': 'Full Stack | AI Specialist',
                'experience': '5+ years of experience in building scalable web applications.',
                'user_skills': ['Python', 'Django', 'React', 'AI', 'PostgreSQL']
            },
            {
                'email': 'layla@example.com',
                'username': 'layla_design',
                'first_name': 'Layla',
                'last_name': 'Hassan',
                'role': 'freelancer',
                'bio': 'Creative UI/UX Designer with a passion for clean and modern interfaces.',
                'specialization': 'UI/UX Design',
                'experience': '3 years of experience in product design using Figma and Adobe CC.',
                'user_skills': ['Figma', 'UI/UX Design', 'Tailwind CSS']
            }
        ]

        created_users = []
        for u_data in users_data:
            # Try to find existing user by email or username
            user = User.objects.filter(email=u_data['email']).first()
            if not user:
                user = User.objects.filter(username=u_data['username']).first()
            
            if not user:
                user = User.objects.create_user(
                    email=u_data['email'],
                    username=u_data['username'],
                    first_name=u_data['first_name'],
                    last_name=u_data['last_name'],
                    role=u_data['role']
                )
                user.set_password('password123')
                user.save()
            
            # Update Profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.full_name = f"{u_data['first_name']} {u_data['last_name']}"
            profile.phone_number = "+1 (555) 000-0000"
            profile.professional_title = u_data['specialization']
            profile.location = "San Francisco, CA"
            profile.portfolio_url = "https://linkedin.com/in/example"
            profile.bio = u_data['bio']
            profile.specialization = u_data['specialization']
            profile.experience = u_data['experience'] # Keeping for legacy
            profile.hourly_rate = random.randint(30, 100)
            
            # Add user skills
            user_skills = Skill.objects.filter(name__in=u_data['user_skills'])
            profile.skills.set(user_skills)
            profile.save()
            
            from accounts.models import WorkExperience, Education
            # Add Experience for Omar
            if u_data['email'] == 'omar@example.com':
                WorkExperience.objects.get_or_create(
                    profile=profile,
                    job_title="Senior Full Stack Developer",
                    company="TechFlow Inc.",
                    defaults={
                        'start_date': "March 2021",
                        'end_date': "Present",
                        'is_current': True,
                        'description': "Led the redesign of the flagship mobile application."
                    }
                )
                Education.objects.get_or_create(
                    profile=profile,
                    school="University of Computer Science",
                    degree="B.S. Software Engineering",
                    defaults={
                        'graduation_year': "2018",
                        'description': "Graduated with honors."
                    }
                )

            created_users.append(user)
        
        self.stdout.write(f'Created/Updated {len(created_users)} users.')

        # 3. Create Jobs
        jobs_data = [
            {
                'title': 'Lead AI Engineer',
                'company': 'TechNova Solutions',
                'description': 'We are looking for a Lead AI Engineer to drive our machine learning initiatives. Experience with LLMs and vector databases is a must.',
                'location': 'Remote',
                'source_platform': 'LinkedIn',
                'source_url': 'https://linkedin.com/jobs/1',
                'required_skills': ['Python', 'AI', 'Machine Learning']
            },
            {
                'title': 'Senior Frontend Developer (React)',
                'company': 'CloudStream',
                'description': 'Join our frontend team to build cutting-edge web interfaces. Mastery of React and Tailwind CSS is required.',
                'location': 'Hybrid - Cairo',
                'source_platform': 'Wuzzuf',
                'source_url': 'https://wuzzuf.net/jobs/2',
                'required_skills': ['React', 'Tailwind CSS', 'TypeScript']
            },
            {
                'title': 'Backend Developer (Django)',
                'company': 'FinGo Tech',
                'description': 'Build secure and scalable APIs for our fintech platform using Python and Django.',
                'location': 'Remote',
                'source_platform': 'Indeed',
                'source_url': 'https://indeed.com/jobs/3',
                'required_skills': ['Python', 'Django', 'PostgreSQL']
            }
        ]

        created_jobs = []
        for j_data in jobs_data:
            job, _ = Job.objects.get_or_create(
                title=j_data['title'],
                company=j_data['company'],
                defaults={
                    'description': j_data['description'],
                    'location': j_data['location'],
                    'source_platform': j_data['source_platform'],
                    'source_url': j_data['source_url'],
                    'posted_date': timezone.now().date() - timedelta(days=random.randint(0, 10))
                }
            )
            # Add job skills
            job_skills = Skill.objects.filter(name__in=j_data.get('required_skills', []))
            job.required_skills.set(job_skills)
            created_jobs.append(job)
        self.stdout.write(f'Created {len(created_jobs)} jobs.')

        # 4. Create Freelance Projects
        projects_data = [
            {
                'title': 'Build a Custom E-commerce Flutter App',
                'description': 'Build a high-performance Flutter app for an online boutique. Integration with Stripe and Firebase.',
                'budget': '$2,500',
                'platform_name': 'Upwork',
                'required_skills': ['Mobile Development', 'Flutter']
            },
            {
                'title': 'AI Chatbot Integration for Website',
                'description': 'Integrate an OpenAI-based chatbot into our customer support portal.',
                'budget': '$800',
                'platform_name': 'Freelancer.com',
                'required_skills': ['Python', 'AI', 'Natural Language Processing']
            },
            {
                'title': 'UI Refresh for Dashboard',
                'description': 'Redesign the existing admin dashboard for better usability and modern look.',
                'budget': '$1,500',
                'platform_name': 'Toptal',
                'required_skills': ['Figma', 'UI/UX Design']
            }
        ]

        created_projects = []
        for p_data in projects_data:
            project, _ = FreelanceProject.objects.get_or_create(
                title=p_data['title'],
                platform_name=p_data['platform_name'],
                defaults={
                    'description': p_data['description'],
                    'budget': p_data['budget'],
                    'deadline': timezone.now().date() + timedelta(days=30),
                    'status': 'open',
                    'source_url': 'https://freelance.com/project/1',
                    'posted_date': timezone.now()
                }
            )
            # Add project skills
            project_skills = Skill.objects.filter(name__in=p_data['required_skills'])
            project.required_skills.set(project_skills)
            created_projects.append(project)
        self.stdout.write(f'Created {len(created_projects)} projects.')

        # 5. Create Documents (CVs and Proposals)
        omar = created_users[0]
        layla = created_users[1]

        # Multiple CVs for Omar
        cv_contents = [
            'Senior AI Engineer with expert knowledge in Python, Django, and NLP.',
            'Backend Specialist focused on high-concurrency Node.js and PostgreSQL systems.',
            'Technical Lead with 8 years experience in React and AWS cloud architecture.'
        ]
        for i, content in enumerate(cv_contents):
            cv, _ = CV.objects.get_or_create(
                user=omar,
                job=created_jobs[i % len(created_jobs)],
                defaults={
                    'full_name': 'Omar Elders',
                    'phone_number': '+1 (555) 123-4567',
                    'professional_title': 'Senior Full Stack Developer',
                    'email_address': 'omar@example.com',
                    'location': 'Remote / Cairo',
                    'portfolio_url': 'https://github.com/omar-dev',
                    'professional_summary': content,
                    'content': content, # legacy
                    'ats_score': random.uniform(75, 98)
                }
            )
            # Add Experience to CV
            from documents.models import CVExperience, CVEducation
            CVExperience.objects.get_or_create(
                cv=cv,
                job_title="Senior Developer",
                company="AI Solutions",
                defaults={
                    'start_date': "Jan 2020",
                    'end_date': "Dec 2023",
                    'is_current': False,
                    'description': "Worked on core AI features."
                }
            )
            # Add Education to CV
            CVEducation.objects.get_or_create(
                cv=cv,
                school="Cairo University",
                degree="Computer Science",
                defaults={
                    'graduation_year': "2018",
                    'description': "GPA 3.9"
                }
            )
            # Skills
            cv_skills = Skill.objects.filter(name__in=['Python', 'Django', 'React'])
            cv.skills.set(cv_skills)

        # CV for Layla
        cv_layla, _ = CV.objects.get_or_create(
            user=layla,
            job=created_jobs[1], # Senior Frontend
            defaults={
                'full_name': 'Layla Hassan',
                'phone_number': '+1 (555) 987-6543',
                'professional_title': 'UI/UX Designer',
                'email_address': 'layla@example.com',
                'location': 'Dubai',
                'portfolio_url': 'https://behance.net/layla',
                'professional_summary': 'UX/UI focused Frontend Developer with experience in design systems.',
                'content': 'UX/UI focused Frontend Developer with experience in design systems.',
                'ats_score': 88.0
            }
        )
        CVExperience.objects.get_or_create(
            cv=cv_layla,
            job_title="Junior Designer",
            company="Design Hub",
            defaults={
                'start_date': "Feb 2021",
                'end_date': "Present",
                'is_current': True,
                'description': "Created high-fidelity mockups."
            }
        )

        # Proposal for Layla
        Proposal.objects.get_or_create(
            user=layla,
            project=created_projects[2], # UI Refresh
            defaults={
                'content': 'I am a UI/UX specialist and can help you refresh your dashboard in Figma.',
                'status': 'sent'
            }
        )
        self.stdout.write('Created documents.')

        # 6. Create Match Results (Populating with realistic data)
        # Create Job matches for Omar
        MatchResult.objects.get_or_create(
            user=omar,
            job=created_jobs[0], # Lead AI
            defaults={
                'match_score': 98.5,
                'matched_skills': ['Python', 'AI'],
                'missing_skills': ['Vector Databases'],
                'ai_tips': 'Impressive profile. Highlighting your experience with ChromaDB would secure this role.'
            }
        )

        MatchResult.objects.get_or_create(
            user=omar,
            job=created_jobs[2], # Backend Dev
            defaults={
                'match_score': 82.0,
                'matched_skills': ['Python', 'Django', 'PostgreSQL'],
                'missing_skills': ['Docker', 'AWS'],
                'ai_tips': 'You have the core skills. Adding containerization experience will make you a top candidate.'
            }
        )

        # Create Project matches for Omar
        MatchResult.objects.get_or_create(
            user=omar,
            project=created_projects[1], # AI Chatbot
            defaults={
                'match_score': 91.0,
                'matched_skills': ['AI', 'Python'],
                'missing_skills': ['NLP'],
                'ai_tips': 'Perfect match for your background in AI.'
            }
        )

        # Match Layla with Job
        MatchResult.objects.get_or_create(
            user=layla,
            job=created_jobs[1], # Senior Frontend
            defaults={
                'match_score': 85.0,
                'matched_skills': ['Figma', 'UI/UX Design'],
                'missing_skills': ['React'],
                'ai_tips': 'Focus on bridge between design and code.'
            }
        )

        # Match Layla with Projects
        for i, project in enumerate(created_projects):
            MatchResult.objects.get_or_create(
                user=layla,
                project=project,
                defaults={
                    'match_score': random.uniform(60, 95),
                    'matched_skills': ['Figma'] if i == 2 else [],
                    'missing_skills': ['Flutter'] if i == 0 else [],
                    'ai_tips': 'Keep refining your portfolio.'
                }
            )
        self.stdout.write('Created match results.')

        self.stdout.write(self.style.SUCCESS('Successfully seeded development data!'))
