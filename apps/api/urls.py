"""
API URL routes for Hostel Management System

Uses DRF routers for automatic CRUD endpoint generation
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .viewsets import (
    BlockViewSet,
    MessBillViewSet,
    MessMenuViewSet,
    MessRegistrationViewSet,
    RoomAllocationViewSet,
    RoomBillViewSet,
    RoomViewSet,
    StudentViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'blocks', BlockViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'allocations', RoomAllocationViewSet)
router.register(r'room-bills', RoomBillViewSet)
router.register(r'mess-menu', MessMenuViewSet)
router.register(r'mess-registrations', MessRegistrationViewSet)
router.register(r'mess-bills', MessBillViewSet)

# Standard routing
urlpatterns = [
    # Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # API endpoints
    path('', include(router.urls)),
]
