from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=20, unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True) 
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname']

    def __str__(self):
        return self.nickname
