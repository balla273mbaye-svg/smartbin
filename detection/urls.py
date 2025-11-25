from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tmp/<str:filename>/', views.serve_tmp_file, name='serve_tmp_file'),
]
