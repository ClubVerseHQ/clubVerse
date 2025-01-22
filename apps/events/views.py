from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, F, ExpressionWrapper, FloatField
from django.db.models.functions import Now
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Event, EventReaction, EventComment, EventMedia
import json

class EventsListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.annotate(
            score=ExpressionWrapper(
                (F('reactions') + F('comments') * 2 + F('shares') * 3) /
                (1 + (Now() - F('created_at')) / 3600),
                output_field=FloatField()
            )
        ).select_related('club').prefetch_related(
            'event_reactions__user',  # Prefetch reactions and related user profiles
            'event_comments',                  # Prefetch comments for count
            'media'                            # Prefetch media files
        ).order_by('-score')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events_data = []
        
        for event in context['events']:
            events_data.append({
                'id': event.id,
                'title': event.name,
                'description': event.description,
                'date': event.date.isoformat(),
                'time': event.date.time().isoformat(),
                'location': event.location,
                'club': {
                    'id': event.club.id,
                    'name': event.club.name,
                    'image': event.club.image.url,
                },
                'reactions': [
                    {
                        'user': {
                            'id': r.user.id,
                            'name': r.user.get_full_name(),
                            'avatar': r.user.profile_picture.url if r.user.profile_picture else 
                                    f"https://ui-avatars.com/api/?name={r.user.get_full_name()}&background=random"
                        },
                        'reaction': r.reaction
                    } for r in event.event_reactions.all()
                ],
                'comments': event.event_comments.count(),
                'shares': event.shares,
                'created_at': event.created_at.isoformat(),
                'share_link': event.share_link,
                'media': [{'url': media.file.url} for media in event.media.all()],
                'score': event.score,
                'is_participating': self.request.user in event.participants.all(),
            })

        # Serialize and add to context
        context['events'] = json.dumps(events_data)
        return context

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reactions'] = self.object.event_reactions.all()
        context['comments'] = self.object.event_comments.filter(parent=None)
        return context

class EventReactionView(LoginRequiredMixin, View):
    def post(self, request, event_id):
        try:
            event = get_object_or_404(Event, id=event_id)
            data = json.loads(request.body)
            reaction = data.get('reaction')
            
            # Get or create the reaction
            event_reaction, created = EventReaction.objects.get_or_create(
                user=request.user,
                event=event,
                defaults={'reaction': reaction}
            )
            
            # If not created, update the existing reaction
            if not created:
                if reaction is None:
                    event_reaction.delete()
                else:
                    event_reaction.reaction = reaction
                    event_reaction.save()
            
            # Get updated reactions
            reactions = [
                {
                    'user': {
                        'id': r.user.id,
                        'name': r.user.get_full_name(),
                        'avatar': r.user.profile_picture.url if hasattr(r.user, 'profile_picture') and r.user.profile_picture else
                                f"https://ui-avatars.com/api/?name={r.user.get_full_name()}&background=random"
                    },
                    'reaction': r.reaction
                }
                for r in event.event_reactions.select_related('user').all()
            ]
            
            return JsonResponse({'reactions': reactions})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class EventReactorsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        reactors = [
            {
                'id': r.user.id, 
                'name': r.user.get_full_name(), 
                'avatar': r.user.profile_picture.url or f"https://ui-avatars.com/api/?name={r.user.get_full_name()}&background=random",
                'reaction': r.reaction
            }
            for r in event.event_reactions.all()
        ]
        return JsonResponse({'reactors': reactors})

@method_decorator(require_POST, name='dispatch')
class EventShareView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        event.shares = F('shares') + 1
        event.save()
        
        return JsonResponse({
            'status': 'success',
            'share_link': f"/events/share/{event.share_link}/",
        })



@method_decorator(require_POST, name='dispatch')
class EventCommentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if parent_id:
            parent = get_object_or_404(EventComment, id=parent_id)
            comment = EventComment.objects.create(
                event=event,
                user=request.user,
                content=content,
                parent=parent
            )
        else:
            comment = EventComment.objects.create(
                event=event,
                user=request.user,
                content=content
            )
        
        event.comments = event.event_comments.count()
        event.save()
        
        return JsonResponse({
            'status': 'success',
            'comment_id': comment.id,
            'user': request.user.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
        })

@method_decorator(require_POST, name='dispatch')
class EventParticipateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        
        # Check if event date has passed
        if event.date < timezone.now():
            return JsonResponse({
                'status': 'error',
                'message': 'Event has already ended'
            }, status=400)

        if request.user in event.participants.all():
            event.participants.remove(request.user)
            status = 'removed'
            message = 'You are no longer participating in this event'
        else:
            event.participants.add(request.user)
            status = 'added'
            message = 'You are now participating in this event'

        return JsonResponse({
            'status': status,
            'message': message,
            'participant_count': event.participants.count(),
            'is_participating': status == 'added',
            'event_id': event.id,
            'participants': [
                {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'avatar': user.profile_picture.url if hasattr(user, 'profile_picture') and user.profile_picture else None
                } for user in event.participants.all()[:5]  # Get first 5 participants
            ]
        })