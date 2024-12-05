from django.urls import path
from .views import PestRegisterCreateViewSet, GetRegistersViewSet, GetRegisterDetailView

urlpatterns = [
    path('pest-register/', PestRegisterCreateViewSet.as_view(), name='pest-register'),
    path('get-registers/', GetRegistersViewSet.as_view(), name='get-registers'),
    path('get-register/<int:pk>/', GetRegisterDetailView.as_view(), name='get-register'),
]
