import pytest
from django.urls import reverse
from recipes.models import Recipe, Category


#-----------------------------------------------------------------------------
#---Test d’intégration pour ajout de recette (vue recipe_add)
#-----------------------------------------------------------------------------

@pytest.mark.django_db
def test_integration_add_recipe(client, django_user_model):
    # Création user chef
    user = django_user_model.objects.create_user(username='chef', password='pass123')
    user.profile.role = 'chef'
    user.profile.save()

    # Login
    client.login(username='chef', password='pass123')

    # Création catégorie
    category = Category.objects.create(name="Entrées")

    # Données recette
    data = {
        'title': 'Soupe de légumes',
        'description': 'Une soupe parfaite pour l’hiver',
        'category': category.id,
    }

    url = reverse('recipes:recipe_add')
    response = client.post(url, data)

    # Check redirection vers la liste
    assert response.status_code == 302
    assert response.url == reverse('recipes:recipe_list')

    # Vérifier recette en DB
    recipe = Recipe.objects.get(title='Soupe de légumes')
    assert recipe.description == 'Une soupe parfaite pour l’hiver'
    assert recipe.created_by == user
    assert recipe.category == category




#-----------------------------------------------------------------------------
#---Test d’intégration pour ajout d’une review (vue recipe_review)
#-----------------------------------------------------------------------------

@pytest.mark.django_db
def test_integration_add_review(client, django_user_model):
    # Création user simple
    user = django_user_model.objects.create_user(username='user1', password='pass123')

    # Login
    client.login(username='user1', password='pass123')

    # Setup recette
    category = Category.objects.create(name="Desserts")
    recipe = Recipe.objects.create(title='Tarte', description='Tarte au citron', category=category, created_by=user)

    # Données review
    data = {
        'rating': 4,
        'comment': 'Très bon goût!',
    }

    url = reverse('recipes:recipe_review', args=[recipe.id])
    response = client.post(url, data)

    # Check redirection vers détail recette
    assert response.status_code == 302
    assert response.url == reverse('recipes:recipe_detail', args=[recipe.id])

    # Vérifier review en DB
    review = recipe.reviews.get(user=user)
    assert review.rating == 4
    assert review.comment == 'Très bon goût!'




#-----------------------------------------------------------------------------
#---Test d’intégration pour édition d’une recette (vue recipe_edit)
#-----------------------------------------------------------------------------

@pytest.mark.django_db
def test_integration_edit_recipe(client, django_user_model):
    # Création chef
    user = django_user_model.objects.create_user(username='chef', password='pass123')
    user.profile.role = 'chef'
    user.profile.save()

    # Login
    client.login(username='chef', password='pass123')

    # Setup recette
    category = Category.objects.create(name="Plats")
    recipe = Recipe.objects.create(title='Salade', description='Fraîche et bonne', category=category, created_by=user)

    # Nouvelle description
    data = {
        'title': 'Salade',
        'description': 'Salade fraîche avec vinaigrette maison',
        'category': category.id,
    }

    url = reverse('recipes:recipe_edit', args=[recipe.id])
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse('recipes:recipe_detail', args=[recipe.id])

    recipe.refresh_from_db()
    assert recipe.description == 'Salade fraîche avec vinaigrette maison'





    
