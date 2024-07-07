from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta


User = get_user_model()

# Create your models here.
class Event(models.Model):

    def get_default_time():
        return timezone.now()+timedelta(days=1)

    title = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField(default=get_default_time)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_created')
    no_of_participants = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets_sold')
    pruchase_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'event_id'], name='unique_event_user'
            )
        ]

    def __str__(self) -> str:
        return f'user_{self.user_id}_event_{self.event_id}'
    

class EventFeedback(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='event_feedbacks')
    event = models.ForeignKey(to=Event, on_delete=models.CASCADE, related_name='feedbacks')
    feedback = models.TextField()

    def __str__(self) -> str:
        return f'user_{self.user_id}_event_{self.event_id}'
