from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/threats/', include('threats.urls')),
    path('api/', include('apps.core.urls')),  # Assuming core app has urls
    path('accounts/', include('django.contrib.auth.urls')),  # Auth URLs
    path('', include('apps.core.urls')),  # Include the URLs from the core app
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)