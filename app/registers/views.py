'''
Views for registers.
'''
from core.models import Register
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class PestRegisterCreateViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        pest_name = request.data.get('pest_name')
        image = request.data.get('image')

        if not pest_name:
            raise ValidationError({'pest_name': 'This field is required.'})
        
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