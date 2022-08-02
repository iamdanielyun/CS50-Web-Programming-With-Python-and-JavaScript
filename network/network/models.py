from statistics import mode
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self')
    following = models.ManyToManyField('self')

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": [user.username for user in self.followers.all()],
            "following": [user.username for user in self.following.all()]
        }

class Post(models.Model):
    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)  
    likes = models.ManyToManyField('User')

    def serialize(self):
        return {
            "id": self.id,
            "creator": self.creator.username,
            "content": self.content,
            "date": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": [user.username for user in self.likes.all()]
        }
   




    
