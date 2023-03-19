from config import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('billing_app.api.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
