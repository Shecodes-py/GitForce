from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from rest_framework import status
from rest_framework import generics 
from .serializers import CustomUserSerializer 

# Create your views here.

class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer  

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = {
            "id": user.id,
            "uid": user.uid,
            "full_name": user.full_name,
            "email": user.email,
            "username": user.username,
            # "phone": getattr(user, 'phone', None),
            "farm_location": user.farm_location,
            # "location": getattr(user, 'location', None),
        }
        return Response(data, status=status.HTTP_200_OK)