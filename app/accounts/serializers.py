from django.contrib.auth import (
    get_user_model
)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    # Creamos un campo 'managers' para el serializer
    managers = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), many=True, required=False
    )

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'company', 'branch', 'image', 'is_creator', 'is_active', 'is_staff', 'managers']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def validate(self, attrs):
        user = self.context.get('request').user
        if not user.is_creator and 'managers' in attrs:
            raise serializers.ValidationError('Only creators can assign managers.')
        return attrs

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        managers_data = validated_data.pop('managers', [])
        user = get_user_model().objects.create_user(**validated_data)

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
    
class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to User"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['image']

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
        token['image'] = str(user.image)
        token['id'] = user.id
        token['managers'] = [manager.id for manager in user.managers.all()]

        return token