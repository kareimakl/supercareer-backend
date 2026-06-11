from django.urls import path
from .views import ProposalGeneratorView

urlpatterns = [
    path('generate-proposal/', ProposalGeneratorView.as_view(), name='generate-proposal'),
]

