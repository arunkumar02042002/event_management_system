from rest_framework import serializers

from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "role",
            "is_active",
            "is_staff",
            "is_superuser"
        ]  
    
        read_only_fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "role",
            "is_active",
            "is_staff",
            "is_superuser"
        ]