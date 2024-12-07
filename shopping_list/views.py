from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import ShoppingListItem
from recipes.models import Recipe
import json

# Create your views here.

@login_required
def shopping_list(request):
    items = ShoppingListItem.objects.filter(user=request.user).order_by('recipe__title', 'ingredient')
    return render(request, 'shopping_list/shopping_list.html', {'items': items})

@csrf_exempt
@require_POST
@login_required
def add_to_shopping_list(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        ingredients = recipe.ingredients.split('\n')
        for ingredient in ingredients:
            ShoppingListItem.objects.get_or_create(
                user=request.user,
                ingredient=ingredient.strip(),
                recipe=recipe
            )
        return JsonResponse({'success': True})
    except Recipe.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Recipe not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def remove_from_shopping_list(request, item_id):
    ShoppingListItem.objects.filter(id=item_id, user=request.user).delete()
    return JsonResponse({'success': True})
