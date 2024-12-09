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
import datetime
from django.db.models.functions import TruncDate
from django.db.models import Count

class PestRegisterCreateViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        pest_name = request.data.get('pest_name')
        image = request.data.get('image')

        if not pest_name:
            raise ValidationError({'pest_name': 'This field is required.'})

        ten_seconds_ago = now() - timedelta(seconds=10)
        recent_register = Register.objects.filter(owner=user, created__gte=ten_seconds_ago).exists()

        if recent_register:
            return Response(
                {"message": "You can only register a pest every 10 seconds."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
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
        
class LastSevenDaysRegistersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = datetime.datetime.today()
        last_seven_days = today - timedelta(days=7)

        if user.is_creator:
            data = (
                Register.objects.filter(owner__in=user.managers.all(), created__gte=last_seven_days)
                .annotate(date=TruncDate('created'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )
        elif user.is_technique:
            data = (
                Register.objects.filter(owner__in=user.managed_by.all(), created__gte=last_seven_days)
                .annotate(date=TruncDate('created'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )
        else:
            data = (
                Register.objects.filter(owner=user, created__gte=last_seven_days)
                .annotate(date=TruncDate('created'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

        return Response(data)

class TechnicianRegistersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_technique:
            return Response([])  # Solo los técnicos pueden acceder

        today = datetime.datetime.today()
        last_seven_days = today - timedelta(days=7)

        # Registros asociados a los dueños gestionados por los managers del técnico
        managed_owners = user.managed_by.all()
        manager_registers = (
            Register.objects.filter(
                owner__in=managed_owners,
                created__gte=last_seven_days
            )
            .annotate(date=TruncDate('created'))
            .values('date', 'owner')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # Registros asociados directamente al técnico (mediante solicitudes de trabajo)
        work_requests_owners = user.received_requests.filter(status='working').values_list('owner', flat=True)
        technician_registers = (
            Register.objects.filter(
                owner__in=work_requests_owners,
                created__gte=last_seven_days
            )
            .annotate(date=TruncDate('created'))
            .values('date', 'owner')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # Combinar datos
        combined_data = list(manager_registers) + list(technician_registers)

        for entry in combined_data:
            entry['user_id'] = entry['owner']

        return Response(combined_data)