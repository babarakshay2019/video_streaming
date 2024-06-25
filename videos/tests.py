from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from django.urls import reverse
from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status
from django.test import RequestFactory, TestCase

from videos.views import video_stream
from videos.models import Video
from concurrent.futures import ThreadPoolExecutor
from django.views.decorators.clickjacking import xframe_options_exempt

# Define a ThreadPoolExecutor with a maximum number of threads
executor = ThreadPoolExecutor(max_workers=5)


class UserTests(APITestCase):
    def test_register(self):
        response = self.client.post('/api/register/', {'username': 'testuser', 'email': 'user@example.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        User.objects.create_user(username='testuser', email='user@example.com', password='testpass')
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class VideoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_video(self):
        response = self.client.post('/api/videos/', {'name': 'Test Video', 'url': 'http://example.com/video.mp4'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_videos(self):
        Video.objects.create(user=self.user, name='Test Video', url='http://example.com/video.mp4')
        response = self.client.get('/api/videos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_video(self):
        video = Video.objects.create(user=self.user, name='Test Video', url='http://example.com/video.mp4')
        response = self.client.patch(f'/api/videos/{video.id}/', {'name': 'Updated Video'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_video(self):
        video = Video.objects.create(user=self.user, name='Test Video', url='http://example.com/video.mp4')
        response = self.client.delete(f'/api/videos/{video.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class VideoStreamTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.video = Video.objects.create(user=self.user, name='Test Video', url='http://example.com/video.mp4')

    def test_video_stream_success(self):
        # Create a request object
        url = reverse('video_stream', kwargs={'video_id': self.video.id})
        request = self.factory.get(url)
        request.user = self.user

        # Call the view function
        response = video_stream(request, self.video.id)

        self.assertIsInstance(response, StreamingHttpResponse)

video_stream = xframe_options_exempt(video_stream)
