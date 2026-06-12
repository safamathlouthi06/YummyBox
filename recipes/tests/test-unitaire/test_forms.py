import pytest
from recipes.forms import RecipeForm
from recipes.models import Category

@pytest.mark.django_db
def test_recipe_form_valid():
    cat = Category.objects.create(name="Pâtes")
    form = RecipeForm(data={
        "title": "Pâtes Carbonara",
        "description": "Crémeuses et rapides",
        "category": cat.id
    })
    assert form.is_valid() is True

@pytest.mark.django_db
def test_recipe_form_invalid():
    form = RecipeForm(data={
        "title": "",
        "description": "Test",
        "category": ""
    })
    assert form.is_valid() is False
