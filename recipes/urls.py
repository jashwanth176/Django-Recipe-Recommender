from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('edit/<int:id>/', views.edit_recipe, name='edit_recipe'),
    path('delete/<int:id>/', views.delete_recipe, name='delete_recipe'),
    path('detail/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='recipes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('rate/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),
    path('browse-recipes/', views.browse_recipes, name='browse_recipes'),
    path('diet-plan/', views.diet_plan, name='diet_plan'),
]