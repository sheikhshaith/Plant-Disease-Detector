from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# -------------------------------
# URL ROUTING CONFIGURATION
# -------------------------------
urlpatterns = [
    path('admin/', admin.site.urls),                      # Django admin interface
    path('api/', include('userauths.urls')),              # User authentication and registration APIs
    path('model/', include('core.urls')),                 # Core model-related APIs (e.g., prediction, history)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
