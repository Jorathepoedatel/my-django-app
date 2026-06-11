from django.contrib.auth.models import User
from django.db import models

def user_avatar_path(instance: "Profile", filename):
    return f"users/user_{instance.user.id}/avatars/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True)