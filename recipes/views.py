from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Recipe, Category, Review , Favorite
from .forms import RecipeForm, ReviewForm
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator


def is_chef(user):
    return hasattr(user, 'profile') and user.profile.role == 'chef'

def landing_page(request):
    return render(request, 'landing.html')


@login_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    # Recherche par titre
    search = request.GET.get('search', '')
    if search:
        recipes = recipes.filter(title__icontains=search)

    # Filtre par catégorie
    category_id = request.GET.get('category', '')
    if category_id:
        recipes = recipes.filter(category__id=category_id)

    # Filtre par note minimale
    min_rating = request.GET.get('min_rating', '')
    if min_rating:
        # Filtrer manuellement car average_rating est une méthode Python
        recipe_ids = [r.id for r in recipes if r.average_rating() and r.average_rating() >= float(min_rating)]
        recipes = recipes.filter(id__in=recipe_ids)

        # Pagination — 6 recettes par page
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'recipes/recipe_list.html', {
        'recipes': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'min_rating': min_rating,
    })

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    reviews = recipe.reviews.all()
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'reviews': reviews,
        'review_form': ReviewForm(),
    })

@user_passes_test(is_chef)
def recipe_add(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            return redirect('recipes:recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def recipe_edit(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if recipe.created_by != request.user or not is_chef(request.user):
        return HttpResponseForbidden("Tu n'as pas la permission de modifier cette recette.")
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipes:recipe_detail', id=id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def recipe_delete(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if recipe.created_by == request.user and is_chef(request.user):
        recipe.delete()
        return redirect('recipes:recipe_list')
    else:
        return HttpResponseForbidden("Tu n'as pas la permission de supprimer cette recette.")

@login_required
def recipe_review(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.recipe = recipe
            review.user = request.user
            review.save()
            return redirect('recipes:recipe_detail', id=id)
    return redirect('recipes:recipe_detail', id=id)



@login_required
def toggle_favorite(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    if not created:
        # Déjà en favori -> on supprime
        favorite.delete()
    return redirect('recipes:recipe_detail', id=id)

@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    return render(request, 'recipes/my_favorites.html', {'favorites': favorites})