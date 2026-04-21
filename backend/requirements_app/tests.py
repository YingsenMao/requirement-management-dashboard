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
    # regulatory(50) + >1000(40) + >1M(40) + 4 materials(20) + small(30) = 180
    assert req.priority_score == 180

@pytest.mark.django_db
def test_priority_score_medium_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', region='china', requirement_type='bug',
        impacted_users='<100', revenue_impact=None, supplementary_materials=[],
        workload='medium', submitter=user
    )
    # bug(10) + <100(10) + None(0) + 0 materials(0) + medium(15) = 35
    assert req.priority_score == 35

@pytest.mark.django_db
def test_priority_score_large_workload():
    user = User.objects.create_user(username='test_user', password='pass')
    req = RequirementRequest.objects.create(
        name='Test', summary='Test', region='china', requirement_type='optimization',
        impacted_users='100-500', revenue_impact='50k-300k', supplementary_materials=['a'],
        workload='large', submitter=user
    )
    # optimization(0) + 100-500(20) + 50k-300k(20) + 1 material(5) + large(0) = 45
    assert req.priority_score == 45

@pytest.mark.django_db
def test_user_isolation():
    user1 = User.objects.create_user(username='user1', password='pass')
    user2 = User.objects.create_user(username='user2', password='pass')
    
    RequirementRequest.objects.create(name='Req1', summary='Sum1', region='china', requirement_type='bug', impacted_users='<100', submitter=user1)
    RequirementRequest.objects.create(name='Req2', summary='Sum2', region='china', requirement_type='bug', impacted_users='<100', submitter=user2)
    
    client = APIClient()
    client.force_authenticate(user=user1)
    
    response = client.get('/api/requests/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Req1'

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
    assert len(response.data) == 2
    # Check sorting: HighScore should be first
    assert response.data[0]['name'] == 'HighScore'
    assert response.data[1]['name'] == 'LowScore'

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
