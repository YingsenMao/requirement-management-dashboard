import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from .models import RequirementRequest, Attachment, ReviewSession, ReviewMessage

User = get_user_model()

@pytest.mark.django_db
def test_create_admin_user():
    admin = User.objects.create_user(username='admin_user', password='securepassword123', role='admin')
    assert admin.role == 'admin'
    assert admin.check_password('securepassword123')

@pytest.mark.django_db
def test_create_regular_user():
    user = User.objects.create_user(username='regular_user', password='securepassword123', role='user')
    assert user.role == 'user'
    assert user.check_password('securepassword123')

@pytest.mark.django_db
def test_jwt_token_obtain_pair():
    client = APIClient()
    User.objects.create_user(username='jwt_test_user', password='securepassword123', role='user')
    
    response = client.post('/api/token/', {'username': 'jwt_test_user', 'password': 'securepassword123'}, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    
    token = AccessToken(response.data['access'])
    assert token['role'] == 'user'
    assert token['username'] == 'jwt_test_user'

@pytest.mark.django_db
def test_jwt_token_obtain_pair_admin():
    client = APIClient()
    User.objects.create_user(username='jwt_test_admin', password='securepassword123', role='admin', department='it')
    
    response = client.post('/api/token/', {'username': 'jwt_test_admin', 'password': 'securepassword123'}, format='json')
    assert response.status_code == 200
    
    token = AccessToken(response.data['access'])
    assert token['role'] == 'admin'
    assert token['username'] == 'jwt_test_admin'
    assert token['department'] == 'it'

@pytest.mark.django_db
def test_jwt_token_refresh():
    client = APIClient()
    User.objects.create_user(username='refresh_test_user', password='securepassword123', role='user')
    
    response = client.post('/api/token/', {'username': 'refresh_test_user', 'password': 'securepassword123'}, format='json')
    refresh_token = response.data['refresh']
    
    response = client.post('/api/token/refresh/', {'refresh': refresh_token}, format='json')
    assert response.status_code == 200
    assert 'access' in response.data

@pytest.mark.django_db
def test_create_requirement_request_defaults():
    user = User.objects.create_user(username='req_test_user', password='securepassword123')
    req = RequirementRequest.objects.create(
        name='Test Requirement',
        summary='This is a test summary.',
        country='China',
        requirement_type='bug',
        impacted_users='<100',
        submitter=user
    )
    assert req.name == 'Test Requirement'
    assert req.workload == 'pending'
    assert req.status == 'pending_review'
    assert req.priority_score is None
    assert req.submitter == user
    assert req.supplementary_materials == []

@pytest.mark.django_db
def test_priority_score_pending_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', country='China', requirement_type='regulatory',
        impacted_users='>1000', revenue_impact='>1M', supplementary_materials=['a', 'b', 'c', 'd', 'e'],
        workload='pending', submitter=user
    )
    assert req.priority_score is None

@pytest.mark.django_db
def test_priority_score_small_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', country='China', requirement_type='regulatory',
        impacted_users='>1000', revenue_impact='>1M', supplementary_materials=['a', 'b', 'c', 'd'],
        workload='small', submitter=user
    )
    # regulatory(50) + >1000(40) + >1M(50) + 4 materials(80→max50) + small(50) = 240
    assert req.priority_score == 240

@pytest.mark.django_db
def test_priority_score_medium_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', country='China', requirement_type='bug',
        impacted_users='<100', revenue_impact=None, supplementary_materials=[],
        workload='medium', submitter=user
    )
    # bug(30) + <100(10) + None(0) + 0 materials(0) + medium(10) = 50
    assert req.priority_score == 50

@pytest.mark.django_db
def test_priority_score_large_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', country='China', requirement_type='optimization',
        impacted_users='100-500', revenue_impact='50k-300k', supplementary_materials=['a'],
        workload='large', submitter=user
    )
    # optimization(0) + 100-500(20) + 50k-300k(20) + 1 material(20) + large(-10) = 50
    assert req.priority_score == 50

@pytest.mark.django_db
def test_user_global_read_and_owner_write():
    user1 = User.objects.create_user(username='user1', password='pass')
    user2 = User.objects.create_user(username='user2', password='pass')
    
    req1 = RequirementRequest.objects.create(name='Req1', summary='Sum1', country='China', requirement_type='bug', impacted_users='<100', submitter=user1)
    req2 = RequirementRequest.objects.create(name='Req2', summary='Sum2', country='China', requirement_type='bug', impacted_users='<100', submitter=user2)
    
    client = APIClient()
    client.force_authenticate(user=user1)
    
    # User1 can see all requests (Global Read)
    response = client.get('/api/requests/')
    assert response.status_code == 200
    assert len(response.data) == 2
    
    # User1 can edit their own pending_review request
    response = client.patch(f'/api/requests/{req1.id}/', {'name': 'UpdatedReq1'}, format='json')
    assert response.status_code == 200
    
    # User1 cannot edit user2's request
    response = client.patch(f'/api/requests/{req2.id}/', {'name': 'UpdatedReq2'}, format='json')
    assert response.status_code == 403
    
    # User1 cannot delete user2's request
    response = client.delete(f'/api/requests/{req2.id}/')
    assert response.status_code == 403
    
    # User1 can delete their own request
    response = client.delete(f'/api/requests/{req1.id}/')
    assert response.status_code == 204

@pytest.mark.django_db
def test_user_locking_mechanism():
    user = User.objects.create_user(username='user_lock', password='pass')
    req = RequirementRequest.objects.create(name='LockedReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user, status='confirmed')
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Try to update a confirmed request
    response = client.patch(f'/api/requests/{req.id}/', {'name': 'UpdatedName'}, format='json')
    assert response.status_code == 403

@pytest.mark.django_db
def test_admin_view_and_sorting():
    admin = User.objects.create_user(username='admin_sort', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_sort', password='pass')
    
    RequirementRequest.objects.create(name='LowScore', summary='Sum', country='China', requirement_type='optimization', impacted_users='<100', submitter=user, workload='large')
    RequirementRequest.objects.create(name='HighScore', summary='Sum', country='China', requirement_type='regulatory', impacted_users='>1000', submitter=user, workload='small')
    
    client = APIClient()
    client.force_authenticate(user=admin)
    
    response = client.get('/api/admin/requests/')
    assert response.status_code == 200
    results = response.data
    assert len(results) == 2
    assert results[0]['name'] == 'HighScore'
    assert results[1]['name'] == 'LowScore'

@pytest.mark.django_db
def test_admin_update_workload_and_status():
    admin = User.objects.create_user(username='admin_update', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_update', password='pass')
    req = RequirementRequest.objects.create(name='UpdateReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user)
    
    client = APIClient()
    client.force_authenticate(user=admin)
    
    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'confirmed'}, format='json')
    assert response.status_code == 200
    assert response.data['workload'] == 'small'
    assert response.data['status'] == 'confirmed'
    assert response.data['priority_score'] is not None

@pytest.mark.django_db
def test_admin_field_level_restrictions():
    admin = User.objects.create_user(username='admin_restrict', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_restrict', password='pass')
    req = RequirementRequest.objects.create(
        name='OriginalName', summary='Sum', country='China', 
        requirement_type='bug', impacted_users='<100', submitter=user
    )
    
    client = APIClient()
    client.force_authenticate(user=admin)
    
    # Admin tries to update workload (Allowed)
    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small'}, format='json')
    assert response.status_code == 200
    assert response.data['workload'] == 'small'
    
    # Admin tries to update name (Should be ignored due to read_only)
    response = client.patch(f'/api/admin/requests/{req.id}/', {'name': 'HackedName'}, format='json')
    assert response.status_code == 200
    assert response.data['name'] == 'OriginalName'

@pytest.mark.django_db
def test_admin_reject_with_reason():
    admin = User.objects.create_user(username='admin_reject', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_reject', password='pass')
    req = RequirementRequest.objects.create(name='RejectReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user)

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'rejected', 'reject_reason': 'Insufficient data'}, format='json')
    assert response.status_code == 200
    assert response.data['status'] == 'rejected'
    assert response.data['reject_reason'] == 'Insufficient data'

@pytest.mark.django_db
def test_admin_reject_without_reason_fails():
    admin = User.objects.create_user(username='admin_reject2', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_reject2', password='pass')
    req = RequirementRequest.objects.create(name='RejectReq2', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user)

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'rejected'}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_can_edit_rejected_requirement():
    user = User.objects.create_user(username='user_edit_rejected', password='pass')
    req = RequirementRequest.objects.create(name='RejectedReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user, status='rejected', reject_reason='Not enough info')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f'/api/requests/{req.id}/', {'name': 'UpdatedReq'}, format='json')
    assert response.status_code == 200
    assert response.data['name'] == 'UpdatedReq'
    assert response.data['status'] == 'pending_review'
    assert response.data['reject_reason'] is None

@pytest.mark.django_db
def test_non_rejected_status_clears_reject_reason():
    admin = User.objects.create_user(username='admin_clear', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_clear', password='pass')
    req = RequirementRequest.objects.create(name='ClearReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user, status='rejected', reject_reason='Old reason')

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'confirmed'}, format='json')
    assert response.status_code == 200
    assert response.data['status'] == 'confirmed'
    assert response.data['reject_reason'] is None

@pytest.mark.django_db
def test_admin_set_estimated_completion_date():
    admin = User.objects.create_user(username='admin_ecd', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_ecd', password='pass')
    req = RequirementRequest.objects.create(name='ECDReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user)

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'confirmed', 'estimated_completion_date': '2026-08-15'}, format='json')
    assert response.status_code == 200
    assert response.data['estimated_completion_date'] == '2026-08-15'

@pytest.mark.django_db
def test_user_cannot_set_estimated_completion_date():
    user = User.objects.create_user(username='user_ecd_forbidden', password='pass')
    req = RequirementRequest.objects.create(name='ECDReq2', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f'/api/requests/{req.id}/', {'name': 'Updated', 'estimated_completion_date': '2026-08-15'}, format='json')
    assert response.status_code == 200
    assert response.data['estimated_completion_date'] is None

@pytest.mark.django_db
def test_urgency_default_medium():
    user = User.objects.create_user(username='user_urgency', password='pass')
    req = RequirementRequest.objects.create(name='UrgReq', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user)
    assert req.urgency == 'medium'

@pytest.mark.django_db
def test_user_can_set_urgency():
    user = User.objects.create_user(username='user_urgency_set', password='pass')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/requests/', {
        'name': 'UrgReq2', 'summary': 'Sum', 'country': 'China',
        'requirement_type': 'bug', 'urgency': 'high', 'owning_department': 'it'
    }, format='json')
    assert response.status_code == 201
    assert response.data['urgency'] == 'high'

@pytest.mark.django_db
def test_admin_cannot_modify_urgency():
    admin = User.objects.create_user(username='admin_urgency', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='user_urgency_owner', password='pass')
    req = RequirementRequest.objects.create(name='UrgReq3', summary='Sum', country='China', requirement_type='bug', impacted_users='<100', submitter=user, urgency='low')

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'confirmed', 'urgency': 'high'}, format='json')
    assert response.status_code == 200
    assert response.data['urgency'] == 'low'

@pytest.mark.django_db
def test_owning_department_defaults_to_it():
    user = User.objects.create_user(username='dept_default_user', password='pass')
    req = RequirementRequest.objects.create(name='DeptReq', summary='Sum', country='China', requirement_type='bug', submitter=user)
    assert req.owning_department == 'it'

@pytest.mark.django_db
def test_create_requirement_requires_owning_department():
    user = User.objects.create_user(username='dept_missing_user', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/requests/', {
        'name': 'NoDept', 'summary': 'Sum', 'country': 'China', 'requirement_type': 'bug'
    }, format='json')
    assert response.status_code == 400
    assert 'owning_department' in response.data

@pytest.mark.django_db
def test_create_requirement_invalid_owning_department():
    user = User.objects.create_user(username='dept_invalid_user', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/requests/', {
        'name': 'BadDept', 'summary': 'Sum', 'country': 'China',
        'requirement_type': 'bug', 'owning_department': 'hr'
    }, format='json')
    assert response.status_code == 400
    assert 'owning_department' in response.data

@pytest.mark.django_db
def test_create_requirement_with_owning_department():
    user = User.objects.create_user(username='dept_ok_user', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/requests/', {
        'name': 'RndReq', 'summary': 'Sum', 'country': 'China',
        'requirement_type': 'bug', 'owning_department': 'rnd'
    }, format='json')
    assert response.status_code == 201
    assert response.data['owning_department'] == 'rnd'

@pytest.mark.django_db
def test_regular_user_sees_all_departments():
    user = User.objects.create_user(username='dept_all_user', password='pass')
    RequirementRequest.objects.create(name='ITReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it')
    RequirementRequest.objects.create(name='RndReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='rnd')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get('/api/requests/')
    assert response.status_code == 200
    assert len(response.data) == 2

@pytest.mark.django_db
def test_admin_department_isolation_list():
    it_admin = User.objects.create_user(username='it_admin', password='pass', role='admin', department='it')
    rnd_admin = User.objects.create_user(username='rnd_admin', password='pass', role='admin', department='rnd')
    user = User.objects.create_user(username='dept_iso_user', password='pass')

    RequirementRequest.objects.create(name='ITReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it')
    RequirementRequest.objects.create(name='RndReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='rnd')

    client = APIClient()

    client.force_authenticate(user=it_admin)
    response = client.get('/api/admin/requests/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'ITReq'
    assert response.data[0]['owning_department'] == 'it'

    client.force_authenticate(user=rnd_admin)
    response = client.get('/api/admin/requests/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'RndReq'
    assert response.data[0]['owning_department'] == 'rnd'

@pytest.mark.django_db
def test_admin_cross_department_retrieve_and_assess_404():
    it_admin = User.objects.create_user(username='it_admin_404', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='dept_404_user', password='pass')
    rnd_req = RequirementRequest.objects.create(name='RndReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='rnd')

    client = APIClient()
    client.force_authenticate(user=it_admin)

    response = client.get(f'/api/admin/requests/{rnd_req.id}/')
    assert response.status_code == 404

    response = client.patch(f'/api/admin/requests/{rnd_req.id}/', {'workload': 'small', 'status': 'confirmed'}, format='json')
    assert response.status_code == 404

@pytest.mark.django_db
def test_admin_null_department_sees_empty_list():
    admin = User.objects.create_user(username='null_dept_admin', password='pass', role='admin')
    user = User.objects.create_user(username='null_dept_user', password='pass')
    RequirementRequest.objects.create(name='ITReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it')

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get('/api/admin/requests/')
    assert response.status_code == 200
    assert len(response.data) == 0

@pytest.mark.django_db
def test_admin_cross_department_attachment_download(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    it_admin = User.objects.create_user(username='it_admin_dl', password='pass', role='admin', department='it')
    rnd_admin = User.objects.create_user(username='rnd_admin_dl', password='pass', role='admin', department='rnd')
    user = User.objects.create_user(username='dept_dl_user', password='pass')
    rnd_req = RequirementRequest.objects.create(name='RndReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='rnd')
    attachment = Attachment.objects.create(requirement=rnd_req, file=SimpleUploadedFile('doc.pdf', b'x' * 100, content_type='application/pdf'))

    client = APIClient()

    client.force_authenticate(user=it_admin)
    response = client.get(f'/api/attachments/{attachment.id}/download/')
    assert response.status_code == 403

    client.force_authenticate(user=rnd_admin)
    response = client.get(f'/api/attachments/{attachment.id}/download/')
    assert response.status_code == 200

    client.force_authenticate(user=user)
    response = client.get(f'/api/attachments/{attachment.id}/download/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_owner_can_change_owning_department_when_pending_or_rejected():
    user = User.objects.create_user(username='dept_change_user', password='pass')
    req_pending = RequirementRequest.objects.create(name='PendingReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it', status='pending_review')
    req_rejected = RequirementRequest.objects.create(name='RejectedReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it', status='rejected', reject_reason='Wrong dept')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f'/api/requests/{req_pending.id}/', {'owning_department': 'rnd'}, format='json')
    assert response.status_code == 200
    assert response.data['owning_department'] == 'rnd'

    response = client.patch(f'/api/requests/{req_rejected.id}/', {'owning_department': 'rnd'}, format='json')
    assert response.status_code == 200
    assert response.data['owning_department'] == 'rnd'
    assert response.data['status'] == 'pending_review'

@pytest.mark.django_db
def test_owner_cannot_change_owning_department_when_locked():
    user = User.objects.create_user(username='dept_lock_user', password='pass')
    req = RequirementRequest.objects.create(name='LockedReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it', status='confirmed')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f'/api/requests/{req.id}/', {'owning_department': 'rnd'}, format='json')
    assert response.status_code == 403
    req.refresh_from_db()
    assert req.owning_department == 'it'

@pytest.mark.django_db
def test_admin_cannot_modify_owning_department():
    admin = User.objects.create_user(username='it_admin_mod', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='dept_mod_user', password='pass')
    req = RequirementRequest.objects.create(name='ITReq', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it')

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'owning_department': 'rnd'}, format='json')
    assert response.status_code == 200
    assert response.data['owning_department'] == 'it'

@pytest.mark.django_db
def test_admin_create_regular_user_account():
    admin = User.objects.create_user(username='creator_admin', password='pass', role='admin', department='it')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'new_regular', 'password': 'Str0ngPass!234', 'role': 'user'
    }, format='json')
    assert response.status_code == 201
    assert response.data['username'] == 'new_regular'
    assert response.data['role'] == 'user'
    assert response.data['department'] is None

    created = User.objects.get(username='new_regular')
    assert created.department is None
    assert created.check_password('Str0ngPass!234')

@pytest.mark.django_db
def test_admin_create_regular_user_department_forced_none():
    admin = User.objects.create_user(username='creator_admin2', password='pass', role='admin', department='it')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'sneaky_user', 'password': 'Str0ngPass!234', 'role': 'user', 'department': 'rnd'
    }, format='json')
    assert response.status_code == 201
    assert response.data['department'] is None
    assert User.objects.get(username='sneaky_user').department is None

@pytest.mark.django_db
def test_admin_create_admin_account():
    admin = User.objects.create_user(username='creator_admin3', password='pass', role='admin', department='it')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'new_rnd_admin', 'password': 'Str0ngPass!234', 'role': 'admin', 'department': 'rnd'
    }, format='json')
    assert response.status_code == 201
    assert response.data['role'] == 'admin'
    assert response.data['department'] == 'rnd'

    created = User.objects.get(username='new_rnd_admin')
    assert created.role == 'admin'
    assert created.department == 'rnd'
    assert created.check_password('Str0ngPass!234')

@pytest.mark.django_db
def test_admin_create_admin_requires_department():
    admin = User.objects.create_user(username='creator_admin4', password='pass', role='admin', department='it')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'no_dept_admin', 'password': 'Str0ngPass!234', 'role': 'admin'
    }, format='json')
    assert response.status_code == 400
    assert 'department' in response.data
    assert not User.objects.filter(username='no_dept_admin').exists()

@pytest.mark.django_db
def test_admin_create_admin_invalid_department():
    admin = User.objects.create_user(username='creator_admin5', password='pass', role='admin', department='it')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'bad_dept_admin', 'password': 'Str0ngPass!234', 'role': 'admin', 'department': 'hr'
    }, format='json')
    assert response.status_code == 400
    assert 'department' in response.data

@pytest.mark.django_db
def test_admin_create_duplicate_username():
    admin = User.objects.create_user(username='creator_admin6', password='pass', role='admin', department='it')
    User.objects.create_user(username='existing_user', password='pass')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'existing_user', 'password': 'Str0ngPass!234', 'role': 'user'
    }, format='json')
    assert response.status_code == 400
    assert 'username' in response.data

@pytest.mark.django_db
def test_admin_create_weak_password_rejected():
    admin = User.objects.create_user(username='creator_admin7', password='pass', role='admin', department='it')
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post('/api/admin/users/', {
        'username': 'weak_pass_user', 'password': '123', 'role': 'user'
    }, format='json')
    assert response.status_code == 400
    assert 'password' in response.data

@pytest.mark.django_db
def test_regular_user_cannot_create_accounts():
    user = User.objects.create_user(username='regular_no_power', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/admin/users/', {
        'username': 'hacked_user', 'password': 'Str0ngPass!234', 'role': 'user'
    }, format='json')
    assert response.status_code == 403
    assert not User.objects.filter(username='hacked_user').exists()

@pytest.mark.django_db
def test_unauthenticated_cannot_create_accounts():
    client = APIClient()

    response = client.post('/api/admin/users/', {
        'username': 'anon_user', 'password': 'Str0ngPass!234', 'role': 'user'
    }, format='json')
    assert response.status_code in [401, 403]

@pytest.mark.django_db
def test_jwt_department_claim_regular_user_is_none():
    client = APIClient()
    User.objects.create_user(username='jwt_dept_user', password='securepassword123', role='user')

    response = client.post('/api/token/', {'username': 'jwt_dept_user', 'password': 'securepassword123'}, format='json')
    assert response.status_code == 200

    token = AccessToken(response.data['access'])
    assert token['department'] is None

@pytest.mark.django_db
def test_ai_review_session_create_without_api_key():
    user = User.objects.create_user(username='ai_test_user', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    with override_settings(DASHSCOPE_API_KEY=''):
        response = client.post('/api/ai/review-sessions/', {
            'mode': 'create',
            'form_context': {'name': 'Test', 'summary': 'Test summary'}
        }, format='json')
    assert response.status_code == 503

@pytest.mark.django_db
def test_ai_review_session_create_missing_form_context():
    user = User.objects.create_user(username='ai_test_user2', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post('/api/ai/review-sessions/', {
            'mode': 'create',
            'form_context': {'name': 'Test'}
        }, format='json')
    assert response.status_code == 400
    assert 'form_context' in response.data

@pytest.mark.django_db
def test_ai_review_session_edit_mode_requires_requirement_id():
    user = User.objects.create_user(username='ai_test_user3', password='pass')
    client = APIClient()
    client.force_authenticate(user=user)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post('/api/ai/review-sessions/', {
            'mode': 'edit',
            'form_context': {'name': 'Test', 'summary': 'Test summary'}
        }, format='json')
    assert response.status_code == 400
    assert 'requirement_id' in response.data

@pytest.mark.django_db
def test_ai_review_session_edit_mode_validates_ownership():
    user1 = User.objects.create_user(username='ai_owner1', password='pass')
    user2 = User.objects.create_user(username='ai_owner2', password='pass')
    req = RequirementRequest.objects.create(name='Test', summary='Sum', country='China', requirement_type='bug', submitter=user1, owning_department='it')

    client = APIClient()
    client.force_authenticate(user=user2)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post('/api/ai/review-sessions/', {
            'mode': 'edit',
            'requirement_id': req.id,
            'form_context': {'name': 'Test', 'summary': 'Test summary'}
        }, format='json')
    assert response.status_code == 403

@pytest.mark.django_db
def test_ai_review_session_edit_mode_validates_status():
    user = User.objects.create_user(username='ai_status_user', password='pass')
    req = RequirementRequest.objects.create(name='Test', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it', status='confirmed')

    client = APIClient()
    client.force_authenticate(user=user)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post('/api/ai/review-sessions/', {
            'mode': 'edit',
            'requirement_id': req.id,
            'form_context': {'name': 'Test', 'summary': 'Test summary'}
        }, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ai_review_session_concurrent_limit():
    user = User.objects.create_user(username='ai_limit_user', password='pass')
    for i in range(3):
        ReviewSession.objects.create(user=user, mode='create', status='asking', form_context={'name': f'Test{i}', 'summary': f'Sum{i}'})

    client = APIClient()
    client.force_authenticate(user=user)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post('/api/ai/review-sessions/', {
            'mode': 'create',
            'form_context': {'name': 'Test', 'summary': 'Test summary'}
        }, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ai_review_message_non_owner_forbidden():
    user1 = User.objects.create_user(username='ai_msg_owner1', password='pass')
    user2 = User.objects.create_user(username='ai_msg_owner2', password='pass')
    session = ReviewSession.objects.create(user=user1, mode='create', status='asking', form_context={'name': 'Test', 'summary': 'Sum'})

    client = APIClient()
    client.force_authenticate(user=user2)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post(f'/api/ai/review-sessions/{session.id}/messages/', {
            'answer': 'Test answer'
        }, format='json')
    assert response.status_code == 404

@pytest.mark.django_db
def test_ai_review_message_wrong_state():
    user = User.objects.create_user(username='ai_msg_state', password='pass')
    session = ReviewSession.objects.create(user=user, mode='create', status='generated', form_context={'name': 'Test', 'summary': 'Sum'})

    client = APIClient()
    client.force_authenticate(user=user)

    with override_settings(DASHSCOPE_API_KEY='test_key'):
        response = client.post(f'/api/ai/review-sessions/{session.id}/messages/', {
            'answer': 'Test answer'
        }, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ai_review_confirm_wrong_state():
    user = User.objects.create_user(username='ai_confirm_state', password='pass')
    session = ReviewSession.objects.create(user=user, mode='create', status='asking', form_context={'name': 'Test', 'summary': 'Sum'})

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f'/api/ai/review-sessions/{session.id}/confirm/')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ai_review_confirm_success():
    user = User.objects.create_user(username='ai_confirm_ok', password='pass')
    session = ReviewSession.objects.create(user=user, mode='create', status='generated', form_context={'name': 'Test', 'summary': 'Sum'}, generated_description='<p>Desc</p>', generated_acceptance='<ul><li>AC</li></ul>')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f'/api/ai/review-sessions/{session.id}/confirm/')
    assert response.status_code == 200
    session.refresh_from_db()
    assert session.status == 'confirmed'

@pytest.mark.django_db
def test_ai_review_discard_success():
    user = User.objects.create_user(username='ai_discard_ok', password='pass')
    session = ReviewSession.objects.create(user=user, mode='create', status='asking', form_context={'name': 'Test', 'summary': 'Sum'})

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f'/api/ai/review-sessions/{session.id}/discard/')
    assert response.status_code == 200
    session.refresh_from_db()
    assert session.status == 'discarded'

@pytest.mark.django_db
def test_admin_review_sessions_same_department():
    admin = User.objects.create_user(username='ai_admin_same', password='pass', role='admin', department='it')
    user = User.objects.create_user(username='ai_req_owner', password='pass')
    req = RequirementRequest.objects.create(name='Test', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it')
    session = ReviewSession.objects.create(user=user, requirement=req, mode='edit', status='confirmed', form_context={'name': 'Test', 'summary': 'Sum'}, generated_description='<p>Desc</p>')
    ReviewMessage.objects.create(session=session, role='ai', content='Question 1')
    ReviewMessage.objects.create(session=session, role='user', content='Answer 1')

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get(f'/api/admin/requests/{req.id}/review-sessions/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert len(response.data[0]['messages']) == 2

@pytest.mark.django_db
def test_admin_review_sessions_cross_department_404():
    admin = User.objects.create_user(username='ai_admin_cross', password='pass', role='admin', department='rnd')
    user = User.objects.create_user(username='ai_req_owner2', password='pass')
    req = RequirementRequest.objects.create(name='Test', summary='Sum', country='China', requirement_type='bug', submitter=user, owning_department='it')
    session = ReviewSession.objects.create(user=user, requirement=req, mode='edit', status='confirmed', form_context={'name': 'Test', 'summary': 'Sum'})

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get(f'/api/admin/requests/{req.id}/review-sessions/')
    assert response.status_code == 404

@pytest.mark.django_db
def test_html_sanitizer_strips_script():
    from requirements_app.services.ai_review import sanitize_html
    dirty = '<script>alert("xss")</script><p>Safe content</p>'
    clean = sanitize_html(dirty)
    assert '<script>' not in clean
    assert '<p>Safe content</p>' in clean

@pytest.mark.django_db
def test_html_sanitizer_allows_valid_tags():
    from requirements_app.services.ai_review import sanitize_html
    html = '<h3>Title</h3><p>Text with <strong>bold</strong> and <em>italic</em></p><ul><li>Item 1</li></ul>'
    result = sanitize_html(html)
    assert '<h3>Title</h3>' in result
    assert '<strong>bold</strong>' in result
    assert '<ul><li>Item 1</li></ul>' in result
