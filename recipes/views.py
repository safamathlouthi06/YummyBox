from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Recipe, Category, Review
from .forms import RecipeForm, ReviewForm
from django.http import HttpResponseForbidden


# Vérifie si l'utilisateur est chef
def is_chef(user):
    return hasattr(user, 'profile') and user.profile.role == 'chef'


def landing_page(request):
   
    return render(request, 'landing.html')


@login_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'categories': categories
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
        # Refuser l’accès avec un 403, ça évite les redirections confuses
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
    # Si pas POST ou form invalide, on retourne quand même vers la page de détail
    return redirect('recipes:recipe_detail', id=id)
