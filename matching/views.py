from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ProposalRequestSerializer
from .match import generate_ai_proposal
from opportunities.models import FreelanceProject
from documents.models import Proposal
from drf_spectacular.utils import extend_schema

# 3. API لتوليد مقترح (Proposal)
class ProposalGeneratorView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProposalRequestSerializer,
        responses={200: {"type": "object", "properties": {"proposal": {"type": "string"}, "proposal_id": {"type": "integer"}}}}
    )
    def post(self, request):
        user = request.user
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({"error": "project_id is required"}, status=400)

        try:
            project = FreelanceProject.objects.get(id=project_id)
        except FreelanceProject.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        if not hasattr(user, 'profile'):
            return Response({"error": "Please complete your profile first (UserProfile missing)"}, status=400)

        profile_data = {
            "skills": [s.name for s in user.profile.skills.all()],
            "bio": getattr(user.profile, 'bio', '') or '',
            "full_name": getattr(user.profile, 'full_name', '') or ''
        }

        proposal_text = generate_ai_proposal(profile_data, project.description)

        # Save the generated proposal to the database
        proposal = Proposal.objects.create(
            user=user,
            project=project,
            content=proposal_text,
            status='sent'
        )

        return Response({"proposal": proposal_text, "proposal_id": proposal.id})


