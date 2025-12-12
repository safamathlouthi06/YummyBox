import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from recipes.models import Category, Recipe, Review

User = get_user_model()

@pytest.mark.django_db
def test_category_str_and_creation():
    cat = Category.objects.create(name="Desserts")
    assert str(cat) == "Desserts"
    assert Category.objects.count() == 1

@pytest.mark.django_db
def test_recipe_creation_and_str(user_factory):
    user = user_factory(username="chef")
    cat = Category.objects.create(name="Soupes")
    recipe = Recipe.objects.create(
        title="Harira",
        description="Bonne soupe",
        category=cat,
        created_by=user
    )
    assert str(recipe) == "Harira"
    assert recipe.category == cat
    assert recipe.created_by == user

@pytest.mark.django_db
def test_review_creation_and_rating_validation(user_factory):
    user = user_factory(username="reviewer")
    cat = Category.objects.create(name="Desserts")
    recipe = Recipe.objects.create(title="Tiramisu", description="Classique", category=cat, created_by=user)

    # Rating correct
    review = Review(recipe=recipe, user=user, rating=4, comment="Top")
    review.full_clean()  # Pas d'erreur
    review.save()
    assert review.rating == 4

    # Rating invalide (hors bornes)
    review_bad = Review(recipe=recipe, user=user, rating=7)
    with pytest.raises(ValidationError):
        review_bad.full_clean()

@pytest.mark.django_db
def test_average_rating(user_factory):
    user1 = user_factory(username="user1")
    user2 = user_factory(username="user2")
    cat = Category.objects.create(name="Desserts")
    recipe = Recipe.objects.create(title="Tiramisu", description="Classique", category=cat, created_by=user1)

    Review.objects.create(recipe=recipe, user=user1, rating=4)
    Review.objects.create(recipe=recipe, user=user2, rating=5)

    avg = recipe.average_rating()
    assert avg == 4.5

@pytest.mark.django_db
def test_review_unique_together(user_factory):
    user = user_factory(username="unique_user")
    cat = Category.objects.create(name="Desserts")
    recipe = Recipe.objects.create(title="Tiramisu", description="Classique", category=cat, created_by=user)

    Review.objects.create(recipe=recipe, user=user, rating=3)

    with pytest.raises(Exception):
        # Deuxième review du même user sur la même recette -> erreur unique_together
        Review.objects.create(recipe=recipe, user=user, rating=4)


# Fixture pour créer un user rapidement
@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return create_user
