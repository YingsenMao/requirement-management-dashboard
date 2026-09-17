import os
import mimetypes
from urllib.parse import quote
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import F, Case, When, Value, IntegerField
from django.http import FileResponse, Http404
from django.conf import settings
from .models import RequirementRequest, Attachment, CustomUser, ReviewSession, ReviewMessage
from .serializers import RequirementRequestSerializer, AdminRequirementSerializer, UserCreateSerializer, ReviewSessionSerializer, ReviewSessionCreateSerializer, ReviewMessageSerializer
from .permissions import IsOwnerAndPendingReview, IsAdminUser
from .services.ai_review import AiReviewClient
from rest_framework.throttling import UserRateThrottle

class UserRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for regular users to view all requirements, 
    but only manage their own requirement requests.
    """
    serializer_class = RequirementRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerAndPendingReview]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None

    def get_queryset(self):
        return RequirementRequest.objects.select_related('submitter').prefetch_related('attachments').annotate(
            is_completed=Case(
                When(status='completed', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_completed', F('priority_score').desc(nulls_last=True), '-submission_date')

    def perform_create(self, serializer):
        serializer.save(submitter=self.request.user)

    def perform_update(self, serializer):
        if self.get_object().status == 'rejected':
            serializer.save(status='pending_review', reject_reason=None)
        else:
            serializer.save()

class AdminRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admins to view and manage requirement requests
    scoped to their own department (IT admins see IT requests only,
    R&D admins see R&D requests only).
    """
    serializer_class = AdminRequirementSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None

    def get_queryset(self):
        department = getattr(self.request.user, 'department', None)
        if not department:
            return RequirementRequest.objects.none()
        return RequirementRequest.objects.filter(owning_department=department).select_related('submitter').prefetch_related('attachments').annotate(
            is_completed=Case(
                When(status='completed', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_completed', F('priority_score').desc(nulls_last=True), '-submission_date')


class UserListView(APIView):
    """
    Returns a list of all regular users (for the Submitter filter).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.filter(role='user').values('id', 'username')
        return Response(list(users))


class UserCreateView(APIView):
    """
    Admin-only endpoint to create accounts (create-account only).
    Regular User accounts have no department; Admin accounts require one.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'department': user.department,
            },
            status=201
        )


class AIReviewThrottle(UserRateThrottle):
    scope = 'ai_review'


class ReviewSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIReviewThrottle]

    def post(self, request):
        if not getattr(settings, 'DASHSCOPE_API_KEY', None):
            return Response({"detail": "AI review service not configured"}, status=503)

        serializer = ReviewSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mode = serializer.validated_data['mode']
        requirement_id = serializer.validated_data.get('requirement_id')
        form_context = serializer.validated_data['form_context']

        if mode == 'edit':
            try:
                requirement = RequirementRequest.objects.get(id=requirement_id)
            except RequirementRequest.DoesNotExist:
                return Response({"detail": "Requirement not found"}, status=404)
            if requirement.submitter != request.user:
                return Response({"detail": "You do not own this requirement"}, status=403)
            if requirement.status not in ['pending_review', 'rejected']:
                return Response({"detail": "Requirement is locked"}, status=400)
        else:
            requirement = None

        active_sessions = ReviewSession.objects.filter(user=request.user, status__in=['asking', 'generated']).count()
        if active_sessions >= 3:
            return Response({"detail": "Maximum 3 active review sessions allowed"}, status=400)

        session = ReviewSession.objects.create(
            user=request.user,
            requirement=requirement,
            mode=mode,
            status='asking',
            form_context=form_context
        )

        try:
            client = AiReviewClient()
            messages = [
                {"role": "user", "content": f"Here is my requirement:\n\nName: {form_context.get('name')}\n\nDescription: {form_context.get('summary')}"}
            ]
            result = client.chat(messages, question_count=0)

            if not result.get('finished'):
                question = result.get('question', 'Please tell me more about your requirement.')
                ReviewMessage.objects.create(session=session, role='ai', content=question)
                return Response({
                    'session_id': session.id,
                    'question': question,
                    'finished': False
                }, status=201)
            else:
                session.status = 'generated'
                session.generated_description = result.get('description_html', '')
                session.generated_acceptance = result.get('acceptance_criteria_html', '')
                session.save()
                ReviewMessage.objects.create(session=session, role='ai', content=f"[Generated result]\nDescription: {result.get('description_html', '')}\nAcceptance Criteria: {result.get('acceptance_criteria_html', '')}")
                return Response({
                    'session_id': session.id,
                    'finished': True,
                    'description_html': result.get('description_html', ''),
                    'acceptance_criteria_html': result.get('acceptance_criteria_html', '')
                }, status=201)
        except Exception as e:
            session.delete()
            return Response({"detail": f"AI service error: {str(e)}"}, status=500)


class ReviewMessageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIReviewThrottle]

    def post(self, request, session_id):
        if not getattr(settings, 'DASHSCOPE_API_KEY', None):
            return Response({"detail": "AI review service not configured"}, status=503)

        try:
            session = ReviewSession.objects.get(id=session_id, user=request.user)
        except ReviewSession.DoesNotExist:
            return Response({"detail": "Session not found"}, status=404)

        if session.status != 'asking':
            return Response({"detail": "Session is not in asking state"}, status=400)

        serializer = ReviewMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.validated_data['answer']

        ReviewMessage.objects.create(session=session, role='user', content=answer)

        messages_qs = ReviewMessage.objects.filter(session=session).order_by('created_at')
        messages = [{"role": m.role, "content": m.content} for m in messages_qs]

        question_count = messages_qs.filter(role='ai').count()

        try:
            client = AiReviewClient()
            result = client.chat(messages, question_count=question_count)

            if not result.get('finished'):
                question = result.get('question', 'Please tell me more.')
                ReviewMessage.objects.create(session=session, role='ai', content=question)
                return Response({
                    'finished': False,
                    'question': question
                })
            else:
                session.status = 'generated'
                session.generated_description = result.get('description_html', '')
                session.generated_acceptance = result.get('acceptance_criteria_html', '')
                session.save()
                ReviewMessage.objects.create(session=session, role='ai', content=f"[Generated result]\nDescription: {result.get('description_html', '')}\nAcceptance Criteria: {result.get('acceptance_criteria_html', '')}")
                return Response({
                    'finished': True,
                    'description_html': result.get('description_html', ''),
                    'acceptance_criteria_html': result.get('acceptance_criteria_html', '')
                })
        except Exception as e:
            return Response({"detail": f"AI service error: {str(e)}"}, status=500)


class ReviewSessionConfirmView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = ReviewSession.objects.get(id=session_id, user=request.user)
        except ReviewSession.DoesNotExist:
            return Response({"detail": "Session not found"}, status=404)

        if session.status != 'generated':
            return Response({"detail": "Session is not in generated state"}, status=400)

        session.status = 'confirmed'
        session.save()
        return Response({"detail": "Session confirmed"})


class ReviewSessionDiscardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = ReviewSession.objects.get(id=session_id, user=request.user)
        except ReviewSession.DoesNotExist:
            return Response({"detail": "Session not found"}, status=404)

        session.status = 'discarded'
        session.save()
        return Response({"detail": "Session discarded"})


class AdminReviewSessionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, requirement_id):
        try:
            requirement = RequirementRequest.objects.get(id=requirement_id)
        except RequirementRequest.DoesNotExist:
            return Response({"detail": "Requirement not found"}, status=404)

        if requirement.owning_department != request.user.department:
            return Response({"detail": "Requirement not found"}, status=404)

        sessions = ReviewSession.objects.filter(requirement=requirement).order_by('-created_at')
        serializer = ReviewSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class AttachmentDownloadView(APIView):
    """
    Secure endpoint to download attachments.
    Ensures only the submitter or an admin can download the file.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            attachment = Attachment.objects.select_related('requirement__submitter').get(pk=pk)
        except Attachment.DoesNotExist:
            raise Http404("Attachment not found")

        requirement = attachment.requirement
        user = request.user

        # Defensive Permission Check: Admin (same department) or Submitter
        is_admin = getattr(user, 'role', None) == 'admin'
        is_same_department_admin = is_admin and getattr(user, 'department', None) == requirement.owning_department
        is_submitter = requirement.submitter_id == user.id

        if not (is_same_department_admin or is_submitter):
            return Response({"detail": "You do not have permission to download this file."}, status=403)

        file_path = attachment.file.path
        if not os.path.exists(file_path):
            raise Http404("File not found on server")

        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)

        file_name = os.path.basename(attachment.file.name)
        encoded_name = quote(file_name)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_name}"

        return response
