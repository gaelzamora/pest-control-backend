from rest_framework import serializers
from core.models import Register

class RegisterSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Register
        fields = ['id', 'pest_name', 'created', 'owner', 'image']
        read_only_fields = ['id', 'created', 'owner']

    def create(self, validated_data):
        user = self.context['request'].user
        return Register.objects.create(owner=user, **validated_data)
    
class RegisterImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to Register"""

    class Meta(RegisterSerializer.Meta):
        fields = RegisterSerializer.Meta.fields + ['image']