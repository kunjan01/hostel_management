from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # API Routes
    path('api/v1/', include('apps.api.urls')),
    # Web Routes
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('hostel/', include('apps.hostel.urls')),
    path('mess/', include('apps.mess.urls')),
    path('students/', include('apps.students.urls')),
    path('complaints/', include('apps.complaints.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
