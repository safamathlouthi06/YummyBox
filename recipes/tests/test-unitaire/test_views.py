import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from recipes.models import Recipe, Category, Review
from recipes.forms import RecipeForm


@pytest.mark.django_db
def test_landing_page(client):
    url = reverse('recipes:landing')
    response = client.get(url)
    assert response.status_code == 200
    assert 'landing.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_recipe_list_requires_login(client):
    url = reverse('recipes:recipe_list')
    response = client.get(url)
    # Non connecté -> redirige vers login
    assert response.status_code == 302
    assert response.url.startswith('/accounts/login/')


@pytest.mark.django_db
def test_recipe_list_logged_in(client):
    user = User.objects.create_user(username='user', password='1234')
    client.login(username='user', password='1234')

    cat = Category.objects.create(name='Desserts')
    Recipe.objects.create(title='Tarte', description='Délicieuse', category=cat, created_by=user)

    url = reverse('recipes:recipe_list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'recipes/recipe_list.html' in (t.name for t in response.templates)
    assert b'Tarte' in response.content


@pytest.mark.django_db
def test_recipe_detail_view(client):
    user = User.objects.create_user(username='user', password='1234')
    cat = Category.objects.create(name='Desserts')
    recipe = Recipe.objects.create(title='Tarte', description='Délicieuse', category=cat, created_by=user)

    url = reverse('recipes:recipe_detail', args=[recipe.id])
    response = client.get(url)
    assert response.status_code == 200
    assert 'recipes/recipe_detail.html' in (t.name for t in response.templates)
    assert b'Tarte' in response.content


@pytest.mark.django_db
def test_recipe_add_only_chef(client):
    # user non chef -> interdit
    user = User.objects.create_user(username='user', password='1234')
    client.login(username='user', password='1234')

    url = reverse('recipes:recipe_add')
    response = client.get(url)
    # Redirige ou Forbidden selon ton middleware, ici user_passes_test devrait renvoyer 302
    assert response.status_code == 302 or response.status_code == 403

    # user chef
    chef = User.objects.create_user(username='chef', password='1234')
    # Simuler profile.role = 'chef' (à adapter selon ta vraie structure)
    chef.profile.role = 'chef'
    chef.profile.save()

    client.login(username='chef', password='1234')
    response = client.get(url)
    assert response.status_code == 200
    assert 'recipes/recipe_form.html' in (t.name for t in response.templates)

    # POST valide
    cat = Category.objects.create(name='Desserts')
    form_data = {
        'title': 'Soupe',
        'description': 'Très bonne',
        'category': cat.id,
    }
    response = client.post(url, data=form_data)
    assert response.status_code == 302
    assert response.url == reverse('recipes:recipe_list')


@pytest.mark.django_db
def test_recipe_edit_permission(client):
    user = User.objects.create_user(username='user', password='1234')
    chef = User.objects.create_user(username='chef', password='1234')
    chef.profile.role = 'chef'
    chef.profile.save()

    cat = Category.objects.create(name='Desserts')
    recipe = Recipe.objects.create(title='Gâteau', description='Délicieux', category=cat, created_by=chef)

    url = reverse('recipes:recipe_edit', args=[recipe.id])

    # Non connecté -> redirige login
    response = client.get(url)
    assert response.status_code == 302

    # Connecté mais pas créateur ou pas chef -> 403
    client.login(username='user', password='1234')
    response = client.get(url)
    assert response.status_code == 403

    # Connecté créateur chef -> accès ok
    client.login(username='chef', password='1234')
    response = client.get(url)
    assert response.status_code == 200

    # POST modifie la recette
    form_data = {
        'title': 'Gâteau modifié',
        'description': 'Encore meilleur',
        'category': cat.id,
    }
    response = client.post(url, data=form_data)
    assert response.status_code == 302
    recipe.refresh_from_db()
    assert recipe.title == 'Gâteau modifié'


@pytest.mark.django_db
def test_recipe_delete_permission(client):
    user = User.objects.create_user(username='user', password='1234')
    chef = User.objects.create_user(username='chef', password='1234')
    chef.profile.role = 'chef'
    chef.profile.save()

    cat = Category.objects.create(name='Desserts')
    recipe = Recipe.objects.create(title='Tarte', description='Délicieuse', category=cat, created_by=chef)

    url = reverse('recipes:recipe_delete', args=[recipe.id])

    # Pas connecté -> redirection login
    response = client.post(url)
    assert response.status_code == 302

    # Connecté mais pas créateur chef -> 403
    client.login(username='user', password='1234')
    response = client.post(url)
    assert response.status_code == 403

    # Connecté créateur chef -> suppression ok
    client.login(username='chef', password='1234')
    response = client.post(url)
    assert response.status_code == 302
    with pytest.raises(Recipe.DoesNotExist):
        Recipe.objects.get(id=recipe.id)


@pytest.mark.django_db
def test_recipe_review_post(client):
    user = User.objects.create_user(username='user', password='1234')
    cat = Category.objects.create(name='Desserts')
    recipe = Recipe.objects.create(title='Tarte', description='Délicieuse', category=cat, created_by=user)

    url = reverse('recipes:recipe_review', args=[recipe.id])
    form_data = {
        'rating': 5,
        'comment': 'Super recette!',
    }
    client.login(username='user', password='1234')
    response = client.post(url, data=form_data)
    assert response.status_code == 302
    assert response.url == reverse('recipes:recipe_detail', args=[recipe.id])
    assert Review.objects.filter(recipe=recipe, user=user).exists()
