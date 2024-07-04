
from rest_framework.serializers import ModelSerializer

from .models import Event, Ticket

class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

        read_only_fields = ["slug", "created_by"]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data["created_by"] = user
        return super().create(validated_data)