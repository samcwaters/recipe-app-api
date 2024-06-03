"""
Views for the recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #We could use this viewset as is but we want to filter the response to recipes
    #related to authenticated user, we do this by overriding the getqueryset method
    def get_queryset(self):
        """Retrieve recipe for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

        #Because we know they are going to be authenticated we can retreive the user in the request

    def get_serializer_class(self):
        """Return the serializer class for request."""
        #if the action is list (GET on root of API) then we the default serializer else we use the detail serializer
        if self.action == 'list':
            #return a reference to a class (not an object)
            return serializers.RecipeSerializer

        return self.serializer_class