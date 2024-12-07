from django.urls import path
from . import views

urlpatterns = [
    path('', views.shopping_list, name='shopping_list'),
    path('add/<int:recipe_id>/', views.add_to_shopping_list, name='add_to_shopping_list'),
    path('remove/<int:item_id>/', views.remove_from_shopping_list, name='remove_from_shopping_list'),
]
