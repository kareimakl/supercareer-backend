from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CV, Proposal
from .serializers import CVSerializer, ProposalSerializer

class CVListView(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CV.objects.filter(user=self.request.user)\
            .prefetch_related('experiences', 'education_history', 'skills')

class CVCreateView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProposalHistoryView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(user=self.request.user)\
            .select_related('job', 'project')\
            .prefetch_related('job__required_skills', 'project__required_skills')\
            .order_by('-created_at')

class ProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(user=self.request.user)\
            .select_related('job', 'project')
