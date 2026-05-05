from django.urls import path
from .views import (
    CVListView, 
    BaseCVCreateView, 
    BaseCVUpdateView,
    JobLinkedCVCreateView, 
    ProfileCVBuildView, 
    ProposalHistoryView, 
    ProposalDetailView
)

urlpatterns = [
    path('cv/', CVListView.as_view(), name='cv-list'),
    path('cv/base/', BaseCVCreateView.as_view(), name='cv-base-create'),
    path('cv/base/update/', BaseCVUpdateView.as_view(), name='cv-base-update'),
    path('cv/job/<int:job_id>/', JobLinkedCVCreateView.as_view(), name='cv-job-linked-create'),
    path('cv/profile/', ProfileCVBuildView.as_view(), name='cv-profile-build'),
    path('proposals/', ProposalHistoryView.as_view(), name='proposal-history'),
    path('proposals/<int:pk>/', ProposalDetailView.as_view(), name='proposal-detail'),
]
