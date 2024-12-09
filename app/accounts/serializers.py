from django.contrib.auth import (
    get_user_model
)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers
from django.db.models import Count
from django.contrib.auth import get_user_model
from core.models import Rating, Register, WorkRequest, User

class UserSerializer(serializers.ModelSerializer):
    registers_count = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name', 'company',
            'branch', 'image', 'is_creator', 'is_technique', 'is_active', 
            'is_staff', 'managers', 'registers_count', 'average_rating'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'is_technique': {'read_only': True}
        }
        

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user

        if 'managers' in attrs:
            if not user.is_authenticated:
                raise serializers.ValidationError("Authentication is required to assign managers.")
        
            if not user.is_creator:
                raise serializers.ValidationError("Only creators can assign managers.")

        return attrs

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        managers_data = validated_data.pop('managers', [])
        user = get_user_model().objects.create_user(**validated_data)
        is_technique = validated_data.get('is_technique', False)

        if is_technique:
            user.is_technique=True
            user.save()

        for manager in managers_data:
            user.assign_manager(manager)
        
        return user
    
    def update(self, instance, validated_data):
        """Update and return a user with an encrypted password if provided."""
        managers_data = validated_data.pop('managers', None)
        password = validated_data.pop('password', None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        if managers_data is not None:
            user.managers.clear()
            for manager in managers_data:
                user.assign_manager(manager)
        
        return user

    def get_registers_count(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user is None or not user.is_authenticated:
            return 0

        if user.is_creator:
            total_count = Register.objects.filter(owner__in=obj.managers.all()).count()
            return total_count

        return Register.objects.filter(owner=obj).count()

class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to User"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['image']


class RatingSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.get_full_name", read_only=True)
    technician_name = serializers.CharField(source="technician.get_full_name", read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'technician', 'creator', 'rating', 'comment', 'created', 'creator_name', 'technician_name']
        read_only_fields = ['creator', 'created']

class WorkRequestSerializer(serializers.ModelSerializer):
    technician = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_technique=True))
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkRequest
        fields = ['id', 'owner', 'technician', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        owner = self.context['request'].user
        validated_data['owner'] = owner

        return WorkRequest.objects.create(**validated_data)

    def validate_status(self, value):
        if value not in ['send', 'submitted', 'working']:
            raise serializers.ValidationError("Invalid status.")
        return value


class TechnicianStatusSerializer(serializers.ModelSerializer):
    technician_id = serializers.SerializerMethodField()
    technician_name = serializers.SerializerMethodField()
    technician_email = serializers.SerializerMethodField()
    status = serializers.CharField()

    class Meta:
        model = WorkRequest
        fields = ['technician_id', 'technician_name', 'technician_email', 'status']

    def get_technician_id(self, obj):
        return obj.technician.id

    def get_technician_name(self, obj):
        return f"{obj.technician.first_name} {obj.technician.last_name}"
    
    def get_technician_email(self, obj):
        return obj.technician.email
    
class WorkRequestSerializer(serializers.ModelSerializer):
    owner_image = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkRequest
        fields = ['id', 'owner_name', 'owner_email', 'status', 'owner_image', 'updated_at']

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    def get_owner_email(self, obj):
        return obj.owner.email
    
    def get_owner_image(self, obj):
        if obj.owner.image:
            return obj.owner.image.url
        return None
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name 
        token['last_name'] = user.first_name 
        token['is_staff'] = user.is_staff
        token['branch'] = user.branch
        token['is_creator'] = user.is_creator
        token['is_technique'] = user.is_technique
        token['image'] = str(user.image)
        token['id'] = user.id
        token['managers'] = [manager.id for manager in user.managers.all()]

        return token