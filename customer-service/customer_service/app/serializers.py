from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Customer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.get('password', '')
        if password:
            validated_data['password'] = make_password(password)
        return super().create(validated_data)