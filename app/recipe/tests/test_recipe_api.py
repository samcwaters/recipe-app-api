"""
Tests for recipe API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
	"""Create and return a recipe detail URL."""
	return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe details"""
        #creates the recipe and assign it to a user that we use for authentication
        recipe = create_recipe(user=self.user)

        #we create the deatil ur; using the ID of that recipe
        url = detail_url(recipe.id)
        #we run a get to call the url
        res = self.client.get(url)

        #pass recipe to the serializer
        serializer = RecipeDetailSerializer(recipe)
        #Check the result of the client is the same as the result of the serializer
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test create a recipe."""
        #define a payload
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        #HTTP post to recipe url
        res = self.client.post(RECIPES_URL, payload) #/api/recipes/recipe

        #Check for 201 (success code when creating a new object)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        #Request a specific id (id returned from the post response)
        recipe = Recipe.objects.get(id=res.data['id'])
        #Iterate through the payload and check
        for k, v in payload.items():
            #we're using the getattr to get the object matching the name of k rather then the value
            self.assertEqual(getattr(recipe, k), v)
        #Check the user that assigned to the API matches the user we're authenticated with
        self.assertEqual(recipe.user, self.user)

