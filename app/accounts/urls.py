from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Control user
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('user-info/', views.UserDetailView.as_view(), name='user-info'),
    path('login/', views.LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),

    # Control Managers
    path('create-manager/', views.ControlManagerViewSet.as_view(), name='create-manager'),
    path('get-manager/<int:pk>/', views.ControlManagerViewSet.as_view(), name='get-manager'),
    path('delete-manager/<int:pk>/', views.ControlManagerViewSet.as_view(), name='delete-manager'),
    path('get-managers/', views.GetManagersView.as_view(), name='get-managers'),
    path('search-manager/', views.SearchManagerViewSet.as_view(), name='search-manager')
]
