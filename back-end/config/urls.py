from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('swap.urls')),
    path('chat/', include('chatroom.urls')),
    path('', TemplateView.as_view(template_name="index.html")),
    path("api/token/", TokenObtainPairView.as_view(), name="TokenObtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="TokenRefresh"),
]
