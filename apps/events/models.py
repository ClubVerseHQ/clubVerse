from django.db import models
from apps.clubs.models import Club
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils import timezone
User = get_user_model()


class EventVisibility(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    club = models.ForeignKey(Club, related_name="events", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    visibility = models.ForeignKey(EventVisibility, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="events", blank=True)
    reactions = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    share_link = models.CharField(max_length=20, unique=True, blank=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.share_link:
            self.share_link = get_random_string(length=20)
        super().save(*args, **kwargs)
    
    @property
    def interaction_score(self):
        return self.reactions + (self.comments * 2) + (self.shares * 3)
    
    @property
    def ranking_score(self):
        time_decay = (timezone.now() - self.created_at).total_seconds() / 3600  # Hours since creation
        return self.interaction_score / (1 + time_decay)
    
# Event pictures, videos, files...one event can have multiple media
class EventMedia(models.Model):
    event = models.ForeignKey(Event, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="events/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for {self.event.name}"
    # save those files of events in media/events/{event_id}/
    


# class ReactionType(models.Model):
#     name = models.CharField(max_length=50, unique=True)  # e.g., "like", "dislike", "love"
#     icon = models.CharField(max_length=100, blank=True)  # Optional icon representation (e.g., emojis)
    
#     def __str__(self):
#         return self.name
    
class EventReaction(models.Model):
    REACTION_CHOICES = [
        ('LIKE', '👍'),
        ('LOVE', '❤️'),
        ('HAHA', '😂'),
        ('WOW', '😮'),
        ('SAD', '😢'),
        ('ANGRY', '😠'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_reactions')
    reaction = models.CharField(max_length=5, choices=REACTION_CHOICES, default='LIKE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.get_reaction_display()} - {self.event.name}"

class EventComment(models.Model):
    event = models.ForeignKey(Event, related_name="event_comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="event_comments", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )  # For nested comments
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.name}"

