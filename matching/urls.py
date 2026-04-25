# from django.urls import path
# from .views import UserMatchView # غيرنا الاسم هنا لـ UserMatchView

# urlpatterns = [
#     path('', UserMatchView.as_view(), name='user-matches'),
# ]
from django.urls import path
from .views import JobMatchView, ProjectMatchView,ProposalGeneratorView

urlpatterns = [
    path('jobs/', JobMatchView.as_view(), name='job-matches'),
    path('projects/', ProjectMatchView.as_view(), name='project-matches'),
    path('generate-proposal/', ProposalGeneratorView.as_view(), name='generate-proposal'),
]