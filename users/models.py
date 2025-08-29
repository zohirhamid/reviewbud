from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # extend the build-in django user model by adding phone and user account date created
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'users'
        
    def __str__(self):
        return self.username
