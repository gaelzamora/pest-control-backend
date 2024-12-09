"""
Views for users.
"""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import generics
from rest_framework.generics import UpdateAPIView
from . import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RatingSerializer, TechnicianStatusSerializer, UserSerializer, WorkRequestSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from core.models import Rating, User, WorkRequest
from rest_framework.decorators import action
from rest_framework import viewsets

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = serializers.UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """Set is_technique to True when creating a technician."""
        serializer.save(is_technique=True)

    def create(self, request, *args, **kwargs):
        """Override create to provide custom response."""
        response = super().create(request, *args, **kwargs)
        response.data = {
            "message": "Technician created successfully.",
            "user": response.data
        }
        return response

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user, context={'request': request})
        return Response(user_serializer.data)
    
class UserUpdateView(UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
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
            serializer = UserSerializer(managers, context={'request': request}, many=True)
            return Response(
                {'managers': serializer.data},
                status=status.HTTP_200_OK
            )

        managers = user.managers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        serializer = UserSerializer(managers, context={'request': request}, many=True)
        return Response(
            {'managers': serializer.data},
            status=status.HTTP_200_OK
        )
    
class TechnicianRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, technician_id):
        user = request.user
        if not user.is_creator:
            return Response({"detail": "Only creators can give ratings."}, status=status.HTTP_403_FORBIDDEN)

        try:
            technician = User.objects.get(id=technician_id, is_technique=True)
        except User.DoesNotExist:
            return Response({"detail": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = RatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(creator=user, technician=technician)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, technician_id):
        try:
            technician = User.objects.get(id=technician_id, is_technique=True)
        except User.DoesNotExist:
            return Response({"detail": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)

        ratings = Rating.objects.filter(technician=technician)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)
    
class GetTechniciansAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')
        user = request.user

        if not user.is_creator:
            return Response(
                {"detail": "You do not have permission to search technicians"},
                status=status.HTTP_403_FORBIDDEN
            )

        if query == '':
            technicians = User.objects.filter(is_active=True, is_technique=True)

            serializer = UserSerializer(technicians, many=True)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        technicians = User.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

        serializer = UserSerializer(technicians, many=True)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
class OwnerTechniciansStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owner = request.user

        if not owner.is_creator:
            return Response({"detail": "Only creators can view this information."}, status=403)

        work_requests = WorkRequest.objects.filter(owner=owner).select_related('technician')

        serializer = TechnicianStatusSerializer(work_requests, many=True)
        return Response(serializer.data)

class SendWorkRequestView(generics.CreateAPIView):
    """Owner sends a work request to a technician."""
    serializer_class = WorkRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_creator:
            raise serializers.ValidationError("Only creators can send requests.")
        
        technician_id = self.request.data.get('technician')

        if not technician_id:
            raise serializers.ValidationError({"technician": "A technician must be provided."})

        try:
            technician = User.objects.get(id=technician_id, is_technique=True)
        except User.DoesNotExist:
            raise serializers.ValidationError({"technician": "The selected technician does not exist or is not valid."})


        serializer.save(owner=self.request.user, technician_id=technician.pk)

class WorkRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_send_requests_for_technician(self, request):
        technician = request.user

        send_requests = WorkRequest.objects.filter(technician=technician, status='submitted')

        serializer = WorkRequestSerializer(send_requests, many=True)
        return Response(serializer.data)

class UpdateWorkRequestStatusView(generics.UpdateAPIView):
    queryset = WorkRequest.objects.all()
    serializer_class = WorkRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        work_request = self.get_object()

        if work_request.technician != request.user:
            return Response({"detail": "You are not authorized to update this request."}, status=status.HTTP_403_FORBIDDEN)
        
        work_request.status = 'working'
        work_request.save()

        serializer = self.get_serializer(work_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
