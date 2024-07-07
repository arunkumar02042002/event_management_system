
from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Event, Ticket, EventFeedback

from authentication.serializers import UserSerializer


class ReadOnlyModelSerializer(ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class EventSerializer(ModelSerializer):
    created_by = UserSerializer(required=False, read_only=True)
    class Meta:
        model = Event
        fields = '__all__'

        read_only_fields = ["slug", "created_by", "no_of_participants"]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data["created_by"] = user
        return super().create(validated_data)


class TicketSerializer(ReadOnlyModelSerializer):
    user = UserSerializer()
    event = EventSerializer()
    class Meta:
        model = Ticket
        fields = ['user', 'event', 'pruchase_time']
        read_only_field = ['user', 'event', 'purchase_time']


class EventFeedbackSerializer(ModelSerializer):

    class Meta:
        model = EventFeedback
        fields = '__all__'

        read_only_fields = ['user', 'event']

