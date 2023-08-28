from django.db import models
from django.contrib.auth.models import AbstractUser


# extending the Abstract User model in the core app to include email attribute
class User(AbstractUser):
    email = models.EmailField(unique=True)
