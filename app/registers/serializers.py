from rest_framework import serializers
from core.models import Register, Image

class RegisterSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Register
        fields = ['id', 'pest_name', 'created', 'owner', 'images']
        read_only_fields = ['id', 'created', 'owner']

    def create(self, validated_data):
        user = self.context['request'].user
        return Register.objects.create(owner=user, **validated_data)
    
class ImageSerializer(serializers.ModelSerializer):
    register = serializers.PrimaryKeyRelatedField(queryset=Register.objects.all())

    class Meta:
        model = Image
        fields = ['id', 'register', 'image']
        read_only_fields = ['id']

    def validate_register(self, value):
        user = self.context['request'].user
        if not user.registers.filter(id=value.id).exists():
            raise serializers.ValidationError("You can only add images to your own registers.")
        
        return value