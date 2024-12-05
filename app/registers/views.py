'''
Views for registers.
'''
from core.models import Register
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import RegisterSerializer

from django.utils.timezone import now
from datetime import timedelta
from rest_framework.exceptions import ValidationError

class PestRegisterCreateViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        pest_name = request.data.get('pest_name')
        image = request.data.get('image')

        if not pest_name:
            raise ValidationError({'pest_name': 'This field is required.'})

        # Comprobar si el usuario ya ha registrado una plaga en los últimos 10 segundos
        ten_seconds_ago = now() - timedelta(seconds=10)
        recent_register = Register.objects.filter(owner=user, created__gte=ten_seconds_ago).exists()

        if recent_register:
            return Response(
                {"message": "You can only register a pest every 10 seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Crear el registro
        register = Register.objects.create(
            pest_name=pest_name,
            owner=user,
            image=image
        )

        return Response(
            {
                "message": "Pest register created successfully",
                "data": {
                    "id": register.id,
                    "pest_name": register.pest_name,
                    "owner": user.get_full_name(),
                    "created": register.created,
                },
            },
            status=status.HTTP_201_CREATED
        )


class GetRegistersViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Obtener todos los registros del usuario autenticado.
        """
        user = request.user
        registers = Register.objects.filter(owner=user)
        serializer = RegisterSerializer(registers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetRegisterDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Obtener un registro específico basado en su PK.
        """
        try:
            register = Register.objects.get(pk=pk, owner=request.user)
            serializer = RegisterSerializer(register)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Register.DoesNotExist:
            return Response({'detail': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)