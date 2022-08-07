from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('swap.urls')),
    path('chat/', include('chatroom.urls')),
    path('react/', TemplateView.as_view(template_name="index.html"))
]
