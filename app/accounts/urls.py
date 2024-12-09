from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from rest_framework.routers import DefaultRouter
from .views import WorkRequestViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register(r'work-requests', WorkRequestViewSet, basename='workrequest')

urlpatterns = [
    # Control user
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('user-info/', views.UserDetailView.as_view(), name='user-info'),
    path('login/', views.LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('user-update/', views.UserUpdateView.as_view(), name='user-update'),

    # Control Managers
    path('create-manager/', views.ControlManagerViewSet.as_view(), name='create-manager'),
    path('get-manager/<int:pk>/', views.ControlManagerViewSet.as_view(), name='get-manager'),
    path('delete-manager/<int:pk>/', views.ControlManagerViewSet.as_view(), name='delete-manager'),
    path('get-managers/', views.GetManagersView.as_view(), name='get-managers'),
    path('search-manager/', views.SearchManagerViewSet.as_view(), name='search-manager'),

    # Techniques
    path('get-technicians/', views.GetTechniciansAPIView.as_view(), name='get-techniques'),

    # States
    path('send-request/', views.SendWorkRequestView.as_view(), name='send-request'),
    path('update-request-status/<int:pk>/', views.UpdateWorkRequestStatusView.as_view(), name='update_work_request_status'),
    path('technician-status/', views.OwnerTechniciansStatusView.as_view(), name='technician-status'),
    path('', include(router.urls))
]
