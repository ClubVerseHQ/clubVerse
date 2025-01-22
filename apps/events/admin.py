from django.contrib import admin
from apps.events.models import Event, EventVisibility, EventReaction, EventComment #, ReactionType

admin.site.register(Event)
admin.site.register(EventVisibility)
admin.site.register(EventReaction)
#admin.site.register(ReactionType)
admin.site.register(EventComment)

# Register your models here.
