import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from .models import RequirementRequest

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
    User.objects.create_user(username='jwt_test_admin', password='securepassword123', role='admin')
    
    response = client.post('/api/token/', {'username': 'jwt_test_admin', 'password': 'securepassword123'}, format='json')
    assert response.status_code == 200
    
    token = AccessToken(response.data['access'])
    assert token['role'] == 'admin'
    assert token['username'] == 'jwt_test_admin'

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
        region='china',
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
        name='Test', summary='Test', region='china', requirement_type='regulatory',
        impacted_users='>1000', revenue_impact='>1M', supplementary_materials=['a', 'b', 'c', 'd', 'e'],
        workload='pending', submitter=user
    )
    assert req.priority_score is None

@pytest.mark.django_db
def test_priority_score_small_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', region='china', requirement_type='regulatory',
        impacted_users='>1000', revenue_impact='>1M', supplementary_materials=['a', 'b', 'c', 'd'],
        workload='small', submitter=user
    )
    # regulatory(50) + >1000(40) + >1M(50) + 4 materials(80→max50) + small(50) = 240
    assert req.priority_score == 240

@pytest.mark.django_db
def test_priority_score_medium_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', region='china', requirement_type='bug',
        impacted_users='<100', revenue_impact=None, supplementary_materials=[],
        workload='medium', submitter=user
    )
    # bug(30) + <100(10) + None(0) + 0 materials(0) + medium(10) = 50
    assert req.priority_score == 50

@pytest.mark.django_db
def test_priority_score_large_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', region='china', requirement_type='optimization',
        impacted_users='100-500', revenue_impact='50k-300k', supplementary_materials=['a'],
        workload='large', submitter=user
    )
    # optimization(0) + 100-500(20) + 50k-300k(20) + 1 material(20) + large(-10) = 50
    assert req.priority_score == 50

@pytest.mark.django_db
def test_user_global_read_and_owner_write():
    user1 = User.objects.create_user(username='user1', password='pass')
    user2 = User.objects.create_user(username='user2', password='pass')
    
    req1 = RequirementRequest.objects.create(name='Req1', summary='Sum1', region='china', requirement_type='bug', impacted_users='<100', submitter=user1)
    req2 = RequirementRequest.objects.create(name='Req2', summary='Sum2', region='china', requirement_type='bug', impacted_users='<100', submitter=user2)
    
    client = APIClient()
    client.force_authenticate(user=user1)
    
    # User1 can see all requests (Global Read)
    response = client.get('/api/requests/')
    assert response.status_code == 200
    assert len(response.data['results']) == 2
    
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
    req = RequirementRequest.objects.create(name='LockedReq', summary='Sum', region='china', requirement_type='bug', impacted_users='<100', submitter=user, status='confirmed')
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Try to update a confirmed request
    response = client.patch(f'/api/requests/{req.id}/', {'name': 'UpdatedName'}, format='json')
    assert response.status_code == 403

@pytest.mark.django_db
def test_admin_view_and_sorting():
    admin = User.objects.create_user(username='admin_sort', password='pass', role='admin')
    user = User.objects.create_user(username='user_sort', password='pass')
    
    RequirementRequest.objects.create(name='LowScore', summary='Sum', region='china', requirement_type='optimization', impacted_users='<100', submitter=user, workload='large')
    RequirementRequest.objects.create(name='HighScore', summary='Sum', region='china', requirement_type='regulatory', impacted_users='>1000', submitter=user, workload='small')
    
    client = APIClient()
    client.force_authenticate(user=admin)
    
    response = client.get('/api/admin/requests/')
    assert response.status_code == 200
    results = response.data['results']
    assert len(results) == 2
    assert results[0]['name'] == 'HighScore'
    assert results[1]['name'] == 'LowScore'

@pytest.mark.django_db
def test_admin_update_workload_and_status():
    admin = User.objects.create_user(username='admin_update', password='pass', role='admin')
    user = User.objects.create_user(username='user_update', password='pass')
    req = RequirementRequest.objects.create(name='UpdateReq', summary='Sum', region='china', requirement_type='bug', impacted_users='<100', submitter=user)
    
    client = APIClient()
    client.force_authenticate(user=admin)
    
    response = client.patch(f'/api/admin/requests/{req.id}/', {'workload': 'small', 'status': 'confirmed'}, format='json')
    assert response.status_code == 200
    assert response.data['workload'] == 'small'
    assert response.data['status'] == 'confirmed'
    assert response.data['priority_score'] is not None

@pytest.mark.django_db
def test_admin_field_level_restrictions():
    admin = User.objects.create_user(username='admin_restrict', password='pass', role='admin')
    user = User.objects.create_user(username='user_restrict', password='pass')
    req = RequirementRequest.objects.create(
        name='OriginalName', summary='Sum', region='china', 
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
