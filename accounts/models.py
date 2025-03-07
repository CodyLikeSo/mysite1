from django.db import models
from django.contrib.auth.models import User

class MyObject(models.Model):
    name = models.CharField(max_length=25)
    tag = models.CharField(max_length=25)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username if self.owner else 'Anonymous'})"

class Room(models.Model):
    name = models.CharField(max_length=25)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class UserRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','room')