from django.db import models
from django.conf import settings

# Create your models here.

class DietaryPreference(models.Model):
    name = models.CharField(max_length=100)

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)  # Add this line
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)  # Add this line


    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey('ingredients.Ingredient', on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

class CookingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date_cooked = models.DateTimeField(auto_now_add=True)

class ShoppingListItem(models.Model):
    ingredient = models.CharField(max_length=200)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ingredient
