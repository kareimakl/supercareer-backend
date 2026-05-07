from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from opportunities.models import Job
from .models import CV, Proposal, ProfileCVBuild
from .serializers import CVSerializer, ProposalSerializer, ProfileCVBuildSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample

import json
import requests

CV_EXAMPLE = OpenApiExample(
    "Custom CV Schema",
    description="The expected JSON structure with custom labels.",
    value={
        "Personal Details": {
            "Full Name": "string",
            "Phone Number": "string",
            "Professional Title": "string",
            "Email Address": "user@example.com",
            "Location": "string",
            "Portfolio / LinkedIn URL": "https://example.com",
            "Professional Summary": "string"
        },
        "Experience": [
            {
                "I currently work here": True,
                "Job Title": "string",
                "Company": "string",
                "Start Date": "string",
                "End Date": "string",
                "Description": "string"
            }
        ],
        "Education": [
            {
                "School / University": "string",
                "Degree / Qualification": "string",
                "Year of Graduation": "string",
                "Additional Details": "string"
            }
        ],
        "Skills": [
            "string"
        ]
    }
    # Removed request_only=True so the example is shown for responses as well
)

class CVListView(generics.ListCreateAPIView):
    """List all CVs for the user, or create a new regular (non-base) CV."""
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CV.objects.filter(user=self.request.user)\
            .prefetch_related('experiences', 'education_history', 'skills')

    @extend_schema(request=CVSerializer, responses={201: CVSerializer}, examples=[CV_EXAMPLE])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Create a regular CV (is_base=False) linked to the user
        # Note: 'job' can be passed in validated_data if allowed by serializer, otherwise it will be None
        serializer.save(user=self.request.user, is_base=False)

class CVDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific CV by ID. Only allows access to the user's own CVs."""
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CV.objects.filter(user=self.request.user)\
            .prefetch_related('experiences', 'education_history', 'skills')

    @extend_schema(request=CVSerializer, responses={200: CVSerializer}, examples=[CV_EXAMPLE])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(request=CVSerializer, responses={200: CVSerializer}, examples=[CV_EXAMPLE])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class BaseCVCreateView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CVSerializer, responses={201: CVSerializer}, examples=[CV_EXAMPLE])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Prevent creating more than one base CV per user
        if CV.objects.filter(user=request.user, is_base=True).exists():
            return Response({"error": "Base CV already exists for this user. Use the update endpoint to modify it."}, status=400)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Base CV is stored without linking to any job
        serializer.save(user=self.request.user, is_base=True, job=None)


class BaseCVUpdateView(generics.RetrieveUpdateAPIView):
    """Allow the user to retrieve and update their existing base CV."""
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CVSerializer, responses={200: CVSerializer}, examples=[CV_EXAMPLE])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(request=CVSerializer, responses={200: CVSerializer}, examples=[CV_EXAMPLE])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        # Return the single base CV for the authenticated user or 404
        return get_object_or_404(CV, user=self.request.user, is_base=True)

    def get_queryset(self):
        return CV.objects.filter(user=self.request.user, is_base=True)

class JobLinkedCVCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        base_cv = CV.objects.filter(user=request.user, is_base=True).last()
        
        if not base_cv:
            return Response({"error": "No base CV found for this user."}, status=400)
            
        # Get base CV serialized data
        base_cv_data = CVSerializer(base_cv).data
        
        # We need to filter out read-only / system fields so the payload conforms strictly to CVSchema
        # According to the AI API, CVSchema expects Personal Details, Experience, Education, Skills
        cv_payload = {
            "Personal Details": base_cv_data.get("Personal Details", {}),
            "Experience": base_cv_data.get("Experience", []),
            "Education": base_cv_data.get("Education", []),
            "Skills": base_cv_data.get("Skills", [])
        }
        
        target_job_text = f"Title: {job.title}\nCompany: {job.company}\nDescription: {job.description}"
        payload = {
            "target_job": target_job_text,
            "base_cv": cv_payload
        }
        
        try:
            # Call the AI API
            api_url = "https://resume-analyzer-ni4g.onrender.com/API/CV/Build/Job_cv"
            ai_response = requests.post(api_url, json=payload, timeout=60)
            ai_response.raise_for_status()

            ai_data = ai_response.json()
            optimized_cv_data = ai_data.get("optimized_cv")

            if not optimized_cv_data:
                return Response({"error": "Invalid response from AI API: 'optimized_cv' missing"}, status=502)
                
            # Create the modified CV using our serializer
            serializer = CVSerializer(data=optimized_cv_data)
            if serializer.is_valid():
                serializer.save(user=request.user, job=job, is_base=False)
                return Response(serializer.data, status=201)
            else:
                return Response({"error": "AI response validation failed", "details": serializer.errors}, status=400)
                
        except requests.RequestException as e:
            return Response({"error": "Failed to connect to AI API", "details": str(e)}, status=502)

class ProfileCVBuildView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCVBuildSerializer

    @extend_schema(request=ProfileCVBuildSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            payload = serializer.validated_data['user_data']

            # Convert payload to the format expected by external API
            external_payload = {"user_data": payload}

            api_url = "https://resume-analyzer-ni4g.onrender.com/API/CV/Build/Profile_cv"
            external_response = requests.post(api_url, json=external_payload, timeout=60)
            external_response.raise_for_status()
            response_data = external_response.json()
        except requests.RequestException as e:
            return Response({"error": "Failed to connect to external CV API", "details": str(e)}, status=502)
        except Exception as e:
            # Log unexpected errors and return a generic 500 response
            import traceback, logging
            logging.error("Unexpected error in ProfileCVBuildView: %s", traceback.format_exc())
            return Response({"error": "Internal server error", "details": str(e)}, status=500)

        # Save the build request/response
        profile_build = ProfileCVBuild.objects.create(
            user=request.user,
            request_payload=external_payload,
            response_payload=response_data,
        )

        return Response({
            "id": profile_build.id,
            "request_payload": profile_build.request_payload,
            "response_payload": profile_build.response_payload,
        }, status=201)


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
