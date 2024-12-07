from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    SKILL_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    cooking_skill = models.CharField(max_length=20, choices=SKILL_LEVELS, default='beginner')
    dietary_preferences = models.ManyToManyField('recipes.DietaryPreference', blank=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any additional profile fields here
