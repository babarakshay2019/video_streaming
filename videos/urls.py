from django.urls import path, include
from rest_framework.routers import DefaultRouter

from videos.views import RegisterAPI, LoginAPI, VideoViewSet, video_stream, index

router = DefaultRouter()
router.register('videos', VideoViewSet, basename='video')

urlpatterns = [
    path('', index, name='index'),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/stream/<int:video_id>/', video_stream, name='video_stream'),
    path('api/', include(router.urls)),
]
