from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.id,
            "username" : self.user.username,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes 
        }


class Following(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, to_field="id", default=None, related_name="followers")
    following = models.ForeignKey("User", on_delete=models.CASCADE, to_field="id", default=None, related_name="following")

    def __str__(self):
        return f"User:{self.follower.id} follows: {self.following.id}"



