"""
API Tests for Hostel Management System

Tests for REST API endpoints, authentication, and permissions
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.hostel.models import Block, Room, RoomAllocation, RoomBill
from apps.mess.models import MessBill, MessMenu, MessRegistration
from apps.students.models import Student


@pytest.fixture
def api_client():
    """Create an API client"""
    return APIClient()


@pytest.fixture
def admin_user():
    """Create an admin user"""
    return User.objects.create_user(username='admin', password='admin123', is_staff=True, is_superuser=True)


@pytest.fixture
def regular_user():
    """Create a regular user"""
    return User.objects.create_user(username='user', password='user123')


@pytest.fixture
def get_tokens(admin_user):
    """Get JWT tokens for a user"""
    def _get_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    return _get_tokens


@pytest.fixture
def test_student(admin_user):
    """Create a test student"""
    return Student.objects.create(
        user=admin_user,
        enrollment_no="ENC001",
        name="John Doe",
        email="john@example.com",
        phone="9876543210",
        gender="M",
        date_of_birth="2000-01-15",
        blood_group="O+",
        course="BTech",
        year=2,
        branch="Computer Science",
        address="123 Main St",
        city="Mumbai",
        state="Maharashtra",
        parent_name="Jane Doe",
        parent_phone="9876543211",
    )


@pytest.fixture
def test_block():
    """Create a test block"""
    return Block.objects.create(
        name="Block A",
        block_type="Boys",
        floors=3,
        warden_name="Mr. Kumar",
        warden_phone="9876543210",
    )


@pytest.mark.django_db
class TestStudentAPI:
    """Test Student API endpoints"""

    def test_list_students(self, api_client, admin_user, get_tokens, test_student):
        """Test listing students"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get('/api/students/')
        assert response.status_code == 200
        assert 'results' in response.data or isinstance(response.data, list)

    def test_get_student_detail(self, api_client, admin_user, get_tokens, test_student):
        """Test getting student details"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get(f'/api/students/{test_student.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'John Doe'

    def test_student_bill_summary(self, api_client, admin_user, get_tokens, test_student):
        """Test student bill summary endpoint"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get(f'/api/students/{test_student.id}/bill-summary/')
        assert response.status_code == 200
        assert 'student' in response.data
        assert 'mess_bills' in response.data


@pytest.mark.django_db
class TestBlockAPI:
    """Test Block API endpoints"""

    def test_list_blocks(self, api_client, admin_user, get_tokens, test_block):
        """Test listing blocks"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get('/api/blocks/')
        assert response.status_code == 200

    def test_get_block_detail(self, api_client, admin_user, get_tokens, test_block):
        """Test getting block details"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get(f'/api/blocks/{test_block.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Block A'


@pytest.mark.django_db
class TestAuthentication:
    """Test API authentication"""

    def test_unauthenticated_request(self, api_client):
        """Test that unauthenticated requests are rejected"""
        response = api_client.get('/api/students/')
        assert response.status_code == 401

    def test_get_token(self, api_client, admin_user):
        """Test obtaining JWT tokens"""
        response = api_client.post('/api/token/', {
            'username': 'admin',
            'password': 'admin123',
        })
        # This will fail if token endpoint isn't configured
        # We'll add it in the next step


@pytest.mark.django_db
class TestBillAPI:
    """Test Bill API endpoints"""

    def test_list_mess_bills(self, api_client, admin_user, get_tokens):
        """Test listing mess bills"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get('/api/mess-bills/')
        assert response.status_code == 200

    def test_list_room_bills(self, api_client, admin_user, get_tokens):
        """Test listing room bills"""
        tokens = get_tokens(admin_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = api_client.get('/api/room-bills/')
        assert response.status_code == 200
