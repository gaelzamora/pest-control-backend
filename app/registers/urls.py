from django.urls import path
from .views import PestRegisterCreateViewSet, GetRegistersViewSet, GetRegisterDetailView, LastSevenDaysRegistersAPIView,TechnicianRegistersAPIView

urlpatterns = [
    path('pest-register/', PestRegisterCreateViewSet.as_view(), name='pest-register'),
    path('get-registers/', GetRegistersViewSet.as_view(), name='get-registers'),
    path('get-register/<int:pk>/', GetRegisterDetailView.as_view(), name='get-register'),
    path('get-last-seven-days-registers/', LastSevenDaysRegistersAPIView.as_view(), name='get-register'),
    path('get-technician-registers/', TechnicianRegistersAPIView.as_view(), name='get-technician-registers'),
]
