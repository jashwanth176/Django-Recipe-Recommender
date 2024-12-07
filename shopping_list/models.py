from django.db import models
from django.conf import settings

# Create your models here.

class ShoppingListItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredient = models.CharField(max_length=200)
    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingredient} (from {self.recipe.title})"
