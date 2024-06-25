import cv2
from django.contrib.auth import login, authenticate
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, viewsets, serializers, filters, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.clickjacking import xframe_options_exempt

from videos.models import Video
from videos.serializers import UserSerializer, RegisterSerializer, VideoSerializer
from concurrent.futures import ThreadPoolExecutor

# Define a ThreadPoolExecutor with a maximum number of threads
executor = ThreadPoolExecutor(max_workers=5)

    
class RegisterAPI(generics.GenericAPIView):
    """
    API endpoint for user registration.

    Requires a valid username, email, and password.
    Returns the registered user details and authentication token upon successful registration.
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for user registration.

        Returns:
            Response: JSON response containing the user details and authentication token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user) 
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key  # Use token.key to get the token string
        })

class LoginAPI(generics.GenericAPIView):
    """
    API endpoint for user login.

    Requires a valid username and password.
    Returns the authenticated user details and authentication token upon successful login.
    """
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for user login.

        Returns:
            Response: JSON response containing the authenticated user details and authentication token.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token.key
            })
        else:
            return Response({
                "error": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on videos.

    Requires authentication with a valid token.
    Supports search functionality on video names.
    """
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        """
        Returns the queryset filtered to include only videos belonging to the authenticated user.

        Returns:
            queryset: Queryset of videos belonging to the authenticated user.
        """
        return Video.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Performs creation of a new video instance, associating it with the authenticated user.

        Args:
            serializer (VideoSerializer): Serializer instance containing video data.
        """
        serializer.save(user=self.request.user)


@xframe_options_exempt
def video_stream(request, video_id):
    """
    Streams video frames from a specified video ID.

    Requires authentication with a valid token and permission to access the video.

    Args:
        request (HttpRequest): Django HTTP request object.
        video_id (int): ID of the video to stream.

    Returns:
        StreamingHttpResponse: Streaming response containing video frames encoded as JPEG.
        HttpResponseNotFound: If the video with the given ID is not found or user does not have permission.
        HttpResponseServerError: If there is an error while streaming the video.
    """
    try:
        user = request.user
        video = get_object_or_404(Video, id=video_id, user=user)

        def generate(cap):
            """
            Generator function that streams video frames.

            Args:
                cap (cv2.VideoCapture): VideoCapture object initialized with the video URL.

            Yields:
                bytes: JPEG encoded frames of the video.
            """
            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    _, jpeg = cv2.imencode('.jpg', frame)
                    frame = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            finally:
                cap.release()  # Release the VideoCapture object

        # Create the VideoCapture object outside of the generate function
        cap = cv2.VideoCapture(video.url)

        # Submit the generate function to the ThreadPoolExecutor, passing the cap object as an argument
        future = executor.submit(generate, cap)

        return StreamingHttpResponse(future.result(), content_type='multipart/x-mixed-replace; boundary=frame')

    except Video.DoesNotExist:
        return HttpResponseNotFound("Video not found or you do not have permission to access it.")
    except Exception as e:
        return HttpResponseServerError(f"Error streaming video: {str(e)}")


def index(request):
    """
    Renders the index page.

    If the user is authenticated, it retrieves or generates a token for API access.
    If not authenticated, displays a message with a login link.

    Args:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Rendered HTML response for the index page.
    """
    if request.user.is_authenticated:
        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            token = None  # Handle case where token does not exist for user
        return render(request, 'videos/index.html', context={"token": token.key if token else None})
    else:
        return HttpResponse(
            '<h1>Refresh after Login in Browser to watch videos</h1>'
            '<a href="http://127.0.0.1:8000/api/login/">Login here</a>'
        )
