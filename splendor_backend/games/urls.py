# games/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'games', views.GameViewSet, basename='game')
# 可以添加其他ViewSet，如PlayerViewSet等

urlpatterns = [
    path('', include(router.urls)),
]