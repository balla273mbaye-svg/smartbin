from detection import views
"""
URL configuration for smartbin project.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
]

# 🔹 Servir les médias (pour afficher les images uploadées et résultat)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
