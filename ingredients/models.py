from django.db import models
from django.conf import settings

# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(max_length=100)

class UserIngredient(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)
