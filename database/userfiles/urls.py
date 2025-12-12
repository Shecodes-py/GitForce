from django.urls import path, include
from .views import UserProfileView

urlpatterns = [
    path('sendinfo/<int:pk>/', UserProfileView.as_view(), name='send_info'),  
    path('api-auth/', include('rest_framework.urls'))
]