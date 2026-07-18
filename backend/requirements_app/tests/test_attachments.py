import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from requirements_app.models import CustomUser

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = CustomUser.objects.create_user(username='testuser', password='password', role='user')
    return user

@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client

def get_base_payload():
    return {
        'name': 'Test Requirement',
        'summary': 'Test Summary',
        'country': 'China',
        'requirement_type': 'bug',
        'impacted_users': '<100',
    }

def create_file(name, size_bytes):
    content = b'x' * size_bytes
    return SimpleUploadedFile(name, content, content_type='application/octet-stream')

@pytest.mark.django_db
class TestAttachmentUpload:
    def test_successful_upload(self, authenticated_client, tmp_path, settings):
        settings.MEDIA_ROOT = tmp_path
        payload = get_base_payload()
        file1 = create_file('doc1.pdf', 1024)
        file2 = create_file('img1.jpg', 1024)
        
        payload['attachments'] = [file1, file2]
        
        response = authenticated_client.post('/api/requests/', payload, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data['attachments_list']) == 2

    def test_reject_more_than_3_files(self, authenticated_client, tmp_path, settings):
        settings.MEDIA_ROOT = tmp_path
        payload = get_base_payload()
        payload['attachments'] = [
            create_file('f1.pdf', 100),
            create_file('f2.pdf', 100),
            create_file('f3.pdf', 100),
            create_file('f4.pdf', 100),
        ]
        response = authenticated_client.post('/api/requests/', payload, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'attachments' in response.data

    def test_reject_total_size_over_10mb(self, authenticated_client, tmp_path, settings):
        settings.MEDIA_ROOT = tmp_path
        payload = get_base_payload()
        # 6MB each, total 12MB > 10MB
        payload['attachments'] = [
            create_file('large1.pdf', 6 * 1024 * 1024),
            create_file('large2.pdf', 6 * 1024 * 1024),
        ]
        response = authenticated_client.post('/api/requests/', payload, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'attachments' in response.data

    def test_reject_invalid_extension(self, authenticated_client, tmp_path, settings):
        settings.MEDIA_ROOT = tmp_path
        payload = get_base_payload()
        payload['attachments'] = [create_file('malware.exe', 1024)]
        response = authenticated_client.post('/api/requests/', payload, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'attachments' in response.data
