from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('add/', views.recipe_add, name='recipe_add'),
    path('<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('<int:id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('<int:id>/delete/', views.recipe_delete, name='recipe_delete'),
    path('<int:id>/review/', views.recipe_review, name='recipe_review'),

        path('<int:id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.my_favorites, name='my_favorites'),
]