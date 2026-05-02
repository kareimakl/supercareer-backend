from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from opportunities.models import Job
from .models import CV, Proposal
from .serializers import CVSerializer, ProposalSerializer

class CVListView(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CV.objects.filter(user=self.request.user)\
            .prefetch_related('experiences', 'education_history', 'skills')

class BaseCVCreateView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Base CV is stored without linking to any job
        serializer.save(user=self.request.user, is_base=True, job=None)

class JobLinkedCVCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        base_cv = CV.objects.filter(user=request.user, is_base=True).last()
        
        if not base_cv:
            return Response({"error": "No base CV found for this user."}, status=400)
            
        # Placeholder for external API call logic.
        # This endpoint links the CV to a job and will take modified cv data from the AI API.
        
        new_cv = CV.objects.create(
            user=request.user,
            job=job,
            is_base=False,
            full_name=base_cv.full_name,
            phone_number=base_cv.phone_number,
            professional_title=base_cv.professional_title,
            email_address=base_cv.email_address,
            location=base_cv.location,
            portfolio_url=base_cv.portfolio_url,
            professional_summary=base_cv.professional_summary,
            content=base_cv.content
        )
        
        serializer = CVSerializer(new_cv)
        return Response(serializer.data, status=201)

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
