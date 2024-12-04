from django.urls import path
from .views import PestRegisterCreateViewSet

urlpatterns = [
    path('pest-register/', PestRegisterCreateViewSet.as_view(), name='pest-register')
]
