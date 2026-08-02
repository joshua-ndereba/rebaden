"""
API URL Configuration for SIEM Application
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AssetViewSet, LogSourceViewSet, LogUploadViewSet,
    EventViewSet, AlertViewSet, InvestigationViewSet,
    UserProfileViewSet
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'log-sources', LogSourceViewSet, basename='log-source')
router.register(r'log-upload', LogUploadViewSet, basename='log-upload')
router.register(r'events', EventViewSet, basename='event')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'investigations', InvestigationViewSet, basename='investigation')
router.register(r'profile', UserProfileViewSet, basename='profile')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
