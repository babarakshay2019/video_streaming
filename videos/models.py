from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    """
    Model representing a video uploaded by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the video name.
        """
        return self.name
