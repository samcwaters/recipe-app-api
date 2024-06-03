"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
	"""Serializer for recipies"""

	class Meta:
		model = Recipe
		fields = ['id', 'title', 'time_minutes', 'price', 'link']
		read_only_fields = ['id']

# wwe are extending RecipeSerializer base class for this serializer
class RecipeDetailSerializer(RecipeSerializer):
	"""Serializer for recipe detail view."""

	class Meta(RecipeSerializer.Meta):
		fields = RecipeSerializer.Meta.fields + ['description']