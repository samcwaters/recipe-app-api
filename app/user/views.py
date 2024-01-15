"""
Views fro the user API
"""
from rest_framework import generics

from user.serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    """Create a news user in the system"""
    serializer_class = UserSerializer

