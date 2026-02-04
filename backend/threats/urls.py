from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThreatLogViewSet, BlockedIPViewSet

router = DefaultRouter()
router.register(r'logs', ThreatLogViewSet)
router.register(r'blocked-ips', BlockedIPViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
