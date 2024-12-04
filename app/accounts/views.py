"""
Views for users.
"""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import generics
from . import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from core.models import User

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = serializers.UserSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)
    
class UploadImageUserViewSet(APIView):
    """Upload image to unique user."""
    permission_classes = [SessionAuthentication]

    def get_queryset(self, request):
        """Retrieve user information for authenticated user."""    
        return self.queryset.filter(pk=request.user.pk)
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'upload_image':
            return serializers.UserImageSerializer
        
        return self.serializer_class
    
class ControlManagerViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.is_creator:
            return Response(
                {"detail": "You do not have permission to create managers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        required_fields = ['email', 'first_name', 'last_name', 'branch', 'password']

        for field in required_fields:
            if field not in data:
                return Response(
                    {"detail": f"'{field}' is required."},   
                    status=status.HTTP_400_BAD_REQUEST
                )
    
        try:
            manager = user.create_manager(
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                branch=data['branch'],
                password=data['password']
            )
        except Exception as e:
            return Response(
                {"detail": f"An error ocurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Manager created successfully.",
                "manager": {
                    "id": manager.id,
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "branch": manager.branch,
                    "last_name": manager.last_name,
                },
            },
            status=status.HTTP_201_CREATED
        )
    
    def get(self, request, pk):
        user = request.user

        if not user.is_creator:
            return Response(
                {"detail": "You do not have permission to create managers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        manager = user.managers.filter(pk=pk).first()

        if not manager:
            return Response(
                {"detail": "Manager not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:     
            return Response({
                "Detail": f"Get manager ID: {manager.id} successfully",
                "manager": {
                    "id": manager.id,
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "branch": manager.branch
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def delete(self, request, pk):
        user = request.user

        if not user.is_creator:
            return Response(
                {"detail": "You do not have permission to create managers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        manager = user.managers.filter(pk=pk).first()

        if not manager:
            return Response(
                {"detail": "Manager not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            manager.delete()
            return Response(
                {"detail": f"Manager with ID {pk} deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"An error ocurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class GetManagersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_creator:
            return Response(
                {"detail": "You do not have permission to view managers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        managers = user.managers.all()

        if not managers:
            return Response(
                {"detail": "No managers found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        manager_serializer = UserSerializer(managers, many=True)

        return Response({
            "detail": "Managers retrieved successfully.",
            "managers": manager_serializer.data
        }, status=status.HTTP_200_OK)

class SearchManagerViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')

        user = request.user
        if not user.is_creator:
            return Response(
                {"detail": "You do not have permission to search managers."},
                status=status.HTTP_403_FORBIDDEN
            )

        if query == '':
            managers = user.managers.all()
            serializer = UserSerializer(managers, many=True)
            return Response(
                {'managers': serializer.data},
                status=status.HTTP_200_OK
            )

        managers = user.managers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        serializer = UserSerializer(managers, many=True)
        return Response(
            {'managers': serializer.data},
            status=status.HTTP_200_OK
        )