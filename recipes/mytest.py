from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category, Recipe, Review

User = get_user_model()

class RecipeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Dessert")
        self.recipe = Recipe.objects.create(
            title="Gâteau au chocolat",
            description="Délicieux gâteau au chocolat",
            category=self.category,
            created_by=self.user
        )

    def test_create_category_and_recipe(self):
        self.assertEqual(self.category.name, "Dessert")
        self.assertEqual(self.recipe.title, "Gâteau au chocolat")
        self.assertEqual(self.recipe.category.name, "Dessert")
        self.assertEqual(self.recipe.created_by.username, "testuser")

    def test_average_rating_no_reviews(self):
        self.assertIsNone(self.recipe.average_rating())

    def test_average_rating_with_reviews(self):
        Review.objects.create(recipe=self.recipe, user=self.user, rating=4)
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        Review.objects.create(recipe=self.recipe, user=other_user, rating=2)

        avg = self.recipe.average_rating()
        self.assertEqual(avg, 3.0)  # (4+2)/2 = 3.0

