import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from requirements_app.models import ReviewSession, ReviewMessage, RequirementRequest

User = get_user_model()


@pytest.mark.django_db
def test_audit_changelist_returns_200_for_superuser():
    """Audit changelist should return 200 for superuser."""
    superuser = User.objects.create_superuser(
        username='audit_super',
        password='testpass123',
        email='super@test.com'
    )
    client = Client()
    client.force_login(superuser)

    response = client.get('/admin/requirements_app/reviewsession/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_audit_changelist_contains_stats_context():
    """Audit changelist should inject stats context."""
    superuser = User.objects.create_superuser(
        username='audit_super2',
        password='testpass123',
        email='super2@test.com'
    )
    user1 = User.objects.create_user(username='user1', password='pass1', role='user')
    user2 = User.objects.create_user(username='user2', password='pass2', role='user')

    # Create test sessions and messages
    session1 = ReviewSession.objects.create(
        user=user1,
        mode='create',
        status='confirmed',
        form_context={'name': 'Test 1', 'summary': 'Summary 1'}
    )
    ReviewMessage.objects.create(session=session1, role='ai', content='Question 1')
    ReviewMessage.objects.create(session=session1, role='user', content='Answer 1')
    ReviewMessage.objects.create(session=session1, role='ai', content='Question 2')

    session2 = ReviewSession.objects.create(
        user=user2,
        mode='edit',
        status='discarded',
        form_context={'name': 'Test 2', 'summary': 'Summary 2'}
    )
    ReviewMessage.objects.create(session=session2, role='ai', content='Question 1')

    client = Client()
    client.force_login(superuser)

    response = client.get('/admin/requirements_app/reviewsession/')
    assert response.status_code == 200

    # Check context contains stats
    context = response.context
    assert context['audit_total_sessions'] == 2
    assert context['audit_total_messages'] == 4
    assert context['audit_unique_users'] == 2
    assert context['audit_status_counts']['confirmed'] == 1
    assert context['audit_status_counts']['discarded'] == 1
    assert context['audit_confirmation_rate'] == 50.0
    assert context['audit_avg_messages'] == 2.0

    # Check per-user data
    per_user = context['audit_per_user']
    assert len(per_user) == 2
    # user1 has 1 session, 3 messages, 1 confirmed
    user1_stat = next(u for u in per_user if u['user__username'] == 'user1')
    assert user1_stat['sessions'] == 1
    assert user1_stat['messages'] == 3
    assert user1_stat['confirmed'] == 1
    # user2 has 1 session, 1 message, 0 confirmed
    user2_stat = next(u for u in per_user if u['user__username'] == 'user2')
    assert user2_stat['sessions'] == 1
    assert user2_stat['messages'] == 1
    assert user2_stat['confirmed'] == 0


@pytest.mark.django_db
def test_audit_session_detail_shows_messages_inline():
    """Session detail page should show messages inline."""
    superuser = User.objects.create_superuser(
        username='audit_super3',
        password='testpass123',
        email='super3@test.com'
    )
    user = User.objects.create_user(username='user_detail', password='pass', role='user')
    session = ReviewSession.objects.create(
        user=user,
        mode='create',
        status='confirmed',
        form_context={'name': 'Test', 'summary': 'Summary'}
    )
    ReviewMessage.objects.create(session=session, role='ai', content='AI question')
    ReviewMessage.objects.create(session=session, role='user', content='User answer')

    client = Client()
    client.force_login(superuser)

    response = client.get(f'/admin/requirements_app/reviewsession/{session.id}/change/')
    assert response.status_code == 200
    # Check that messages are in the response (inline)
    content = response.content.decode('utf-8')
    assert 'AI question' in content
    assert 'User answer' in content


@pytest.mark.django_db
def test_audit_readonly_permissions_enforced():
    """Audit page should be read-only (no add/change/delete)."""
    superuser = User.objects.create_superuser(
        username='audit_super4',
        password='testpass123',
        email='super4@test.com'
    )
    user = User.objects.create_user(username='user_perm', password='pass', role='user')
    session = ReviewSession.objects.create(
        user=user,
        mode='create',
        status='confirmed',
        form_context={'name': 'Test', 'summary': 'Summary'}
    )

    client = Client()
    client.force_login(superuser)

    # Add page should be forbidden
    response = client.get('/admin/requirements_app/reviewsession/add/')
    assert response.status_code == 403

    # Delete should be forbidden
    response = client.post(f'/admin/requirements_app/reviewsession/{session.id}/delete/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_audit_non_staff_access_denied():
    """Non-staff user should not access audit page."""
    user = User.objects.create_user(
        username='nonstaff',
        password='pass',
        role='user',
        is_staff=False
    )
    client = Client()
    client.force_login(user)

    response = client.get('/admin/requirements_app/reviewsession/')
    # Should redirect to login or return 403
    assert response.status_code in [302, 403]


@pytest.mark.django_db
def test_audit_message_admin_readonly():
    """ReviewMessage admin should be read-only."""
    superuser = User.objects.create_superuser(
        username='audit_super5',
        password='testpass123',
        email='super5@test.com'
    )
    user = User.objects.create_user(username='user_msg', password='pass', role='user')
    session = ReviewSession.objects.create(
        user=user,
        mode='create',
        status='confirmed',
        form_context={'name': 'Test', 'summary': 'Summary'}
    )
    message = ReviewMessage.objects.create(session=session, role='ai', content='Test message')

    client = Client()
    client.force_login(superuser)

    # List should be accessible
    response = client.get('/admin/requirements_app/reviewmessage/')
    assert response.status_code == 200

    # Add should be forbidden
    response = client.get('/admin/requirements_app/reviewmessage/add/')
    assert response.status_code == 403

    # Delete should be forbidden
    response = client.post(f'/admin/requirements_app/reviewmessage/{message.id}/delete/')
    assert response.status_code == 403
