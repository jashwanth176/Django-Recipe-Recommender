import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  # Add this import
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Recipe, ShoppingListItem
from .forms import RecipeForm
import requests
from django.conf import settings

# Create your views here.


def home(request):
    if request.user.is_authenticated:
        recipes = Recipe.objects.all()
        login_form = None
    else:
        recipes = []
        login_form = AuthenticationForm()
    return render(request, 'recipes/home.html', {'recipes': recipes, 'login_form': login_form})

def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RecipeForm()
    return render(request, 'recipes/add_recipe.html', {'form': form})

def edit_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/edit_recipe.html', {'form': form})

def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        recipe.delete()
        return redirect('home')
    return render(request, 'recipes/delete_recipe.html', {'recipe': recipe})

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

@login_required
@require_POST
def rate_recipe(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        data = json.loads(request.body)
        rating = int(data.get('rating', 0))
        if 1 <= rating <= 5:
            recipe.rating = rating
            recipe.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid rating'})
    except Recipe.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Recipe not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def landing(request):
    return render(request, 'recipes/landing.html')

def browse_recipes(request):
    """
    View to fetch and display recipes from an external API.
    """
    api_key = settings.RECIPE_API_KEY  # Ensure you have set this in settings.py
    query = request.GET.get('query', 'chicken')  # Default search term
    url = f'https://api.spoonacular.com/recipes/complexSearch?query={query}&number=10&apiKey={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        recipes = data.get('results', [])
    except requests.exceptions.RequestException as e:
        recipes = []
        # You might want to log the error or handle it accordingly

    context = {
        'recipes': recipes,
        'query': query
    }
    return render(request, 'recipes/browse_recipes.html', context)

def diet_plan(request):
    """
    View to create and display a diet meal plan using the new meal plan API.
    """
    meal_plan = {}
    error = None

    # Get all form data
    diet = request.GET.get('diet', '')
    age = request.GET.get('age', '')
    gender = request.GET.get('gender', '')
    height = request.GET.get('height', '')
    weight = request.GET.get('weight', '')
    goal = request.GET.get('goal', '')

    # Only make API call if we have all required fields
    if all([diet, age, gender, height, weight, goal]):
        try:
            # Calculate base calories based on user input
            # Basic BMR calculation using Harris-Benedict equation
            if gender == 'male':
                bmr = 88.362 + (13.397 * float(weight)) + (4.799 * float(height)) - (5.677 * float(age))
            else:
                bmr = 447.593 + (9.247 * float(weight)) + (3.098 * float(height)) - (4.330 * float(age))

            # Adjust calories based on goal
            if goal == 'lose-weight':
                target_calories = bmr * 0.85  # 15% deficit
            elif goal == 'gain-weight':
                target_calories = bmr * 1.15  # 15% surplus
            else:
                target_calories = bmr

            # Create meal templates based on diet type
            diet_templates = {
                'balanced': {
                    "breakfast": {
                        "recipeName": "Balanced Breakfast Bowl",
                        "difficulty": "intermediate",
                        "preparationTime": 20,
                        "servings": 1,
                        "ingredients": [
                            {"name": "Quinoa", "unit": "grams", "amount": 50},
                            {"name": "Eggs", "unit": "pieces", "amount": 2},
                            {"name": "Avocado", "unit": "pieces", "amount": 0.5},
                            {"name": "Mixed Vegetables", "unit": "grams", "amount": 100}
                        ],
                        "instructions": ["Cook quinoa", "Prepare eggs", "Slice avocado", "Combine all ingredients"],
                        "macros": {
                            "calories": {"amount": round(target_calories * 0.3), "unit": "kcal"},
                            "proteins": {"amount": 20, "unit": "grams"},
                            "carbs": {"amount": 30, "unit": "grams"},
                            "fats": {"amount": 15, "unit": "grams"}
                        }
                    }
                },
                'high-protein': {
                    "breakfast": {
                        "recipeName": "High Protein Breakfast",
                        "difficulty": "intermediate",
                        "preparationTime": 25,
                        "servings": 1,
                        "ingredients": [
                            {"name": "Egg Whites", "unit": "pieces", "amount": 4},
                            {"name": "Chicken Breast", "unit": "grams", "amount": 100},
                            {"name": "Oats", "unit": "grams", "amount": 40}
                        ],
                        "instructions": ["Cook egg whites", "Grill chicken", "Prepare oats"],
                        "macros": {
                            "calories": {"amount": round(target_calories * 0.3), "unit": "kcal"},
                            "proteins": {"amount": 35, "unit": "grams"},
                            "carbs": {"amount": 20, "unit": "grams"},
                            "fats": {"amount": 8, "unit": "grams"}
                        }
                    }
                },
                'low-carb': {
                    "breakfast": {
                        "recipeName": "Low Carb Breakfast",
                        "difficulty": "easy",
                        "preparationTime": 15,
                        "servings": 1,
                        "ingredients": [
                            {"name": "Eggs", "unit": "pieces", "amount": 3},
                            {"name": "Bacon", "unit": "slices", "amount": 2},
                            {"name": "Spinach", "unit": "grams", "amount": 100}
                        ],
                        "instructions": ["Cook eggs", "Crisp bacon", "Sauté spinach"],
                        "macros": {
                            "calories": {"amount": round(target_calories * 0.3), "unit": "kcal"},
                            "proteins": {"amount": 25, "unit": "grams"},
                            "carbs": {"amount": 5, "unit": "grams"},
                            "fats": {"amount": 20, "unit": "grams"}
                        }
                    }
                },
                'vegetarian': {
                    "breakfast": {
                        "recipeName": "Vegetarian Breakfast",
                        "difficulty": "easy",
                        "preparationTime": 20,
                        "servings": 1,
                        "ingredients": [
                            {"name": "Tofu", "unit": "grams", "amount": 150},
                            {"name": "Spinach", "unit": "grams", "amount": 100},
                            {"name": "Sweet Potato", "unit": "grams", "amount": 150}
                        ],
                        "instructions": ["Scramble tofu", "Steam sweet potato", "Sauté spinach"],
                        "macros": {
                            "calories": {"amount": round(target_calories * 0.3), "unit": "kcal"},
                            "proteins": {"amount": 15, "unit": "grams"},
                            "carbs": {"amount": 25, "unit": "grams"},
                            "fats": {"amount": 12, "unit": "grams"}
                        }
                    }
                }
            }

            # Get the template for the selected diet (default to balanced if not found)
            selected_template = diet_templates.get(diet, diet_templates['balanced'])

            # Create a week's worth of meals with variations
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days:
                breakfast = selected_template['breakfast'].copy()
                lunch = selected_template['breakfast'].copy()
                dinner = selected_template['breakfast'].copy()
                
                # Modify recipe names for lunch and dinner
                lunch['recipeName'] = lunch['recipeName'].replace('Breakfast', 'Lunch')
                dinner['recipeName'] = dinner['recipeName'].replace('Breakfast', 'Dinner')
                
                meal_plan[day] = {
                    'Breakfast': breakfast,
                    'Lunch': lunch,
                    'Dinner': dinner
                }

        except Exception as e:
            error = f"Failed to generate meal plan: {str(e)}"
            meal_plan = {}

    context = {
        'meal_plan': meal_plan,
        'diet': diet,
        'age': age,
        'gender': gender,
        'height': height,
        'weight': weight,
        'goal': goal,
        'error': error
    }
    
    return render(request, 'recipes/diet_plan.html', context)